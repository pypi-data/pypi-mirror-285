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
from typing import Any, cast, Dict, List

import trafaret as t

from datarobot.insights.base import BaseInsight


class ShapPreview(BaseInsight):
    """Class for SHAP Preview calculations. Use the standard methods of BaseInsight to compute and
    retrieve SHAP matrices:
    * compute: submit a request to compute a SHAP preview, and return immediately
    * create: submit a request to compute a SHAP preview, and wait for it to finish
    * list: retrieve all ShapPreview results for a model, possibly on multiple datasets or data slices.
    """

    SHAP_PREVIEW_VALUE = t.Dict(
        {
            t.Key("feature_rank"): t.Int(),
            t.Key("feature_name"): t.String(),
            t.Key("feature_value"): t.String(),
            t.Key("shap_value"): t.Float(),
        }
    ).ignore_extra("*")

    SHAP_PREVIEW_ROW = t.Dict(
        {
            t.Key("row_index"): t.Int(),
            t.Key("total_preview_features"): t.Int(),
            t.Key("prediction_value"): t.Float(),
            t.Key("preview_values"): t.List(SHAP_PREVIEW_VALUE),
        }
    )

    INSIGHT_NAME = "shapPreview"
    INSIGHT_DATA = {
        t.Key("previews_count"): t.Int(),
        t.Key("previews"): t.List(SHAP_PREVIEW_ROW),
    }

    @property
    def previews(self) -> List[Dict[str, Any]]:
        """SHAP preview values

        Returns
        -------
        preview : List[Dict[str, Any]]
            A list of the ShapPreview values for each row
        """
        return cast(List[Dict[str, Any]], self.data["previews"])

    @property
    def previews_count(self) -> int:
        """Number of shap preview rows

        Returns
        -------
        int
        """
        return cast(int, self.data["previews_count"])
