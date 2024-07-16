#
# Copyright 2024 DataRobot, Inc. and its affiliates.
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

from datarobot._experimental.models.enums import (
    AggregationType,
    GuardConditionComparator,
    GuardType,
)
from datarobot.enums import enum_to_list
from datarobot.models.api_object import APIObject
from datarobot.models.genai.comparison_chat import get_entity_id
from datarobot.models.genai.playground import Playground
from datarobot.models.use_cases.use_case import UseCase
from datarobot.models.use_cases.utils import get_use_case_id


class InsightsConfigurationDict(TypedDict):
    """Dictionary representation of insights configuration."""

    insight_name: str
    deployment_id: Optional[str]
    model_id: Optional[str]
    sidecar_model_metric_validation_id: Optional[str]
    custom_metric_id: Optional[str]
    evaluation_dataset_configuration_id: Optional[str]
    cost_configuration_id: Optional[str]
    result_unit: Optional[str]
    guard_conditions: Optional[List[Dict[str, Any]]]
    execution_status: Optional[str]
    error_message: Optional[str]
    aggregation_types: Optional[List[str]]
    sidecar_model_metric_metadata: Optional[Dict[str, Any]]
    guard_template_id: Optional[str]
    guard_configuration_id: Optional[str]


guard_conditions = t.Dict(
    {
        t.Key("comparator"): t.Enum(*enum_to_list(GuardConditionComparator)),
        t.Key("comparand"): t.Or(t.String, t.Float, t.Bool, t.List(t.String)),
    }
).ignore_extra("*")

sidecar_model_metric_metadata = t.Dict(
    {
        t.Key("prompt_column_name", optional=True): t.Or(t.String, t.Null),
        t.Key("response_column_name", optional=True): t.Or(t.String, t.Null),
        t.Key("target_column_type", optional=True): t.Or(t.String, t.Null),
        t.Key("guard_type", optional=True): t.Or(t.Enum(*enum_to_list(GuardType)), t.Null),
    }
).ignore_extra("*")

insight_configuration_trafaret = t.Dict(
    {
        t.Key("insight_name"): t.String,
        t.Key("deployment_id", optional=True): t.Or(t.String, t.Null),
        t.Key("model_id", optional=True): t.Or(t.String, t.Null),
        t.Key("sidecar_model_metric_validation_id", optional=True): t.Or(t.String, t.Null),
        t.Key("custom_metric_id", optional=True): t.Or(t.String, t.Null),
        t.Key("evaluation_dataset_configuration_id", optional=True): t.Or(t.String, t.Null),
        t.Key("cost_configuration_id", optional=True): t.Or(t.String, t.Null),
        t.Key("result_unit", optional=True): t.Or(t.String, t.Null),
        t.Key("guard_conditions", optional=True): t.Or(t.List(guard_conditions), t.Null),
        t.Key("execution_status", optional=True): t.Or(t.String, t.Null),
        t.Key("error_message", optional=True): t.Or(t.String, t.Null),
        # additional data
        t.Key("aggregation_types", optional=True): t.Or(
            t.List(t.Enum(*enum_to_list(AggregationType))), t.Null
        ),
        t.Key("sidecar_model_metric_metadata", optional=True): t.Or(
            sidecar_model_metric_metadata, t.Null
        ),
        t.Key("guard_template_id", optional=True): t.Or(t.String, t.Null),
        t.Key("guard_configuration_id", optional=True): t.Or(t.String, t.Null),
    }
).ignore_extra("*")

insights_trafaret = t.Dict(
    {
        t.Key("playground_id"): t.String,
        t.Key("insights_configuration"): t.List(insight_configuration_trafaret),
        t.Key("creation_date"): t.String,
        t.Key("creation_user_id"): t.String,
        t.Key("last_update_date"): t.String,
        t.Key("last_update_user_id"): t.String,
        t.Key("tenant_id"): t.String,
    }
).ignore_extra("*")


