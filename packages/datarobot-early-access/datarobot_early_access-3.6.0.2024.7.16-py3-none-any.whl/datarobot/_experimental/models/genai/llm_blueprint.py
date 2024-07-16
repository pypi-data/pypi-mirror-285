# flake8: noqa
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

from typing import Any, cast, Dict, Optional, Union

from mypy_extensions import TypedDict
import trafaret as t

from datarobot._experimental.models.enums import VectorDatabaseRetrievers
from datarobot.enums import enum_to_list, PromptType
from datarobot.models.genai.llm import LLMDefinition
from datarobot.models.genai.llm_blueprint import (
    VectorDatabaseSettings as BaseVectorDatabaseSettings,
)
from datarobot.models.genai.llm_blueprint import LLMBlueprint as BaseLLMBlueprint
from datarobot.models.genai.llm_blueprint import LLMSettingsCommonDict, LLMSettingsCustomModelDict
from datarobot.models.genai.llm_blueprint import get_entity_id
from datarobot.models.genai.playground import Playground
from datarobot.models.genai.vector_database import VectorDatabase
from datarobot.utils import to_api

vector_database_settings_trafaret = t.Dict(
    {
        t.Key("max_documents_retrieved_per_prompt", optional=True): t.Or(t.Int, t.Null),
        t.Key("max_tokens", optional=True): t.Or(t.Int, t.Null),
        t.Key("retriever", optional=True): t.Enum(*VectorDatabaseRetrievers._member_names_),
        t.Key("add_neighbor_chunks", optional=True): t.Bool,
    }
).ignore_extra("*")


llm_blueprint_trafaret = t.Dict(
    {
        t.Key("id"): t.String,
        t.Key("name"): t.String,
        t.Key("description"): t.String(allow_blank=True),
        t.Key("is_saved"): t.Bool,
        t.Key("is_starred"): t.Bool,
        t.Key("playground_id"): t.String,
        t.Key("llm_id", optional=True): t.Or(t.String, t.Null),
        t.Key("llm_settings", optional=True): t.Or(t.Dict().allow_extra("*"), t.Null),
        t.Key("llm_name", optional=True): t.Or(t.String, t.Null),
        t.Key("creation_date"): t.String,
        t.Key("creation_user_id"): t.String,
        t.Key("creation_user_name"): t.String(allow_blank=True),
        t.Key("last_update_date"): t.String,
        t.Key("last_update_user_id"): t.String,
        t.Key("prompt_type"): t.Enum(*enum_to_list(PromptType)),
        t.Key("vector_database_id", optional=True): t.Or(t.String, t.Null),
        t.Key("vector_database_settings", optional=True): t.Or(
            vector_database_settings_trafaret, t.Null
        ),
        t.Key("vector_database_name", optional=True): t.Or(t.String, t.Null),
        t.Key("vector_database_status", optional=True): t.Or(t.String, t.Null),
        t.Key("vector_database_error_message", optional=True): t.Or(t.String, t.Null),
        t.Key("vector_database_error_resolution", optional=True): t.Or(t.String, t.Null),
        t.Key("custom_model_llm_validation_status", optional=True): t.Or(t.String, t.Null),
        t.Key("custom_model_llm_error_message", optional=True): t.Or(t.String, t.Null),
        t.Key("custom_model_llm_error_resolution", optional=True): t.Or(t.String, t.Null),
    }
).ignore_extra("*")


class VectorDatabaseSettingsDict(TypedDict):
    max_documents_retrieved_per_prompt: Optional[int]
    max_tokens: Optional[int]
    retriever: Optional[VectorDatabaseRetrievers]
    add_neighbor_chunks: Optional[bool]


