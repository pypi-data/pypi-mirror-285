#
# Copyright 2023 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

import trafaret as t

from datarobot import UseCase
from datarobot._experimental.models.genai.custom_model_embedding_validation import (
    CustomModelEmbeddingValidation,
)
from datarobot.models.api_object import APIObject
from datarobot.models.genai.vector_database import (  # noqa: F401; pylint: disable=unused-import
    CustomModelVectorDatabaseValidation,
    embedding_model_trafaret,
    EmbeddingModel,
)
from datarobot.models.genai.vector_database import (  # noqa: F401; pylint: disable=unused-import
    SupportedTextChunkings,
    TextChunkingConfig,
    TextChunkingMethod,
    TextChunkingParameterFields,
)
from datarobot.models.genai.vector_database import ChunkingParameters as BaseChunkingParameters
from datarobot.models.genai.vector_database import SupportedEmbeddings as BaseSupportedEmbeddings
from datarobot.models.genai.vector_database import VectorDatabase as BaseVectorDatabase
from datarobot.models.use_cases.utils import get_use_case_id

chunking_parameters_trafaret = t.Dict(
    {
        t.Key("embedding_model", optional=True, default=None): str,
        t.Key("embedding_validation_id", optional=True, default=None): str,
        t.Key("chunking_method"): t.Or(str, t.Null),
        t.Key("chunk_size"): t.Or(t.Int, t.Null),
        t.Key("chunk_overlap_percentage"): t.Or(t.Int, t.Null),
        t.Key("separators"): t.Or(t.List(t.String), t.Null),
        t.Key("custom_chunking", default=False): t.Bool,
    }
).ignore_extra("*")


supported_custom_model_embedding_trafaret = t.Dict(
    {
        t.Key("id"): t.String,
        t.Key("name"): t.String,
    }
)

supported_embeddings_trafaret = t.Dict(
    {
        t.Key("embedding_models"): t.List(embedding_model_trafaret),
        t.Key("default_embedding_model"): t.String,
        t.Key("custom_model_embedding_validations"): t.List(
            supported_custom_model_embedding_trafaret
        ),
    }
).ignore_extra("*")

vector_database_trafaret = t.Dict(
    {
        t.Key("id"): t.String,
        t.Key("name"): t.String,
        t.Key("size"): t.Int,
        t.Key("use_case_id"): t.String,
        t.Key("dataset_id", optional=True, default=None): t.Or(t.Null, t.String),
        t.Key("embedding_model", optional=True, default=None): t.Or(t.Null, t.String),
        t.Key("chunking_method", optional=True, default=None): t.Or(t.Null, t.String),
        t.Key("chunk_size"): t.Or(t.Int, t.Null),
        t.Key("chunk_overlap_percentage"): t.Or(t.Int, t.Null),
        t.Key("chunks_count"): t.Int,
        t.Key("custom_chunking", default=False): t.Bool,
        t.Key("separators"): t.Or(t.List(t.String(allow_blank=True)), t.Null),
        t.Key("creation_date"): t.String,
        t.Key("creation_user_id"): t.String,
        t.Key("organization_id"): t.String,
        t.Key("tenant_id"): t.String,
        t.Key("last_update_date"): t.String,
        t.Key("execution_status"): t.String,
        t.Key("playgrounds_count"): t.Int,
        t.Key("dataset_name"): t.String(allow_blank=True),
        t.Key("user_name"): t.String,
        t.Key("source"): t.String,
        t.Key("validation_id", optional=True, default=None): t.Or(t.Null, t.String),
        t.Key("error_message", optional=True, default=None): t.Or(t.Null, t.String),
        t.Key("embedding_validation_id", optional=True, default=None): t.Or(t.Null, t.String),
        t.Key("is_separator_regex"): t.Bool,
    }
).ignore_extra("*")