class InsightsConfiguration(APIObject):
    """
    Configuration information for a specific insight.

    Attributes
    ----------
    insight_name : str
        The name of the insight.
    deployment_id : str, optional
        The deployment ID the insight is applied to.
    model_id : str, optional
        The model ID for the insight.
    sidecar_model_metric_validation_id : str, optional
        Validation ID for the sidecar model metric.
    custom_metric_id : str, optional
        The ID for a custom model metric.
    evaluation_dataset_configuration_id : str, optional
        The ID for the evaluation dataset configuration.
    cost_configuration_id : str, optional
        The ID for the cost configuration information.
    result_unit : str, optional
        The unit of the result, for example "USD".
    guard_conditions : list[dict], optional
        The guard conditions to be used with the insight.
    execution_status : str, optional
        The execution status of the insight.
    error_message : str, optional
        The error message for the insight, for example if it is missing specific configuration
        for deployed models.
    aggregation_types : list[str], optional
        The aggregation types to be used for the insight.
    sidecar_model_metric_metadata : dict, optional
        Metadata specific to sidecar model metrics.
    guard_template_id : str, optional
        The ID for the guard template that applies to the insight.
    guard_configuration_id : str, optional
        The ID for the guard configuration that applies to the insight.
    """

    _path = "api/v2/genai/insights/supportedInsights/"

    _converter = insight_configuration_trafaret

    def __init__(
        self,
        insight_name: str,
        deployment_id: Optional[str] = None,
        model_id: Optional[str] = None,
        sidecar_model_metric_validation_id: Optional[str] = None,
        custom_metric_id: Optional[str] = None,
        evaluation_dataset_configuration_id: Optional[str] = None,
        cost_configuration_id: Optional[str] = None,
        result_unit: Optional[str] = None,
        guard_conditions: Optional[List[Dict[str, Any]]] = None,
        execution_status: Optional[str] = None,
        error_message: Optional[str] = None,
        aggregation_types: Optional[List[str]] = None,
        sidecar_model_metric_metadata: Optional[Dict[str, Any]] = None,
        guard_template_id: Optional[str] = None,
        guard_configuration_id: Optional[str] = None,
    ):
        self.insight_name = insight_name
        self.deployment_id = deployment_id
        self.model_id = model_id
        self.sidecar_model_metric_validation_id = sidecar_model_metric_validation_id
        self.custom_metric_id = custom_metric_id
        self.evaluation_dataset_configuration_id = evaluation_dataset_configuration_id
        self.cost_configuration_id = cost_configuration_id
        self.result_unit = result_unit
        self.guard_conditions = guard_conditions
        self.execution_status = execution_status
        self.error_message = error_message
        self.aggregation_types = aggregation_types
        self.sidecar_model_metric_metadata = sidecar_model_metric_metadata
        self.guard_template_id = guard_template_id
        self.guard_configuration_id = guard_configuration_id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.insight_name}, model_id={self.model_id})"

    def to_dict(self) -> InsightsConfigurationDict:
        return {
            "insight_name": self.insight_name,
            "deployment_id": self.deployment_id,
            "model_id": self.model_id,
            "sidecar_model_metric_validation_id": self.sidecar_model_metric_validation_id,
            "custom_metric_id": self.custom_metric_id,
            "evaluation_dataset_configuration_id": self.evaluation_dataset_configuration_id,
            "cost_configuration_id": self.cost_configuration_id,
            "result_unit": self.result_unit,
            "guard_conditions": self.guard_conditions,
            "execution_status": self.execution_status,
            "error_message": self.error_message,
            "aggregation_types": self.aggregation_types,
            "sidecar_model_metric_metadata": self.sidecar_model_metric_metadata,
            "guard_template_id": self.guard_template_id,
            "guard_configuration_id": self.guard_configuration_id,
        }

    @classmethod
    def list(cls, use_case_id: str) -> List[InsightsConfiguration]:
        """Get a list of all supported insights that can be used within a given Use Case.

        Parameters
        ----------
        use_case_id: str
            The ID of the Use Case to list supported insights for.

        Returns
        -------
        insights: list[Insights]
            A list of supported insights.
        """
        response_data = cls._client.get(
            url=f"{cls._client.domain}/{cls._path}", params={"use_case_id": use_case_id}
        )
        return [
            cls.from_server_data(insight)
            for insight in response_data.json()["insightsConfiguration"]
        ]


class Insights(APIObject):
    """
    The insights configured for a playground.

    Attributes
    ----------
    playground_id : str
        The ID of the playground the insights are configured for.
    insights_configuration : list[InsightsConfiguration]
        The insights configuration for the playground.
    creation_date : str
        The date the insights were configured.
    creation_user_id : str
        The ID of the user who created the insights.
    last_update_date : str
        The date the insights were last updated.
    last_update_user_id : str
        The ID of the user who last updated the insights.
    tenant_id : str
        The tenant ID that applies to the record.

    """

    _path = "api/v2/genai/insights"

    _converter = insights_trafaret

    def __init__(
        self,
        playground_id: str,
        insights_configuration: List[Dict[str, Any]],
        creation_date: str,
        creation_user_id: str,
        last_update_date: str,
        last_update_user_id: str,
        tenant_id: str,
    ):
        self.playground_id = playground_id
        self.insights_configuration = [
            InsightsConfiguration.from_server_data(config) for config in insights_configuration
        ]
        self.creation_date = creation_date
        self.creation_user_Id = creation_user_id
        self.last_update_date = last_update_date
        self.last_update_user_id = last_update_user_id
        self.tenant_id = tenant_id

    @classmethod
    def get(
        cls, playground: Union[str, Playground], with_aggregation_types_only: bool = False
    ) -> Insights:
        """Get the insights configuration for a given playground.

        Parameters
        ----------
        playground: str|Playground
            The ID of the playground to get insights for.
        with_aggregation_types_only: bool, optional
            If True, only return the aggregation types for the insights.

        Returns
        -------
        insights: Insights
            The insights configuration for the playground.
        """
        playground_id = get_entity_id(playground)
        response_data = cls._client.get(
            url=f"{cls._client.domain}/{cls._path}/{playground_id}/",
            params={"with_aggreation_types_only": with_aggregation_types_only},
        )
        return cls.from_server_data(response_data.json())

    @classmethod
    def create(
        cls,
        playground: Union[str, Playground],
        insights_configuration: List[InsightsConfiguration],
        use_case: Union[UseCase, str],
    ) -> Insights:
        """Create a new insights configuration for a given playground.

        Parameters
        ----------
        playground: str
            The ID of the playground to create insights for.
        insights_configuration: list[InsightsConfiguration]
            The insights configuration for the playground.
        use_case_id: str
            The Use Case ID to the playground is a part of.

        Returns
        -------
        insights: Insights
            The created insights configuration.
        """
        playground_id = get_entity_id(playground)
        payload = {
            "playground_id": playground_id,
            "insights_configuration": [config.to_dict() for config in insights_configuration],
            "use_case_id": get_use_case_id(use_case, is_required=True),
        }

        response_data = cls._client.post(url=f"{cls._client.domain}/{cls._path}/", json=payload)
        return cls.from_server_data(response_data.json())
