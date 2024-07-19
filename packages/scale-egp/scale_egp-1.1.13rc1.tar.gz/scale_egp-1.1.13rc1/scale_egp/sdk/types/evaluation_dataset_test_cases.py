from __future__ import annotations

from typing import Optional, Dict, Any, Union, List, Literal

import pydantic

PYDANTIC_V2 = hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2.")

if PYDANTIC_V2:
    from pydantic.v1 import Field, validator, ValidationError
else:
    from pydantic import Field, validator, ValidationError


from scale_egp.sdk.enums import TestCaseSchemaType, ExtraInfoSchemaType
from scale_egp.utils.model_utils import Entity, BaseModel, RootModel


class ChunkData(BaseModel):
    text: str
    metadata: Dict[str, Any]

class StringExtraInfo(BaseModel):
    schema_type: Literal[ExtraInfoSchemaType.STRING] = ExtraInfoSchemaType.STRING
    info: str

class ChunksExtraInfo(BaseModel):
    schema_type: Literal[ExtraInfoSchemaType.CHUNKS] = ExtraInfoSchemaType.CHUNKS
    chunks: List[ChunkData]

class ExtraInfo(RootModel):
    __root__: Union[StringExtraInfo, ChunksExtraInfo] = Field(..., discriminator="schema_type")

class GenerationTestCaseData(BaseModel):
    """
    A data model representing the data of a Testcase with a GENERATION schema type.

    Attributes:
        input: The input to the generation model
        expected_output: The expected output of the generation model
        expected_extra_info: The expected extra info of the generation model
    """

    input: str
    expected_output: Optional[str] = ""
    expected_extra_info: Optional[ExtraInfo]


class TestCase(Entity):
    """
    A data model representing a test case.

    Attributes:
        id: The ID of the test case
        evaluation_dataset_id: The ID of the evaluation dataset that the test case belongs to
        schema_type: The schema type of the test case
        test_case_data: The data of the test case. In general, this can be thought of as the
            data to evaluate an application against.
    """

    id: str
    evaluation_dataset_id: str
    schema_type: TestCaseSchemaType
    test_case_data: Union[GenerationTestCaseData]
    test_case_metadata: Optional[Dict[str, Any]]
    chat_history: Optional[Dict[str, Any]]


class TestCaseRequest(BaseModel):
    schema_type: TestCaseSchemaType
    test_case_data: Union[GenerationTestCaseData]
    account_id: Optional[str] = Field(
        description="Account to create knowledge base in. If you have access to more than one "
        "account, you must specify an account_id"
    )
    test_case_metadata: Optional[Dict[str, Any]] = Field(
        description="Additional metadata to associate with the test case"
    )
    chat_history: Optional[Dict[str, Any]] = Field(
        description="Used for tracking previous chat interactions for multi-chat test cases"
    )

    @validator("test_case_data")
    @classmethod
    def test_case_data_matches_schema_type(cls, test_case_data, values):
        schema_type = values.get("schema_type")
        TestCaseSchemaValidator.validate(schema_type, test_case_data)
        return test_case_data


class TestCaseSchemaValidator:
    TEST_CASE_SCHEMA_TO_DATA_TYPE = {
        TestCaseSchemaType.GENERATION: GenerationTestCaseData,
    }

    @classmethod
    def validate(cls, schema_type: TestCaseSchemaType, data: Dict[str, Any]):
        try:
            model = cls.TEST_CASE_SCHEMA_TO_DATA_TYPE[schema_type]
            model.from_dict(data)
        except ValidationError as e:
            raise ValueError(f"Test case data does not match schema type {schema_type}") from e

    @classmethod
    def get_model(cls, schema_type: TestCaseSchemaType):
        return cls.TEST_CASE_SCHEMA_TO_DATA_TYPE[schema_type]

    @classmethod
    def dict_to_model(cls, schema_type: TestCaseSchemaType, data: Dict[str, Any]):
        return cls.TEST_CASE_SCHEMA_TO_DATA_TYPE[schema_type].from_dict(data)