class VectorDatabaseSettings(BaseVectorDatabaseSettings):
    """
    Settings for a DataRobot GenAI vector database associated with an LLM blueprint.

    Attributes
    ----------
    max_documents_retrieved_per_prompt : int or None, optional
        The maximum number of documents to retrieve for each prompt.
    max_tokens : int or None, optional
        The maximum number of tokens to retrieve for each document.
    retriever: VectorDatabaseRetrievers
        The vector database retriever name.
    add_neighbor_chunks
        Whether to add neighbouring documents to the retrieved documents.

    """

    _converter = vector_database_settings_trafaret

    def __init__(
        self,
        max_documents_retrieved_per_prompt: Optional[int] = None,
        max_tokens: Optional[int] = None,
        retriever: Optional[
            VectorDatabaseRetrievers
        ] = VectorDatabaseRetrievers.SINGLE_LOOKUP_RETRIEVER,
        add_neighbor_chunks: Optional[bool] = False,
    ):
        super().__init__(max_documents_retrieved_per_prompt, max_tokens)
        self.max_documents_retrieved_per_prompt = max_documents_retrieved_per_prompt
        self.max_tokens = max_tokens
        self.retriever = retriever
        self.add_neighbor_chunks = add_neighbor_chunks

    def to_dict(self) -> VectorDatabaseSettingsDict:
        return {
            "max_documents_retrieved_per_prompt": self.max_documents_retrieved_per_prompt,
            "max_tokens": self.max_tokens,
            "retriever": self.retriever,
            "add_neighbor_chunks": self.add_neighbor_chunks,
        }


