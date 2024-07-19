import hashlib
import logging
import re
import time
from typing import Optional, Dict, Any, List
from uuid import uuid4

import boto3
import os
import sys
import tarfile
import shutil

import botocore
import requests
import docker
import base64
import json

from urllib.parse import urlparse
from datetime import datetime
from argh import arg
from httpx import TimeoutException
from pydantic import BaseModel, Field

from scale_egp.cli.collections import GenericCommands
from scale_egp.exceptions import EGPException
from scale_egp.sdk.enums import EmbeddingModelName
from scale_egp.sdk.models.model_enums import ModelType
from scale_egp.sdk.types import ModelTemplateRequest, ModelTemplate, ModelInstanceRequest, ModelInstance, \
    ModelDeploymentRequest, ModelDeployment, ChunkToUpload, LocalChunksSourceConfig, EmbeddingRequest, \
    CompletionRequest, ParameterBindings

LOCAL_DATA_DIR = os.path.join(os.path.expanduser("~"), ".scale-egp", "aws-setup")
CACHE_DIR = os.path.join(LOCAL_DATA_DIR, "cache")
CACHE_UNTAR_DIR = os.path.join(CACHE_DIR, "untar")


# Set up logging to just print the string to stderr
formatter = logging.Formatter('%(message)s')
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)

TEST_EMBEDDING_REQUEST = EmbeddingRequest(texts=["hello"])
TEST_COMPLETION_REQUEST = {"prompts": ["hello"]}


def debug_print(*args, **kwargs):
    logger.info(*args, **kwargs)


def error_print(*args, **kwargs):
    logger.error(*args, **kwargs)


EMBEDDING_MODEL_FINE_TUNED = "finetuned"
EMBEDDING_MODEL_OPEN_SOURCE = "opensource"


class EmbeddingConfig(BaseModel):
    embedding_model: str


class KnowledgeBaseData(BaseModel):
    embedding_config: EmbeddingConfig
    chunks: List[ChunkToUpload]


class AppConfigInput(BaseModel):
    knowledge_bases: Dict[str, KnowledgeBaseData]


