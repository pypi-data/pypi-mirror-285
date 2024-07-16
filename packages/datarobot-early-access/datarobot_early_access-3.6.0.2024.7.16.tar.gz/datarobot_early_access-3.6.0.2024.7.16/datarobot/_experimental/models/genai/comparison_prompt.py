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

from mypy_extensions import TypedDict
import trafaret as t

from datarobot._experimental.models.genai.chat_prompt import (
    Citation,
    citation_trafaret,
    confidence_scores_trafaret,
    feedback_metadata_trafaret,
    FeedbackMetadata,
    FeedbackMetadataDict,
    result_metadata_trafaret,
)
from datarobot.models.api_object import APIObject
from datarobot.models.genai.comparison_prompt import (
    ComparisonPromptResult as BaseComparisonPromptResult,
)
from datarobot.models.genai.comparison_prompt import ComparisonPrompt as BaseComparisonPrompt
from datarobot.models.genai.comparison_prompt import _get_genai_entity_id
from datarobot.models.genai.llm_blueprint import LLMBlueprint
from datarobot.utils.waiters import wait_for_async_resolution

comparison_prompt_result_trafaret = t.Dict(
    {
        t.Key("id"): t.String,
        t.Key("llm_blueprint_id"): t.String,
        t.Key("result_metadata", optional=True): t.Or(result_metadata_trafaret, t.Null),
        t.Key("result_text", optional=True): t.Or(t.String, t.Null),
        t.Key("confidence_scores", optional=True): t.Or(confidence_scores_trafaret, t.Null),
        t.Key("citations"): t.List(citation_trafaret),
        t.Key("execution_status"): t.String,
        t.Key("chat_context_id", optional=True): t.Or(t.String, t.Null),
        t.Key("comparison_prompt_result_ids_included_in_history", optional=True): t.Or(
            t.List(t.String), t.Null
        ),
    }
).ignore_extra("*")

comparison_prompt_trafaret = t.Dict(
    {
        t.Key("id"): t.String,
        t.Key("text"): t.String,
        t.Key("results"): t.List(comparison_prompt_result_trafaret),
        t.Key("creation_date"): t.String,
        t.Key("creation_user_id"): t.String,
        t.Key("comparison_chat_id", optional=True): t.Or(t.String, t.Null),
        t.Key("metadata_filter", optional=True): t.Or(t.Dict, t.Null),
    }
).ignore_extra("*")


class FeedbackResultDict(TypedDict):
    comparison_prompt_result_id: str
    feedback_metadata: FeedbackMetadataDict


feedback_result_trafaret = t.Dict(
    {
        t.Key("comparison_prompt_result_id"): t.String,
        t.Key("feedback_metadata"): feedback_metadata_trafaret,
    }
).ignore_extra("*")


class FeedbackResult(APIObject):
    """
    Feedback associated with a comparison prompt result.

    Attributes
    ----------
    comparison_prompt_result_id : str
        The ID of the comparison prompt result associated with the feedback.
    feedback_metadata : FeedbackMetadata
        The metadata for the feedback.
    """

    _converter = feedback_result_trafaret

    def __init__(self, comparison_prompt_result_id: str, feedback_metadata: FeedbackMetadata):
        self.comparison_prompt_result_id = comparison_prompt_result_id
        self.feedback_metadata = feedback_metadata

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(comparison_prompt_result_id={self.comparison_prompt_result_id},"
            f"feedback_metadata={self.feedback_metadata})"
        )

    def to_dict(self) -> FeedbackResultDict:
        return {
            "comparison_prompt_result_id": self.comparison_prompt_result_id,
            "feedback_metadata": self.feedback_metadata.to_dict(),
        }