class LLMBlueprint(BaseLLMBlueprint):
    """
    Metadata for a DataRobot GenAI LLM blueprint.

    Attributes
    ----------
    id : str
        The LLM blueprint ID.
    name : str
        The LLM blueprint name.
    description : str
        A description of the LLM blueprint.
    is_saved : bool
        Whether the LLM blueprint is saved (meaning the settings are locked and blueprint is eligible for use with `ComparisonPrompts`).
    is_starred : bool
        Whether the LLM blueprint is starred.
    playground_id : str
        The ID of the playground associated with the LLM blueprint.
    llm_id : str or None
        The ID of the LLM type. If not None, this must be one of the IDs returned by `LLMDefinition.list`
        for this user.
    llm_name : str or None
        The name of the LLM.
    llm_settings : dict or None
        The LLM settings for the LLM blueprint. The specific keys allowed and the
        constraints on the values are defined in the response from `LLMDefinition.list`
        but this typically has dict fields:
        - system_prompt - The system prompt that tells the LLM how to behave.
        - max_completion_length - The maximum number of tokens in the completion.
        - temperature - Controls the variability in the LLM response.
        - top_p - Whether the model considers next tokens with top_p probability mass.
        Or
        - system_prompt - The system prompt that tells the LLM how to behave.
        - validation_id - The ID of the external model LLM validation.
        - external_llm_context_size - The external LLM's context size, in tokens,
        for external model LLM blueprints.
    creation_date : str
        The date the playground was created.
    creation_user_id : str
        The ID of the user creating the playground.
    creation_user_name : str
        The name of the user creating the playground.
    last_update_date : str
        The date the playground was last updated.
    last_update_user_id : str
        The ID of the user who most recently updated the playground.
    prompt_type : PromptType
        The prompting strategy for the LLM blueprint.
        Currently supported options are listed in PromptType.
    vector_database_id : str or None
        The ID of the vector database, if any, associated with the LLM blueprint.
    vector_database_settings : VectorDatabaseSettings or None
        The settings for the vector database, if any, associated with the LLM blueprint.
    vector_database_name : str or None
        The name of the vector database associated with the LLM blueprint, if any.
    vector_database_status : str or None
        The status of the vector database, if any, associated with the LLM blueprint.
    vector_database_error_message : str or None
        The error message for the vector database, if any, associated with the LLM blueprint.
    vector_database_error_resolution : str or None
        The resolution for the vector database error, if any, associated with the LLM blueprint.
    custom_model_llm_validation_status : str or None
        The status of the custom model LLM validation if the llm_id is 'custom-model'.
    custom_model_llm_error_message : str or None
        The error message for the custom model LLM, if any.
    custom_model_llm_error_resolution : str or None
        The resolution for the custom model LLM error, if any.
    """

    _path = "api/v2/genai/llmBlueprints"

    _converter = llm_blueprint_trafaret

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        is_saved: bool,
        is_starred: bool,
        playground_id: str,
        creation_date: str,
        creation_user_id: str,
        creation_user_name: str,
        last_update_date: str,
        last_update_user_id: str,
        prompt_type: PromptType,
        llm_id: Optional[str] = None,
        llm_name: Optional[str] = None,
        llm_settings: Optional[Union[LLMSettingsCommonDict, LLMSettingsCustomModelDict]] = None,
        vector_database_id: Optional[str] = None,
        vector_database_settings: Optional[Dict[str, Any]] = None,
        vector_database_name: Optional[str] = None,
        vector_database_status: Optional[str] = None,
        vector_database_error_message: Optional[str] = None,
        vector_database_error_resolution: Optional[str] = None,
        custom_model_llm_validation_status: Optional[str] = None,
        custom_model_llm_error_message: Optional[str] = None,
        custom_model_llm_error_resolution: Optional[str] = None,
    ):
        super().__init__(
            id=id,
            name=name,
            description=description,
            is_saved=is_saved,
            is_starred=is_starred,
            playground_id=playground_id,
            creation_date=creation_date,
            creation_user_id=creation_user_id,
            creation_user_name=creation_user_name,
            last_update_date=last_update_date,
            last_update_user_id=last_update_user_id,
            prompt_type=prompt_type,
            llm_id=llm_id,
            llm_name=llm_name,
            llm_settings=llm_settings,
            vector_database_id=vector_database_id,
            vector_database_name=vector_database_name,
            vector_database_status=vector_database_status,
            vector_database_error_message=vector_database_error_message,
            vector_database_error_resolution=vector_database_error_resolution,
            custom_model_llm_validation_status=custom_model_llm_validation_status,
            custom_model_llm_error_message=custom_model_llm_error_message,
            custom_model_llm_error_resolution=custom_model_llm_error_resolution,
        )
        self.vector_database_settings = (
            VectorDatabaseSettings.from_server_data(vector_database_settings)
            if vector_database_settings
            else None
        )

    @classmethod
    def create(  # type: ignore[override]
        cls,
        playground: Union[Playground, str],
        name: str,
        prompt_type: PromptType = PromptType.CHAT_HISTORY_AWARE,
        description: str = "",
        llm: Optional[Union[LLMDefinition, str]] = None,
        llm_settings: Optional[Union[LLMSettingsCommonDict, LLMSettingsCustomModelDict]] = None,
        vector_database: Optional[Union[VectorDatabase, str]] = None,
        vector_database_settings: Optional[VectorDatabaseSettings] = None,
    ) -> LLMBlueprint:
        """
        Create a new LLM blueprint.

        Parameters
        ----------
        playground : Playground or str
            The playground associated with the created LLM blueprint.
            Accepts playground or playground ID.
        name : str
            The LLM blueprint name.
        prompt_type : PromptType, optional
            Prompting type of the LLM blueprint, by default PromptType.CHAT_HISTORY_AWARE.
        description : str, optional
            An optional description for the LLM blueprint, otherwise null.
        llm : LLMDefinition, str, or None, optional
            The LLM to use for the blueprint, either `LLMDefinition` or LLM ID.
        llm_settings : dict or None
            The LLM settings for the LLM blueprint. The specific keys allowed and the
            constraints on the values are defined in the response from `LLMDefinition.list`
            but this typically has dict fields:
            - system_prompt - The system prompt that tells the LLM how to behave.
            - max_completion_length - The maximum number of tokens in the completion.
            - temperature - Controls the variability in the LLM response.
            - top_p - Whether the model considers next tokens with top_p probability mass.
            Or
            - system_prompt - The system prompt that tells the LLM how to behave.
            - validation_id - The ID of the custom model LLM validation
            for custom model LLM blueprints.
        vector_database: VectorDatabase, str, or None, optional
            The vector database to use with this LLM blueprint, either
            `VectorDatabase` or vector database ID.
        vector_database_settings: VectorDatabaseSettings or None, optional
            The settings for the vector database, if any.

        Returns
        -------
        llm_blueprint : LLMBlueprint
            The created LLM blueprint.
        """
        payload = {
            "playground_id": get_entity_id(playground),
            "name": name,
            "prompt_type": prompt_type,
            "description": description,
            "llm_id": get_entity_id(llm) if llm else None,
            "llm_settings": llm_settings,
            "vector_database_id": get_entity_id(vector_database) if vector_database else None,
            "vector_database_settings": (
                vector_database_settings.to_dict() if vector_database_settings else None
            ),
        }

        url = f"{cls._client.domain}/{cls._path}/"
        r_data = cls._client.post(url, data=payload)
        return cls.from_server_data(r_data.json())

    def update(  # type: ignore[override]
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        llm: Optional[Union[LLMDefinition, str]] = None,
        llm_settings: Optional[Union[LLMSettingsCommonDict, LLMSettingsCustomModelDict]] = None,
        vector_database: Optional[Union[VectorDatabase, str]] = None,
        vector_database_settings: Optional[VectorDatabaseSettings] = None,
        is_saved: Optional[bool] = None,
        is_starred: Optional[bool] = None,
        prompt_type: Optional[PromptType] = None,
        remove_vector_database: Optional[bool] = False,
    ) -> LLMBlueprint:
        """
        Update the LLM blueprint.

        Parameters
        ----------
        name : str or None, optional
            The new name for the LLM blueprint.
        description: str or None, optional
            The new description for the LLM blueprint.
        llm: Optional[Union[LLMDefinition, str]], optional
            The new LLM type for the LLM blueprint.
        llm_settings: Optional[dict], optional
            The new LLM settings for the LLM blueprint. These must match the `LLMSettings`
            returned from the `LLMDefinition.list` method for the LLM type used for this
            LLM blueprint but this typically has dict fields:
            - system_prompt - The system prompt that tells the LLM how to behave.
            - max_completion_length - The maximum number of tokens in the completion.
            - temperature - Controls the variability in the LLM response.
            - top_p - Whether the model considers next tokens with top_p probability mass.
            Or
            - system_prompt - The system prompt that tells the LLM how to behave.
            - validation_id - The ID of the custom model LLM validation
            for custom model LLM blueprints.
        vector_database: Optional[Union[VectorDatabase, str]], optional
            The new vector database for the LLM blueprint.
        vector_database_settings: Optional[VectorDatabaseSettings], optional
            The new vector database settings for the LLM blueprint.
        is_saved: Optional[bool], optional
            The new `is_saved` attribute for the LLM blueprint (meaning the settings are locked and blueprint is eligible for use with `ComparisonPrompts`).
        is_starred: Optional[bool], optional
            The new setting for whether the LLM blueprint is starred.
        prompt_type : PromptType, optional
            The new prompting type of the LLM blueprint.
        remove_vector_database: Optional[bool], optional
            Whether to remove the vector database from the LLM blueprint.

        Returns
        -------
        llm_blueprint : LLMBlueprint
            The updated LLM blueprint.
        """
        payload = {
            "name": name,
            "description": description,
            "llm_id": get_entity_id(llm) if llm else None,
            "llm_settings": llm_settings,
            "vector_database_id": get_entity_id(vector_database) if vector_database else None,
            "vector_database_settings": (
                vector_database_settings.to_dict() if vector_database_settings else None
            ),
            "is_saved": is_saved,
            "is_starred": is_starred,
            "prompt_type": prompt_type,
        }
        url = f"{self._client.domain}/{self._path}/{self.id}/"
        json_payload = cast(Dict[str, Any], to_api(payload))
        if remove_vector_database:  # This forces the removal of the vector database.
            json_payload["vectorDatabaseId"] = None
            json_payload["vectorDatabaseSettings"] = None
        r_data = self._client.patch(url, json=json_payload)
        return self.from_server_data(r_data.json())