class AwsVpcSetupCommands(GenericCommands):
    command_group_name = "aws-setup"
    command_group_title = "AWS VPC Setup Commands"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._egp_client_val = None
        self._s3_util_client_val = None
        self._ecr_util_client_val = None

    @property
    def _egp_client(self):
        if self._egp_client_val is None:
            self._egp_client_val = self._client_factory.get_client()
        return self._egp_client_val

    @property
    def _s3_util_client(self):
        if self._s3_util_client_val is None:
            try:
                self._s3_util_client_val = S3UtilClient(boto3.client("s3"))
            except Exception as e:
                debug_print(f"Error creating S3 client: {e}")
                debug_print("Check your AWS credentials and try again.")
                sys.exit(1)
        return self._s3_util_client_val

    @property
    def _ecr_util_client(self):
        if self._ecr_util_client_val is None:
            try:
                ecr_client = boto3.client("ecr")
            except Exception as e:
                debug_print(f"Error creating ECR client: {e}")
                debug_print("Check your AWS credentials and try again.")
                sys.exit(1)

            try:
                docker_client = docker.from_env()
            except Exception as e:
                debug_print(f"Error creating Docker client: {e}")
                debug_print("Check your Docker installation / setup (like environment variables) and try again.")
                sys.exit(1)

            ecr_url = None
            try:
                ecr_credentials = ecr_client.get_authorization_token()["authorizationData"][0]
                ecr_username = "AWS"
                ecr_password = base64.b64decode(ecr_credentials["authorizationToken"]).decode().split(":")[1]
                ecr_url = ecr_credentials["proxyEndpoint"].replace("https://", "")

                docker_client.login(username=ecr_username, password=ecr_password, registry=ecr_url, reauth=True)
            except Exception as e:
                debug_print(f"Error logging into ECR: {e}")
                debug_print("Check your AWS credentials and try again.")
                if ecr_url:
                    debug_print(f"If your credentials are expired, try running `docker logout {ecr_url}` and try again")
                sys.exit(1)

            self._ecr_util_client_val = EcrUtilClient(ecr_client, docker_client)
        return self._ecr_util_client_val

    @arg("--model-config-src-uri", required=False, help="URI pointing to the model config file (currently only supports http(s) URIs). One of src-uri or src-file must be provided")
    @arg("--model-config-src-file", required=False, help="File path for a config file. One of src-uri or src-file must be provided")
    @arg("--model-weights-src-uri", required=False, help="URI pointing to the model weights file (currently only supports http(s) URIs). Required if model weights do not exist in S3")
    @arg("--model-weights-dest-uri", help="The model weight destination S3 URI (bucket and key) (key prefix if unpacking)")
    @arg("--model-image-src-cr-uri", required=False, help="Registry / repository URI pointing to the model image. If image does not exist in ECR, one of cr-uri or tar-uri must be provided")
    @arg("--model-image-src-tar-uri", required=False, help="URI pointing to the model image tar file (currently only supports http(s) URIs). If image does not exist in ECR, one of cr-uri or tar-uri must be provided")
    @arg("--model-image-dest-uri", required=True, help="The model image destination ECR URI")
    @arg("--debug", required=False, help="Enable debug logging", default=False)
    def create_model_deployment(self, *, model_config_src_uri, model_config_src_file, model_weights_src_uri, model_weights_dest_uri, model_image_src_cr_uri, model_image_src_tar_uri, model_image_dest_uri, debug):
        """
        Requirements: AWS CLI, Docker
        Must have AWS credentials configured with permissions to S3 and ECR.

        This command creates a model deployment in the Scale EGP given a model
        configuration, model weights, and model image. Scale will provide you
        with these in the form of https URLs for the model weights and image,
        and either a JSON file or a URL for the model configuration.

        You will need to provide the installation locations of the model weights
        and image. In the default Scale EGP configuration, the model weights
        should be stored in the bucket scale-egp-<workspace>-models and the image
        should be stored in the ECR repository scale-egp-<workspace-id>-launch/inference
        or vllm based on the model type.

        Here is an example of how to use this command:

        export EGP_ENDPOINT_URL=https://api.<workspace-id>.workspace.egp.scale.com/
        export EGP_ACCOUNT_ID=<account-id>
        export EGP_API_KEY=<api-key>
        scale-egp aws-setup create-model-deployment \\
            --model-weights-src-uri "<scale-provided-model-weights-url>" \\
            --model-weights-dest-uri "s3://scale-egp-<workspace-id>-models/my-model-weights" \\
            --model-image-src-tar-uri "scale-provided-model-image-url>" \\
            --model-image-dest-uri "<aws-account-id>.dkr.ecr.us-west-2.amazonaws.com/vllm:1.0.0" \\
            --model-config-src-uri "<scale-provided-model-config-url>"

        If you already have the model weights and image in S3 and ECR, you can skip
        providing the sources. The command would then look like this:

        scale-egp aws-setup create-model-deployment \\
            --model-weights-dest-uri "s3://scale-egp-<workspace-id>-models/my-model-weights" \\
            --model-image-dest-uri "<aws-account-id>.dkr.ecr.us-west-2.amazonaws.com/vllm:1.0.0" \\
            --model-config-src-uri "<scale-provided-model-config-url>"

        The model weights and image files are cached locally to avoid repeated downloads.
        The cache is located at ~/.scale-egp/aws-setup/ and can be cleared with the command:

        scale-egp aws-setup clear-cache
        """
        if debug:
            logger.setLevel(logging.INFO)

        self._create_model_deployment_logic(model_config_src_uri, model_config_src_file, model_weights_src_uri, model_weights_dest_uri, model_image_src_cr_uri, model_image_src_tar_uri, model_image_dest_uri)

    def _create_model_deployment_logic(self, model_config_src_uri, model_config_src_file, model_weights_src_uri, model_weights_dest_uri, model_image_src_cr_uri, model_image_src_tar_uri, model_image_dest_uri):
        model_template_request, model_instance_request, model_deployment_request = self._load_model_config(model_config_src_uri, model_config_src_file)
        should_unpack_weights = model_template_request.model_type in [ModelType.COMPLETION]
        model_weights_bucket, model_weights_key = split_s3_uri(model_weights_dest_uri)

        should_install_model_weights = self._check_model_weights_options(model_weights_src_uri, model_weights_bucket, model_weights_key, should_unpack_weights)
        should_install_model_image = self._check_model_image_options(model_image_src_cr_uri, model_image_src_tar_uri, model_image_dest_uri)

        if should_install_model_weights:
            self._install_model_weights(model_weights_src_uri, model_weights_bucket, model_weights_key, should_unpack_weights)
        else:
            debug_print(f"Model weights already exist in s3://{model_weights_bucket}/{model_weights_key}")
            debug_print(f"Skipping installation of model weights.")

        if should_install_model_image:
            self._install_model_image(model_image_src_cr_uri, model_image_src_tar_uri, model_image_dest_uri)
        else:
            debug_print(f"Model image already exists in {model_image_dest_uri}")
            debug_print(f"Skipping installation of model image.")

        model_instance, model_deployment = self._deploy_model(model_weights_bucket, model_weights_key, model_image_dest_uri, model_template_request, model_instance_request, model_deployment_request)

        self._check_model_deployed(model_instance, model_deployment, model_template_request.model_type)

        debug_print("\n\n\n")
        print("Model instance ID:", model_instance.id)
        print("Model deployment ID:", model_deployment.id)

        return model_instance, model_deployment

    @arg("--os-embedding-instance-id", required=True, help="The model instance ID of the OPEN SOURCE embedding model to use (NOTE: this is the model __instance__)")
    @arg("--os-embedding-deployment-id", required=True, help="The deployment ID of the OPEN SOURCE embedding model to use (NOTE: this is the model __deployment__)")
    @arg("--ft-embedding-instance-id", required=True, help="The model instance ID of the FINE TUNED embedding model to use (NOTE: this is the model __instance__)")
    @arg("--ft-embedding-deployment-id", required=True, help="The deployment ID of the FINE TUNED embedding model to use (NOTE: this is the model __deployment__)")
    @arg("--llm-instance-id", required=True, help="The model instance ID of the LLM model to use (NOTE: this is the model __instance__)")
    @arg("--llm-deployment-id", required=True, help="The deployment ID of the LLM model to use (NOTE: this is the model __deployment__)")
    @arg("--app-data-uri", required=True, help="URI pointing to a file containing applications knowledge base data (currently only supports http(s) URIs)")
    @arg("--debug", required=False, help="Enable debug logging", default=False)
    def create_app_configs(self, *, os_embedding_instance_id, os_embedding_deployment_id, ft_embedding_instance_id, ft_embedding_deployment_id, llm_instance_id, llm_deployment_id, app_data_uri, debug):
        """
        Creates application configurations for Scale MLE developed apps,
        by creating knowledge bases and prompt generators for each app.
        Currently supports the creation of Text2SQL applications.

        The model instance and deployment IDs can be obtained by running
        the create-model-deployment subcommand, given the Scale provided
        configuration. The app data URI should point to a JSON file provided
        by Scale.
        """
        if debug:
            logger.setLevel(logging.INFO)

        self._create_app_configs_logic(
            os_embedding_instance_id,
            os_embedding_deployment_id,
            ft_embedding_instance_id,
            ft_embedding_deployment_id,
            llm_instance_id,
            llm_deployment_id,
            app_data_uri
        )

    def _create_app_configs_logic(self, os_embedding_instance_id, os_embedding_deployment_id, ft_embedding_instance_id, ft_embedding_deployment_id, llm_instance_id, llm_deployment_id, app_data_uri):

        applications = self._load_app_data_config(app_data_uri)

        env_vars = []
        for name, app_config_input in applications.items():
            ret_env_vars = self._load_knowledge_bases_and_create_app(name, app_config_input, os_embedding_deployment_id, ft_embedding_deployment_id)
            env_vars.extend(ret_env_vars)

        debug_print("\n\n\n")

        print(f"MODEL_ID={llm_instance_id}")
        print(f"MODEL_DEPLOYMENT_ID={llm_deployment_id}")
        for env_var in env_vars:
            print(env_var)

    @arg("--os-emb-model-config-src-uri", required=False,
         help="OPEN SOURCE EMBEDDING: URI pointing to the model config file (currently only supports http(s) URIs). One of src-uri or src-file must be provided")
    @arg("--os-emb-model-config-src-file", required=False,
         help="OPEN SOURCE EMBEDDING: File path for a config file. One of src-uri or src-file must be provided")
    @arg("--os-emb-model-weights-src-uri", required=False,
         help="OPEN SOURCE EMBEDDING: URI pointing to the model weights file (currently only supports http(s) URIs). Required if model weights do not exist in S3")
    @arg("--os-emb-model-weights-dest-uri",
         help="OPEN SOURCE EMBEDDING: The model weight destination S3 URI (bucket and key) (key prefix if unpacking)")
    @arg("--os-emb-model-image-src-cr-uri", required=False,
         help="OPEN SOURCE EMBEDDING: Registry / repository URI pointing to the model image. If image does not exist in ECR, one of cr-uri or tar-uri must be provided")
    @arg("--os-emb-model-image-src-tar-uri", required=False,
         help="OPEN SOURCE EMBEDDING: URI pointing to the model image tar file (currently only supports http(s) URIs). If image does not exist in ECR, one of cr-uri or tar-uri must be provided")
    @arg("--os-emb-model-image-dest-uri", required=True, help="OPEN SOURCE EMBEDDING: The model image destination ECR URI")
    @arg("--ft-emb-model-config-src-uri", required=False,
         help="FINE TUNED EMBEDDING: URI pointing to the model config file (currently only supports http(s) URIs). One of src-uri or src-file must be provided")
    @arg("--ft-emb-model-config-src-file", required=False,
         help="FINE TUNED EMBEDDING: File path for a config file. One of src-uri or src-file must be provided")
    @arg("--ft-emb-model-weights-src-uri", required=False,
         help="FINE TUNED EMBEDDING: URI pointing to the model weights file (currently only supports http(s) URIs). Required if model weights do not exist in S3")
    @arg("--ft-emb-model-weights-dest-uri",
         help="FINE TUNED EMBEDDING: The model weight destination S3 URI (bucket and key) (key prefix if unpacking)")
    @arg("--ft-emb-model-image-src-cr-uri", required=False,
         help="FINE TUNED EMBEDDING: Registry / repository URI pointing to the model image. If image does not exist in ECR, one of cr-uri or tar-uri must be provided")
    @arg("--ft-emb-model-image-src-tar-uri", required=False,
         help="FINE TUNED EMBEDDING: URI pointing to the model image tar file (currently only supports http(s) URIs). If image does not exist in ECR, one of cr-uri or tar-uri must be provided")
    @arg("--ft-emb-model-image-dest-uri", required=True,
         help="FINE TUNED EMBEDDING: The model image destination ECR URI")
    @arg("--llm-model-config-src-uri", required=False,
         help="LLM: URI pointing to the model config file (currently only supports http(s) URIs). One of src-uri or src-file must be provided")
    @arg("--llm-model-config-src-file", required=False,
         help="LLM: File path for a config file. One of src-uri or src-file must be provided")
    @arg("--llm-model-weights-src-uri", required=False,
         help="LLM: URI pointing to the model weights file (currently only supports http(s) URIs). Required if model weights do not exist in S3")
    @arg("--llm-model-weights-dest-uri",
         help="LLM: The model weight destination S3 URI (bucket and key) (key prefix if unpacking)")
    @arg("--llm-model-image-src-cr-uri", required=False,
         help="LLM: Registry / repository URI pointing to the model image. If image does not exist in ECR, one of cr-uri or tar-uri must be provided")
    @arg("--llm-model-image-src-tar-uri", required=False,
         help="LLM: URI pointing to the model image tar file (currently only supports http(s) URIs). If image does not exist in ECR, one of cr-uri or tar-uri must be provided")
    @arg("--llm-model-image-dest-uri", required=True, help="LLM: The model image destination ECR URI")
    @arg("--app-data-uri", required=True,
         help="URI pointing to a file containing applications knowledge base data (currently only supports http(s) URIs)")
    @arg("--debug", required=False, help="Enable debug logging", default=False)
    def create_models_and_app_configs(self, *,
        os_emb_model_config_src_uri,
        os_emb_model_config_src_file,
        os_emb_model_weights_src_uri,
        os_emb_model_weights_dest_uri,
        os_emb_model_image_src_cr_uri,
        os_emb_model_image_src_tar_uri,
        os_emb_model_image_dest_uri,
        ft_emb_model_config_src_uri,
        ft_emb_model_config_src_file,
        ft_emb_model_weights_src_uri,
        ft_emb_model_weights_dest_uri,
        ft_emb_model_image_src_cr_uri,
        ft_emb_model_image_src_tar_uri,
        ft_emb_model_image_dest_uri,
        llm_model_config_src_uri,
        llm_model_config_src_file,
        llm_model_weights_src_uri,
        llm_model_weights_dest_uri,
        llm_model_image_src_cr_uri,
        llm_model_image_src_tar_uri,
        llm_model_image_dest_uri,
        app_data_uri,
        debug
    ):
        if debug:
            logger.setLevel(logging.INFO)

        uris = [
            os_emb_model_config_src_uri,
            ft_emb_model_config_src_uri,
            llm_model_config_src_uri,
            app_data_uri,
            os_emb_model_weights_src_uri,
            os_emb_model_image_src_tar_uri,
            ft_emb_model_weights_src_uri,
            ft_emb_model_image_src_tar_uri,
            llm_model_weights_src_uri,
            llm_model_image_src_tar_uri,
        ]
        for uri in uris:
            if uri:
                download_uri(uri)

        os_embedding_instance, os_embedding_deployment = self._create_model_deployment_logic(
            os_emb_model_config_src_uri,
            os_emb_model_config_src_file,
            os_emb_model_weights_src_uri,
            os_emb_model_weights_dest_uri,
            os_emb_model_image_src_cr_uri,
            os_emb_model_image_src_tar_uri,
            os_emb_model_image_dest_uri,
        )

        ft_embedding_instance, ft_embedding_deployment = self._create_model_deployment_logic(
            ft_emb_model_config_src_uri,
            ft_emb_model_config_src_file,
            ft_emb_model_weights_src_uri,
            ft_emb_model_weights_dest_uri,
            ft_emb_model_image_src_cr_uri,
            ft_emb_model_image_src_tar_uri,
            ft_emb_model_image_dest_uri
        )

        llm_instance, llm_deployment = self._create_model_deployment_logic(
            llm_model_config_src_uri,
            llm_model_config_src_file,
            llm_model_weights_src_uri,
            llm_model_weights_dest_uri,
            llm_model_image_src_cr_uri,
            llm_model_image_src_tar_uri,
            llm_model_image_dest_uri
        )

        self._create_app_configs_logic(
            os_embedding_instance.id,
            os_embedding_deployment.id,
            ft_embedding_instance.id,
            ft_embedding_deployment.id,
            llm_instance.id,
            llm_deployment.id,
            app_data_uri
        )

    @arg("--debug", required=False, help="Enable debug logging", default=False)
    def clear_cache(self, *, debug=False):
        """
        This command clears the local cache of downloaded files.
        """
        if debug:
            logger.setLevel(logging.INFO)

        try:
            shutil.rmtree(LOCAL_DATA_DIR)
            print(f"Cleared local cache at {LOCAL_DATA_DIR}.")
        except Exception as e:
            error_print(f"Error clearing local cache: {e}")
            error_print("Check the directory permissions and try again.")
            sys.exit(1)


    def _parse_model_configs(self, model_config):
        model_template_config = model_config["model_template"]
        model_template_config["account_id"] = self._egp_client.account_id
        model_template_config["name"] = ""
        model_template_config["vendor_configuration"]["bundle_config"]["registry"] = ""
        model_template_config["vendor_configuration"]["bundle_config"]["image"] = ""
        model_template_config["vendor_configuration"]["bundle_config"]["tag"] = ""

        model_instance_config = model_config["model_instance"]
        model_instance_config["account_id"] = self._egp_client.account_id
        model_instance_config["name"] = ""
        model_instance_config["model_template_id"] = ""

        model_deploy_config = model_config["model_deployment"]
        model_deploy_config["account_id"] = self._egp_client.account_id
        model_deploy_config["name"] = ""

        return ModelTemplateRequest(**model_template_config), ModelInstanceRequest(**model_instance_config), ModelDeploymentRequest(**model_deploy_config)

    def _load_model_config(self, model_config_src_uri, model_config_src_file):
        if model_config_src_uri is None and model_config_src_file is None:
            error_print("Either model-config-src-uri or model-config-src-file must be provided.")
            sys.exit(1)

        if model_config_src_file is None:
            model_config_src_file = download_uri(model_config_src_uri)

        try:
            with open(model_config_src_file, "r") as f:
                model_config_contents = f.read()
            model_config = json.loads(model_config_contents)
        except Exception as e:
            error_print(f"Error reading model config from {model_config_src_file}: {e}")
            error_print("Check the model config source and try again.")
            sys.exit(1)

        try:
            return self._parse_model_configs(model_config)
        except KeyError as e:
            error_print(f"Error parsing model request from model config: missing or erroneous key {e}")
            error_print("Check the model config source is downloading correctly.")
            error_print("Reach out to Scale for further help.")
            sys.exit(1)
        except Exception as e:
            error_print(f"Error parsing model request from model config: {e}")
            error_print("Check the model config source and try again.")
            error_print("Reach out to Scale for further help.")
            sys.exit(1)

    def _check_model_weights_options(self, model_weights_src_uri, model_weights_dest_bucket, model_weights_dest_key, should_unpack):
        should_install_model_weights = True

        if should_unpack:
            if '.' in model_weights_dest_key:
                error_print("For the configured model type, the model weights should be stored in an S3 directory. Fix the destination key (remove file extension) and try again.")
                sys.exit(1)
            if self._s3_util_client.does_directory_exists(model_weights_dest_bucket, model_weights_dest_key):
                should_install_model_weights = False
        elif not should_unpack:
            if not model_weights_dest_key.endswith('.tar'):
                error_print("For the configured model type, the model weights should be stored in a tar file. Fix the destination key (add .tar extension) and try again.")
                sys.exit(1)
            if self._s3_util_client.does_file_exist(model_weights_dest_bucket, model_weights_dest_key):
                should_install_model_weights = False

        if should_install_model_weights and model_weights_src_uri is None:
            error_print("Parameter --model-weights-src-uri is required if model weights do not exist in S3.")
            sys.exit(1)

        return should_install_model_weights

    def _install_model_weights(self, model_weights_src_uri, destination_bucket, destination_key, should_unpack=False):
        debug_print("")
        debug_print(f"####################################################################")
        debug_print(f"####################  Installing model weights  ####################")
        debug_print(f"####################################################################")

        if should_unpack:
            model_weight_unpacked_dir = download_and_untar_uri(model_weights_src_uri)
            self._s3_util_client.copy_directory_to_s3(model_weight_unpacked_dir, destination_bucket, destination_key)
        else:
            model_weight_tar_file_path = download_uri(model_weights_src_uri)
            self._s3_util_client.copy_file_to_s3(model_weight_tar_file_path, destination_bucket, destination_key)

        debug_print(f"Model weights mirrored to s3://{destination_bucket}/{destination_key} successfully.")

    def _check_model_image_options(self, model_image_src_cr_uri, model_image_src_tar_uri, model_image_dest_uri):
        should_install_model_image = True
        if self._ecr_util_client.image_exists(model_image_dest_uri):
            should_install_model_image = False

        if should_install_model_image and model_image_src_cr_uri is None and model_image_src_tar_uri is None:
            error_print("Parameter --model-image-src-cr-uri or --model-image-src-tar-uri is required if model image does not exist in ECR.")
            sys.exit(1)

        return should_install_model_image

    def _install_model_image(self, model_image_src_cr_uri, model_image_src_tar_uri, model_image_dest_uri):
        debug_print("")
        debug_print(f"####################################################################")
        debug_print(f"####################  Installing model image  ######################")
        debug_print(f"####################################################################")

        if model_image_src_cr_uri is None and model_image_src_tar_uri is None:
            error_print("Either model-image-src-cr-uri or model-image-src-tar-uri must be provided.")
            sys.exit(1)

        if model_image_src_cr_uri is not None:
            self._ecr_util_client.mirror_image(model_image_src_cr_uri, model_image_dest_uri)
        else:
            image_tar_file_path = download_uri(model_image_src_tar_uri)
            self._ecr_util_client.upload_image_from_tar(image_tar_file_path, model_image_dest_uri)

        debug_print(f"Model image mirrored to {model_image_dest_uri} successfully.")

    def _deploy_model(self, model_weights_bucket, model_weights_key, model_image_uri, model_template_request, model_instance_request, model_deployment_request):
        debug_print("")
        debug_print(f"####################################################################")
        debug_print(f"#######################  Deploying model  ##########################")
        debug_print(f"####################################################################")

        registry, repository, tag = get_registry_repository_tag(model_image_uri)
        date_suffix = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        model_name = f"{repository}_{tag}__{model_weights_key}__{date_suffix}"

        model_template_request.name = model_name
        model_template_request.vendor_configuration.bundle_config.registry = registry
        model_template_request.vendor_configuration.bundle_config.image = repository
        model_template_request.vendor_configuration.bundle_config.tag = tag

        debug_print(f"Creating model template {model_name}...")
        try:
            model_template_collection = self._egp_client.model_templates()
            model_template_response = model_template_collection._post(model_template_collection._sub_path, model_template_request)
            if model_template_response.status_code != 200:
                raise Exception(f"Request error: {model_template_response.json()}")
            model_template_response_dict = model_template_response.json()
            if not isinstance(model_template_response_dict, dict):
                raise Exception(f"Unexpected response: {model_template_response_dict}")
            model_template = ModelTemplate(**model_template_response_dict)
        except Exception as e:
            error_print(f"Error creating model template: {e}")
            error_print("Check your API key and other API configuration.")
            error_print("Reach out to Scale for further help.")
            sys.exit(1)
        debug_print(f"Model template {model_name} created successfully with ID {model_template.id}.")

        model_instance_name = f"{model_name}___instance"

        model_instance_request.name = model_instance_name
        model_instance_request.model_template_id = model_template.id

        debug_print(f"Creating model instance {model_instance_name}...")
        try:
            model_instance_collection = self._egp_client.models()
            model_instance_response = model_instance_collection._post(model_instance_collection._sub_path, model_instance_request)
            if model_instance_response.status_code != 200:
                raise Exception(f"Request error: {model_instance_response.json()}")
            model_instance_response_dict = model_instance_response.json()
            if not isinstance(model_instance_response_dict, dict):
                raise Exception(f"Unexpected response: {model_instance_response_dict}")
            model_instance = ModelInstance(**model_instance_response_dict)
        except Exception as e:
            error_print(f"Error creating model instance: {e}")
            error_print("Check your API key and other API configuration.")
            error_print("Reach out to Scale for further help.")
            sys.exit(1)
        debug_print(f"Model instance {model_instance_name} created successfully with ID {model_instance.id}.")

        model_deployment_name = f"{model_name}___deployment"

        model_deployment_request.name = model_deployment_name
        model_deployment_request.model_creation_parameters = {
            "MODEL_BUCKET": model_weights_bucket,
            "MODEL_PATH": model_weights_key
        }

        debug_print(f"Deploying model {model_deployment_name}...")
        model_deployment_collection = self._egp_client.models().deployments()
        path = model_deployment_collection._sub_path.format(model_id=model_instance.id)

        deployment_try_count = 0
        while True:
            try:
                model_deployment_response = model_deployment_collection._post(path, model_deployment_request)
                if model_deployment_response.status_code != 200:
                    raise Exception(f"Request error: {model_deployment_response.json()}")
                model_deployment_response_dict = model_deployment_response.json()
                if not isinstance(model_deployment_response_dict, dict):
                    raise Exception(f"Unexpected response: {model_deployment_response_dict}")
                model_deployment = ModelDeployment(**model_deployment_response_dict)
                break
            except Exception as e:
                deployment_try_count += 1
                if deployment_try_count > 3:
                    error_print(f"Error deploying model: {e}")
                    error_print("Check your API key and other API configuration.")
                    error_print("Reach out to Scale for further help.")
                    sys.exit(1)
                debug_print(f"Error deploying model: {e}")
                debug_print(f"Retrying deployment {deployment_try_count}...")
                time.sleep(10)
        debug_print(model_deployment)
        debug_print(f"Model {model_deployment_name} deployed successfully with ID {model_deployment.id}.")

        poll_count = 0
        internal_service_error_count = 0
        debug_print(f"Deployment Status: {model_deployment.status}")
        while model_deployment.status != "READY":
            poll_count += 1
            time.sleep(10)

            try:
                model_deployment = self._egp_client.models().deployments().get(id=model_deployment.id, model=model_instance)
            except EGPException as e:
                if 500 <= e.code < 600:
                    internal_service_error_count += 1
                    debug_print(f"Internal service error: {e}")
                    debug_print(f"Internal service error count: {internal_service_error_count}")
                    if internal_service_error_count > 3:
                        debug_print(f"Error testing model deployment {model_deployment.id}, under instance {model_instance.id}: {e}")
                        debug_print("Check the model deployment and instance configurations.")
                        debug_print("Reach out to Scale for further help.")
                        sys.exit(1)
                    time.sleep(10)
                    continue
                else:
                    error_print(f"Error testing model deployment {model_deployment.id}, under instance {model_instance.id}: {e}")
                    error_print("Check the model deployment and instance configurations.")
                    error_print("Reach out to Scale for further help.")
                    sys.exit(1)
            except Exception as e:
                debug_print(e.__class__)
                debug_print(e.__class__.__name__)

            debug_print(f"Waiting on Model Deployment, Status: {model_deployment.status}")
            debug_print(f"Poll count: {poll_count}")

            if poll_count > 12:
                raise TimeoutError("Model deployment took too long to complete. Exiting")

        debug_print(f"Model deployment {model_deployment_name} is ready.")

        return model_instance, model_deployment

    def _load_app_data_config(self, app_data_uri):
        try:
            app_data_file_path = download_uri(app_data_uri)
        except Exception as e:
            error_print(f"Error downloading knowledge base data from {app_data_uri}: {e}")
            error_print("Check the knowledge base data source and try again.")
            sys.exit(1)

        try:
            with open(app_data_file_path, "r") as f:
                app_data = json.load(f)

            if not isinstance(app_data, dict):
                raise ValueError("App data must be a dictionary.")

            parsed_app_data = {key: AppConfigInput(**value) for key, value in app_data.items()}
            return parsed_app_data
        except Exception as e:
            error_print(f"Error parsing app data: {e}")
            error_print("Check the knowledge base data source and try again.")
            sys.exit(1)

    def _load_knowledge_bases_and_create_app(self, name: str, app_kb_input: AppConfigInput, os_embedding_deployment_id, ft_embedding_deployment_id):
        debug_print("")
        debug_print(f"####################################################################")
        debug_print(f"######################  Creating Application  ######################")
        debug_print(f"####################################################################")

        debug_print(f"Creating app {name}...")

        env_settings = []
        time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        for kb_key, knowledge_base_data in app_kb_input.knowledge_bases.items():
            embedding_deployment_id = os_embedding_deployment_id
            if knowledge_base_data.embedding_config.embedding_model == EMBEDDING_MODEL_FINE_TUNED:
                embedding_deployment_id = ft_embedding_deployment_id

            kb_id = self._load_knowledge_base(
                f"{name}-{kb_key}-{embedding_deployment_id}--{time_str}",
                embedding_deployment_id,
                knowledge_base_data
            )
            env_key = f"{name.upper()}_{kb_key.upper()}_KNOWLEDGE_BASE_ID"
            env_setting = f"{env_key}={kb_id}"
            env_settings.append(env_setting)

        return env_settings

    def _load_knowledge_base(self, name, embedding_deployment_id, knowledge_base_data: KnowledgeBaseData):
        debug_print(f"Creating knowledge base {name}...")
        try:
            knowledge_base = self._egp_client.knowledge_bases().create(
                name=name,
                model_deployment_id=embedding_deployment_id
            )
        except Exception as e:
            error_print(f"Error creating knowledge base {name}: {e}")
            error_print("Check your API key and other API configuration.")
            error_print("Reach out to Scale for further help.")
            sys.exit(1)
        debug_print(f"Knowledge base {name} created successfully with ID {knowledge_base.knowledge_base_id}.")

        debug_print(f"Creating upload for knowledge base {name}...")
        try:
            upload = self._egp_client.knowledge_bases().uploads().create_local_upload(
                knowledge_base=knowledge_base,
                chunks=knowledge_base_data.chunks,
                data_source_config=LocalChunksSourceConfig(
                    artifact_name=f"{name}_upload",
                    artifact_uri=f"{knowledge_base.knowledge_base_name}_{uuid4()}",
                    deduplication_strategy="Overwrite"
                )
            )
        except Exception as e:
            error_print(f"Error uploading knowledge base {name}: {e}")
            error_print("Check your API key and other API configuration.")
            error_print("Reach out to Scale for further help.")
            sys.exit(1)
        debug_print(f"Knowledge base {name} upload started with ID {upload.upload_id}.")

        poll_count = 0
        while upload.status != "Completed":
            time.sleep(10)
            poll_count += 1
            try:
                upload = self._egp_client.knowledge_bases().uploads().get(
                    id=upload.upload_id,
                    knowledge_base=knowledge_base
                )
            except Exception as e:
                error_print(f"Error polling knowledge base {name} upload: {e}")
                error_print("Check your API key and other API configuration.")
                error_print("Reach out to Scale for further help.")
                sys.exit(1)
            debug_print(f"Waiting on Knowledge Base Upload, Status: {upload.status}")
            debug_print(f"Poll count: {poll_count}")
            debug_print(f"Status reason: {upload.status_reason}")
            debug_print(f"Artifact statuses: {upload.artifacts_status}")

        debug_print(f"Knowledge base {name} upload completed successfully.")

        return knowledge_base.knowledge_base_id

    def _check_model_deployed(self, model_instance, model_deployment, model_type):
        request = TEST_EMBEDDING_REQUEST if model_type == ModelType.EMBEDDING else TEST_COMPLETION_REQUEST
        poll_count = 0
        timeout = 30
        internal_service_error_count = 0
        debug_print(f"Testing model deployment {model_deployment.id}, under instance {model_instance.id}...")
        while True:
            debug_print(f"Waited {poll_count * timeout} seconds for model to be ready")
            poll_count += 1
            try:
                result = self._egp_client.models().deployments().execute(
                    model_deployment.id,
                    model_instance,
                    request,
                    timeout=timeout
                )
                break
            except TimeoutException as e:
                continue
            except EGPException as e:
                if 500 <= e.code < 600:
                    internal_service_error_count += 1
                    debug_print(f"Internal service error: {e}")
                    debug_print(f"Internal service error count: {internal_service_error_count}")
                    if internal_service_error_count > 3:
                        debug_print(f"Error testing model deployment {model_deployment.id}, under instance {model_instance.id}: {e}")
                        debug_print("Check the model deployment and instance configurations.")
                        debug_print("Reach out to Scale for further help.")
                        sys.exit(1)
                    time.sleep(10)
                    continue
                else:
                    error_print(f"Error testing model deployment {model_deployment.id}, under instance {model_instance.id}: {e}")
                    error_print("Check the model deployment and instance configurations.")
                    error_print("Reach out to Scale for further help.")
                    sys.exit(1)
            except Exception as e:
                error_print(f"Error testing model deployment {model_deployment.id}, under instance {model_instance.id}: {e}")
                error_print("Reach out to Scale for further help.")
                sys.exit(1)
        print("Model deployment is ready.")