class ComparisonPromptResult(BaseComparisonPromptResult):
    """
    Metadata for a DataRobot GenAI comparison prompt result.

    Attributes
    ----------
    id: str
        The ID of the comparison prompt result.
    llm_blueprint_id : str
        The ID of the LLM blueprint associated with the chat prompt.
    result_metadata : ResultMetadata or None
        Metadata for the result of the chat prompt submission.
    result_text: str or None
        The result text from the chat prompt submission.
    confidence_scores: ConfidenceScores or None
        The confidence scores if there is a vector database associated with the chat prompt.
    citations: list[Citation]
        List of citations from text retrieved from the vector database, if any.
    execution_status: str
        The execution status of the chat prompt.
    chat_context_id: Optional[str], optional
        The ID of the chat context for this comparison prompt result.
    comparison_prompt_result_ids_included_in_history: Optional[List[str]], optional
        The IDs of the comparison prompt results included in the chat history for this
        comparison prompt result.
    """

    _converter = comparison_prompt_result_trafaret

    def __init__(
        self,
        id: str,
        llm_blueprint_id: str,
        citations: List[Dict[str, Any]],
        execution_status: str,
        result_metadata: Optional[Dict[str, Any]] = None,
        result_text: Optional[str] = None,
        confidence_scores: Optional[Dict[str, float]] = None,
        chat_context_id: Optional[str] = None,
        comparison_prompt_result_ids_included_in_history: Optional[List[str]] = None,
    ):
        super().__init__(
            id=id,
            llm_blueprint_id=llm_blueprint_id,
            citations=citations,
            execution_status=execution_status,
            result_metadata=result_metadata,
            result_text=result_text,
            confidence_scores=confidence_scores,
            chat_context_id=chat_context_id,
            comparison_prompt_result_ids_included_in_history=comparison_prompt_result_ids_included_in_history,
        )
        self.citations = [Citation.from_server_data(citation) for citation in citations]


class ComparisonPrompt(BaseComparisonPrompt):
    """
    Metadata for a DataRobot GenAI comparison prompt.

    Attributes
    ----------
    id : str
        Comparison prompt ID.
    text : str
        The prompt text.
    results : list[ComparisonPromptResult]
        The list of results for individual LLM blueprints that are part of the comparison prompt.
    creation_date : str
        The date when the playground was created.
    creation_user_id : str
        ID of the creating user.
    comparison_chat_id : str
        The ID of the comparison chat this comparison prompt is associated with.
    metadata_filter: Optional[Dict[str, Any] | None]
        The metadata filter for the chat prompt.
    """

    _converter = comparison_prompt_trafaret

    def __init__(
        self,
        id: str,
        text: str,
        results: List[Dict[str, Any]],
        creation_date: str,
        creation_user_id: str,
        comparison_chat_id: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            id=id,
            text=text,
            results=results,
            creation_date=creation_date,
            creation_user_id=creation_user_id,
            comparison_chat_id=comparison_chat_id,
        )
        self.results = [ComparisonPromptResult.from_server_data(result) for result in results]
        self.metadata_filter = metadata_filter

    def update(
        self,
        additional_llm_blueprints: Optional[List[Union[LLMBlueprint, str]]] = None,
        wait_for_completion: bool = False,
        feedback_result: Optional[FeedbackResult] = None,
        **kwargs: Any,
    ) -> ComparisonPrompt:
        """
        Update the comparison prompt.

        Parameters
        ----------
        additional_llm_blueprints : list[LLMBlueprint or str]
            The additional LLM blueprints you want to submit the comparison prompt.

        Returns
        -------
        comparison_prompt : ComparisonPrompt
            The updated comparison prompt.
        """
        payload = {
            "additionalLLMBlueprintIds": (
                [_get_genai_entity_id(bp) for bp in additional_llm_blueprints]
                if additional_llm_blueprints
                else None
            ),
            "feedbackResult": feedback_result.to_dict() if feedback_result else None,
        }
        url = f"{self._client.domain}/{self._path}/{_get_genai_entity_id(self.id)}/"
        r_data = self._client.patch(url, data=payload)
        if wait_for_completion and additional_llm_blueprints:
            # If no additional_llm_blueprints then we get no location header
            location = wait_for_async_resolution(self._client, r_data.headers["Location"])
            return self.from_location(location)
        else:
            # Update route returns empty string so we need to GET here
            r_data = self._client.get(url)
            return self.from_server_data(r_data.json())