class ChunkingParameters(BaseChunkingParameters):
    """
    Parameters defining how documents are split and embedded.

    Attributes
    ----------
    embedding_model : Optional[str]
        Name of the text embedding model.
        Currently supported options are listed in VectorDatabaseEmbeddingModel
        but the values can differ with different platform versions.
    chunking_method : str
        Name of the method to split dataset documents.
        Currently supported options are listed in VectorDatabaseChunkingMethod
        but the values can differ with different platform versions.
    chunk_size : int
        Size of each text chunk in number of tokens.
    chunk_overlap_percentage : int
        Overlap percentage between chunks.
    separators : list[str]
        Strings used to split documents into text chunks.
    embedding_validation : Optional[CustomModelEmbeddingValidation, SupportedCustomModelEmbedding, str]
        ID or object for custom embedding validation.
    custom_chunking : bool
        Determines if the chunking is custom. With custom chunking,
        dataset rows are not split into chunks automatically;
        instead, the user provides the chunks.
    """

    _converter = chunking_parameters_trafaret

    def __init__(
        self,
        embedding_model: Optional[str],
        chunking_method: Union[str, None],
        chunk_size: Union[int, None],
        chunk_overlap_percentage: Union[int, None],
        separators: Union[List[str], None],
        custom_chunking: bool = False,
        embedding_validation: Optional[
            Union[CustomModelEmbeddingValidation, SupportedCustomModelEmbedding, str]
        ] = None,
    ):
        super().__init__(
            embedding_model, chunking_method, chunk_size, chunk_overlap_percentage, separators  # type: ignore[arg-type]
        )
        self.embedding_validation_id = self._get_embedding_validation_id(embedding_validation)
        self.custom_chunking = custom_chunking

    @staticmethod
    def _get_embedding_validation_id(
        embedding_validation: Optional[
            Union[CustomModelEmbeddingValidation, SupportedCustomModelEmbedding, str]
        ] = None,
    ) -> Union[str, None]:
        """Get ID of custom embedding validation from supported objects"""
        if isinstance(
            embedding_validation, (CustomModelEmbeddingValidation, SupportedCustomModelEmbedding)
        ):
            return embedding_validation.id
        return embedding_validation


class SupportedCustomModelEmbedding(APIObject):
    """
    All supported custom embedding models for the use case.

    Attributes
    ----------
    id : str
        ID of the custom model embedding validation.
    name : str
        The name of the custom model embedding validation.
    """

    _converter = supported_custom_model_embedding_trafaret

    def __init__(
        self,
        id: str,
        name: str,
    ):
        self.id = id
        self.name = name


class SupportedEmbeddings(BaseSupportedEmbeddings):
    """
    All supported embedding models including the recommended default model.

    Attributes
    ----------
    embedding_models : list[EmbeddingModel]
        All supported embedding models.
    default_embedding_model : str
        Name of the default recommended text embedding model.
        Currently supported options are listed in VectorDatabaseEmbeddingModel
        but the values can differ with different platform versions.
    custom_model_embedding_validations : List[str]
        External embedding models that have been validated
    """

    _converter = supported_embeddings_trafaret

    def __init__(
        self,
        embedding_models: List[Dict[str, Any]],
        default_embedding_model: str,
        custom_model_embedding_validations: List[Dict[str, Any]],
    ):
        super().__init__(embedding_models, default_embedding_model)
        self.custom_model_embedding_validations = [
            SupportedCustomModelEmbedding.from_server_data(validation)
            for validation in custom_model_embedding_validations
        ]