class S3UtilClient:
    def __init__(self, s3_client: boto3.session.Session.client):
        self.s3_client = s3_client

    def _list_objects_v2(self, Bucket=None, Prefix=None):
        try:
            return self.s3_client.list_objects_v2(Bucket=Bucket, Prefix=Prefix)
        except Exception as e:
            error_print(f"Error listing objects in s3://{Bucket}/{Prefix}: {e}")
            error_print("Check your AWS credentials or role access and try again.")
            sys.exit(1)

    def _upload_file(self, file_path, bucket, key):
        try:
            self.s3_client.upload_file(file_path, bucket, key)
        except Exception as e:
            error_print(f"Error uploading file {file_path} to s3://{bucket}/{key}: {e}")
            error_print("Check your AWS credentials or role access and try again.")
            sys.exit(1)

    def does_file_exist(self, bucket, file_key):
        try:
            try:
                self.s3_client.head_object(Bucket=bucket, Key=file_key)
                return True
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == '404':
                    return False
                raise e
        except Exception as e:
            error_print(f"Error checking if object s3://{bucket}/{file_key} exists: {e}")
            error_print("Check your AWS credentials or role access and try again.")
            sys.exit(1)

    def does_directory_exists(self, bucket, key):
        if not key.endswith('/'):
            key = f"{key}/"

        response = self._list_objects_v2(Bucket=bucket, Prefix=key)
        return 'Contents' in response

    def copy_directory_to_s3(self, dir_path, destination_bucket, destination_key):
        debug_print(f"Uploading contents of {dir_path} to s3://{destination_bucket}/{destination_key} ...")
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                # Skip hidden files (created by tar.extractall)
                if file.startswith('.'):
                    continue

                local_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_file_path, dir_path)
                s3_key = os.path.join(destination_key, relative_path)
                self._upload_file(local_file_path, destination_bucket, s3_key)
        debug_print(f"Finished uploading to s3.")

    def copy_file_to_s3(self, file_path, destination_bucket, destination_key):
        debug_print(f"Uploading {file_path} to s3://{destination_bucket}/{destination_key} ...")
        self._upload_file(file_path, destination_bucket, destination_key)
        debug_print(f"Finished uploading to s3")


