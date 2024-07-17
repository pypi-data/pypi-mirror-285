# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "ModelTemplateResponse",
    "VendorConfiguration",
    "VendorConfigurationBundleConfig",
    "VendorConfigurationEndpointConfig",
    "VendorConfigurationFineTuningJobBundleConfig",
    "VendorConfigurationFineTuningJobBundleConfigResources",
    "ModelCreationParametersSchema",
    "ModelCreationParametersSchemaParameter",
    "ModelRequestParametersSchema",
    "ModelRequestParametersSchemaParameter",
]


class VendorConfigurationBundleConfig(BaseModel):
    image: str

    registry: str

    tag: str

    command: Optional[List[str]] = None

    env: Optional[Dict[str, str]] = None

    healthcheck_route: Optional[str] = None

    predict_route: Optional[str] = None

    readiness_initial_delay_seconds: Optional[int] = None

    streaming_command: Optional[List[str]] = None

    streaming_predict_route: Optional[str] = None


class VendorConfigurationEndpointConfig(BaseModel):
    cpus: Optional[int] = None

    endpoint_type: Optional[Literal["SYNC", "ASYNC", "STREAMING", "BATCH"]] = None
    """An enum representing the different types of model endpoint types supported.

    Attributes: SYNC: Denotes that the model endpoint type is sync. ASYNC: Denotes
    that the model endpoint type is async. STREAMING: Denotes that the model
    endpoint type is streaming. BATCH: Denotes that the model endpoint type is
    batch.
    """

    gpu_type: Optional[
        Literal[
            "nvidia-tesla-t4",
            "nvidia-ampere-a10",
            "nvidia-ampere-a100",
            "nvidia-ampere-a100e",
            "nvidia-hopper-h100",
            "nvidia-hopper-h100-1g20gb",
            "nvidia-hopper-h100-3g40gb",
        ]
    ] = None
    """An enumeration."""

    gpus: Optional[int] = None

    high_priority: Optional[bool] = None

    max_workers: Optional[int] = None

    memory: Optional[str] = None

    min_workers: Optional[int] = None

    per_worker: Optional[int] = None
    """The maximum number of concurrent requests that an individual worker can service.

    Launch automatically scales the number of workers for the endpoint so that each
    worker is processing `per_worker` requests, subject to the limits defined by
    `min_workers` and `max_workers`.

    - If the average number of concurrent requests per worker is lower than
      `per_worker`, then the number of workers will be reduced. - Otherwise, if the
      average number of concurrent requests per worker is higher than `per_worker`,
      then the number of workers will be increased to meet the elevated traffic.

    Here is our recommendation for computing `per_worker`:

    1. Compute `min_workers` and `max_workers` per your minimum and maximum
       throughput requirements. 2. Determine a value for the maximum number of
       concurrent requests in the workload. Divide this number by `max_workers`.
       Doing this ensures that the number of workers will "climb" to `max_workers`.
    """

    storage: Optional[str] = None


class VendorConfigurationFineTuningJobBundleConfigResources(BaseModel):
    cpus: Optional[int] = None

    gpu_type: Optional[
        Literal[
            "nvidia-tesla-t4",
            "nvidia-ampere-a10",
            "nvidia-ampere-a100",
            "nvidia-ampere-a100e",
            "nvidia-hopper-h100",
            "nvidia-hopper-h100-1g20gb",
            "nvidia-hopper-h100-3g40gb",
        ]
    ] = None
    """An enumeration."""

    gpus: Optional[int] = None

    memory: Optional[str] = None

    storage: Optional[str] = None


class VendorConfigurationFineTuningJobBundleConfig(BaseModel):
    image: str

    registry: str

    tag: str

    command: Optional[List[str]] = None

    env: Optional[Dict[str, str]] = None

    mount_location: Optional[str] = None
    """
    The filesystem location where the fine tuning job's configuration will be
    available when it is started.
    """

    resources: Optional[VendorConfigurationFineTuningJobBundleConfigResources] = None

    training_dataset_schema_type: Optional[Literal["GENERATION", "RERANKING_QUESTIONS"]] = None
    """An enumeration."""


class VendorConfiguration(BaseModel):
    bundle_config: VendorConfigurationBundleConfig

    endpoint_config: Optional[VendorConfigurationEndpointConfig] = None

    fine_tuning_job_bundle_config: Optional[VendorConfigurationFineTuningJobBundleConfig] = None

    vendor: Optional[Literal["LAUNCH"]] = None


class ModelCreationParametersSchemaParameter(BaseModel):
    description: str

    name: str

    required: bool

    type: Literal["str", "int", "float", "bool"]


class ModelCreationParametersSchema(BaseModel):
    parameters: List[ModelCreationParametersSchemaParameter]


class ModelRequestParametersSchemaParameter(BaseModel):
    description: str

    name: str

    required: bool

    type: Literal["str", "int", "float", "bool"]


class ModelRequestParametersSchema(BaseModel):
    parameters: List[ModelRequestParametersSchemaParameter]


class ModelTemplateResponse(BaseModel):
    id: str
    """The unique identifier of the entity."""

    account_id: str
    """The ID of the account that owns the given entity."""

    created_at: datetime
    """The date and time when the entity was created in ISO format."""

    created_by_user_id: str
    """The user who originally created the entity."""

    endpoint_type: Literal["SYNC", "ASYNC", "STREAMING", "BATCH"]
    """An enum representing the different types of model endpoint types supported.

    Attributes: SYNC: Denotes that the model endpoint type is sync. ASYNC: Denotes
    that the model endpoint type is async. STREAMING: Denotes that the model
    endpoint type is streaming. BATCH: Denotes that the model endpoint type is
    batch.
    """

    api_model_type: Literal["COMPLETION", "CHAT_COMPLETION", "AGENT", "EMBEDDING", "RERANKING"] = FieldInfo(
        alias="model_type"
    )
    """An enum representing the different types of models supported.

    Attributes: COMPLETION: Denotes that the model type is completion.
    CHAT_COMPLETION: Denotes that the model type is chat completion. AGENT: Denotes
    that the model type is agent. EMBEDDING: Denotes that the model type is
    embedding. RERANKING: Denotes that the model type is reranking.
    """

    name: str

    vendor_configuration: VendorConfiguration
    """
    Configuration for launching a model using the Launch service which is an
    internal and self-hosted service developed by Scale that deploys models on
    Kubernetes.

    Attributes: vendor: The vendor of the model template bundle_config: The bundle
    configuration of the model template endpoint_config: The endpoint configuration
    of the model template
    """

    api_model_creation_parameters_schema: Optional[ModelCreationParametersSchema] = FieldInfo(
        alias="model_creation_parameters_schema", default=None
    )
    """
    The field names and types of available parameter fields which may be specified
    during model creation
    """

    api_model_request_parameters_schema: Optional[ModelRequestParametersSchema] = FieldInfo(
        alias="model_request_parameters_schema", default=None
    )
    """
    The field names and types of available parameter fields which may be specified
    in a model execution API's `model_request_parameters` field.
    """