class VectorDatabase(BaseVectorDatabase):
    """
    Metadata for a DataRobot vector database accessible to the user.

    Attributes
    ----------
    id : str
        Vector database ID.
    name : str
        Vector database name.
    size : int
        Size of the vector database assets in bytes.
    use_case_id : str
        Linked use case ID.
    dataset_id : str
        ID of the dataset used for creation.
    embedding_model : str
        Name of the text embedding model.
        Currently supported options are listed in VectorDatabaseEmbeddingModel
        but the values can differ with different platform versions.
    chunking_method : str or None
        Name of the method to split dataset documents.
        Currently supported options are listed in VectorDatabaseChunkingMethod
        but the values can differ with different platform versions.
    chunk_size : int or None
        Size of each text chunk in number of tokens.
    chunk_overlap_percentage : int or None
        Overlap percentage between chunks.
    chunks_count : int
        Total number of text chunks.
    custom_chunking : bool
        Determines if the chunking is custom. With custom chunking,
        dataset rows are not split into chunks automatically;
        instead, the user provides the chunks.
    separators : list[string] or None
        Separators for document splitting.
    creation_date : str
        Date when the database was created.
    creation_user_id : str
        ID of the creating user.
    organization_id : str
        Creating user's organization ID.
    tenant_id : str
        Creating user's tenant ID.
    last_update_date : str
        Last update date for the database.
    execution_status : str
        Database execution status.
        Currently supported options are listed in VectorDatabaseExecutionStatus
        but the values can differ with different platform versions.
    playgrounds_count : int
        Number of using playgrounds.
    dataset_name : str
        Name of the used dataset.
    user_name : str
        Name of the creating user.
    source : str
        Source of the vector database.
        Currently supported options are listed in VectorDatabaseSource
        but the values can differ with different platform versions.
    validation_id : Optional[str]
        ID of custom model vector database validation.
        Only filled for external vector databases.
    error_message : Optional[str]
        Additional information for errored vector database.
    embedding_validation_id : Optional[str]
        ID of the custom embedding validation, if any.
    is_separator_regex : bool
        Whether the separators should be treated as regular expressions.
    """

    _converter = vector_database_trafaret

    def __init__(
        self,
        id: str,
        name: str,
        size: int,
        use_case_id: str,
        dataset_id: Optional[str],
        embedding_model: Optional[str],
        chunking_method: Union[Optional[str], None],
        chunk_size: Union[int, None],
        chunk_overlap_percentage: Union[int, None],
        chunks_count: int,
        custom_chunking: bool,
        separators: Union[List[str], None],
        creation_date: str,
        creation_user_id: str,
        organization_id: str,
        tenant_id: str,
        last_update_date: str,
        execution_status: str,
        playgrounds_count: int,
        dataset_name: str,
        user_name: str,
        source: str,
        validation_id: Optional[str],
        error_message: Optional[str],
        is_separator_regex: bool,
        embedding_validation_id: Optional[str],
    ):
        super().__init__(
            id,
            name,
            size,
            use_case_id,
            dataset_id,
            embedding_model,
            chunking_method,
            chunk_size,
            chunk_overlap_percentage,
            chunks_count,
            separators,
            creation_date,
            creation_user_id,
            organization_id,
            tenant_id,
            last_update_date,
            execution_status,
            playgrounds_count,
            dataset_name,
            user_name,
            source,
            validation_id,
            error_message,
            is_separator_regex,
        )
        self.embedding_validation_id = embedding_validation_id
        self.custom_chunking = custom_chunking

    @classmethod
    def get_supported_embeddings(
        cls,
        dataset_id: Optional[str] = None,
        use_case: Optional[Union[UseCase, str]] = None,
    ) -> SupportedEmbeddings:
        """Get all supported and the recommended embedding models.

        Parameters
        ----------
        dataset_id : str, optional
            ID of a dataset for which the recommended model is returned
            based on the detected language of that dataset.
        use_case : Optional[UseCase, str]
            May be Use Case ID or the Use Case entity.

        Returns
        -------
        supported_embeddings : SupportedEmbeddings
            The supported embedding models.
        """
        params = {
            "dataset_id": dataset_id,
            "use_case_id": get_use_case_id(use_case, is_required=False),
        }
        url = f"{cls._client.domain}/{cls._path}/supportedEmbeddings/"
        r_data = cls._client.get(url, params=params)
        return SupportedEmbeddings.from_server_data(r_data.json())