class EcrUtilClient:

    def __init__(self, ecr_client, docker_client):
        self.ecr_client = ecr_client
        self.docker_client = docker_client

    def image_exists(self, image_uri):
        _, repository, tag = get_registry_repository_tag(image_uri)
        try:
            response = self.ecr_client.describe_images(
                repositoryName=repository,
                imageIds=[
                    {
                        'imageTag': tag
                    }
                ]
            )
            return len(response['imageDetails']) > 0
        except self.ecr_client.exceptions.ImageNotFoundException:
            return False
        except self.ecr_client.exceptions.RepositoryNotFoundException:
            error_print(f"Repository {repository} not found.")
            error_print("Check the repository name or create it in the ECR and try again.")
            sys.exit(1)
        except Exception as e:
            error_print(f"Error checking if image {image_uri} exists: {e}")
            error_print("Check your AWS credentials or permissions and try again.")
            sys.exit(1)

    def mirror_image(self, src_uri, dest_uri):
        debug_print(f"Preparing to mirror image {src_uri} to {dest_uri}...")

        debug_print(f"Pulling image {src_uri}...")
        try:
            self.docker_client.images.pull(src_uri)
        except Exception as e:
            error_print(f"Error pulling image {src_uri}: {e}")
            error_print("Check the image source and try again.")
            error_print("Reach out to Scale for help with authorization issues.")
            sys.exit(1)

        try:
            ecr_registry, ecr_repo, ecr_tag = get_registry_repository_tag(dest_uri)
            ecr_reg_repo = f"{ecr_registry}/{ecr_repo}"
            debug_print(f"Tagging image {src_uri} to repo {ecr_reg_repo} and tag {ecr_tag}...")
            try:
                self.docker_client.images.get(src_uri).tag(ecr_reg_repo, tag=ecr_tag)
            except Exception as e:
                error_print(f"Error tagging image {src_uri} as {dest_uri}: {e}")
                error_print("Check your permissions and try again.")
                sys.exit(1)

            debug_print(f"Pushing image {dest_uri}...")
            debug_print("Depending on image size, this could take some time...")
            try:
                push_log = str(self.docker_client.images.push(dest_uri))
                for line in push_log.split("\n"):
                    if "error" in line.lower():
                        raise Exception(line)
            except Exception as e:
                error_print(f"Error pushing image {dest_uri}: {e}")
                error_print("Check your permissions and try again.")
                sys.exit(1)
        finally:
            try:
                self.docker_client.images.remove(src_uri)
            except Exception as e:
                error_print(f"Error removing locally downloaded image {src_uri}: {e}")
                error_print("Try to remove manually.")

        debug_print("Finished mirroring image.")

    def upload_image_from_tar(self, tar_file_path, dest_uri):
        debug_print(f"Preparing to upload image from tar file {tar_file_path} to {dest_uri}...")

        debug_print(f"Loading image from tar file {tar_file_path}...")
        try_count = 0
        while True:
            try:
                with open(tar_file_path, 'rb') as tar_file:
                    load_response = self.docker_client.images.load(tar_file)
                    image_id = load_response[0].id
                break
            except Exception as e:
                try_count += 1
                if try_count > 3:
                    error_print(f"Error loading image from tar file {tar_file_path}: {e}")
                    error_print("Check the tar file source for errors or expiration.")
                    sys.exit(1)
                debug_print(f"Error loading image from tar file {tar_file_path}: {e}")
                debug_print(f"Retrying loading image from tar file {tar_file_path} {try_count} time(s)...")
                time.sleep(5)
        debug_print(f"Loaded image locally with id {image_id}.")

        debug_print(f"Pushing image to {dest_uri}...")
        debug_print("Depending on image size, this could take some time...")
        try:
            self.docker_client.images.get(image_id).tag(dest_uri)
            push_log = str(self.docker_client.images.push(dest_uri))
            for line in push_log.split("\n"):
                if "error" in line.lower():
                    raise Exception(line)
        except Exception as e:
            error_print(f"Error pushing image {dest_uri}: {e}")
            error_print("Check your permissions and try again.")
            sys.exit(1)
        finally:
            try:
                self.docker_client.images.remove(image_id, force=True)
            except Exception as e:
                error_print(f"Error removing locally loaded image {image_id}: {e}")
                error_print("Try to remove manually.")

        debug_print("Finished uploading image from tar file.")


def download_uri(uri):
    if uri.startswith("http"):
        uri_hash = get_uri_hash(uri)
        out_path = os.path.join(CACHE_DIR, uri_hash)

        if not os.path.exists(out_path):
            os.makedirs(CACHE_DIR, exist_ok=True)

            tmp_out_path = f"{out_path}.tmp"
            try:
                debug_print(f"Downloading {uri} to {out_path}...")
                debug_print("Depending on file size, this could take some time...")
                with requests.get(uri, stream=True) as r:
                    with open(tmp_out_path, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                os.rename(tmp_out_path, out_path)
                debug_print(f"Finished downloading to {out_path}.")
            except Exception as e:
                error_print(f"Error downloading {uri} to {out_path}: {e}")
                error_print("Check the source for errors or if using a presigned URL, check for expiration.")
                sys.exit(1)
            finally:
                # Delete the temp file if it exists
                if os.path.exists(tmp_out_path):
                    os.remove(tmp_out_path)
        else:
            debug_print(f"Using cached file for {uri} at {out_path}.")

        return out_path
    else:
        raise ValueError("Currently only supports http(s) URIs")


def download_and_untar_uri(uri):
    uri_hash = get_uri_hash(uri)
    unpack_dir = os.path.join(CACHE_UNTAR_DIR, uri_hash)

    if not os.path.exists(unpack_dir):
        tar_file_path = download_uri(uri)

        temp_unpack_dir = f"{unpack_dir}-tmp"
        os.makedirs(temp_unpack_dir, exist_ok=True)

        debug_print(f"Extracting tar file {tar_file_path} to {unpack_dir}...")
        try:
            with tarfile.open(tar_file_path) as tar:
                tar.extractall(path=temp_unpack_dir)
            os.rename(temp_unpack_dir, unpack_dir)
            debug_print(f"Finished extracting to {unpack_dir}.")
        except Exception as e:
            error_print(f"Error extracting tar file {tar_file_path}")
            error_print(e)
            error_print("Check the tar file source for errors or if using a presigned URL, check for expiration.")
            sys.exit(1)
        finally:
            # Delete the temp directory if it exists
            if os.path.exists(temp_unpack_dir):
                shutil.rmtree(temp_unpack_dir)
    else:
        debug_print(f"Using cached directory for {uri} at {unpack_dir}.")

    return unpack_dir


def get_registry_repository_tag(image_uri):
    registry, repository_and_tag = image_uri.split("/", 1)
    repository, tag = repository_and_tag.split(":")
    return registry, repository, tag


def split_s3_uri(s3_uri):
    parsed = urlparse(s3_uri)
    bucket = parsed.netloc
    key = parsed.path.lstrip('/')
    return bucket, key


def is_s3_presigned_url(uri):
    pattern = r'^https://.+\.s3\..+\.amazonaws\.com/.+$'
    return bool(re.match(pattern, uri))


def remove_uri_query(uri):
    return uri.split("?")[0]


def get_uri_hash(uri):
    if is_s3_presigned_url(uri):
        uri = remove_uri_query(uri)
    return generate_sha256_hash(uri)


def generate_sha256_hash(s):
    return hashlib.sha256(s.encode()).hexdigest()
