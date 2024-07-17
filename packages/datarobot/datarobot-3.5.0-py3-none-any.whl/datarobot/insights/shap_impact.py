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
from typing import Any, cast, Dict, List, Optional, Union

import trafaret as t

from datarobot.enums import ENTITY_TYPES, INSIGHTS_SOURCES
from datarobot.insights.base import BaseInsight


class ShapImpact(BaseInsight):
    """Class for SHAP Impact calculations. Use the standard methods of BaseInsight to compute and
    retrieve SHAP matrices:
    * compute: submit a request to compute a SHAP impact, and return immediately
    * create: submit a request to compute a SHAP impact, and wait for it to finish
    * list: retrieve all ShapImpact results for a model, possibly on multiple datasets or data slices.
    """

    INSIGHT_NAME = "shapImpact"
    INSIGHT_DATA = {
        "shap_impacts": t.Or(
            t.List(t.List(t.Or(t.Int(), t.Float()))),
            t.Dict(
                {
                    t.Key("featureName"): t.String(),
                    t.Key("impactNormalized"): t.Float(),
                    t.Key("impactUnnormalized"): t.Float(),
                }
            ),
        ),
        "base_value": t.List(t.Float()),
        "capping": Optional[
            t.Or(
                t.Null(),
                t.Dict(
                    {
                        t.Key("right"): t.Or(t.String(), t.Float(), t.Null()),  # noqa: F821
                        t.Key("left"): t.Or(t.String(), t.Float(), t.Null()),  # noqa: F821
                    }
                ),
            )
        ],
        "link": t.Or(t.String(), t.Null()),
        "row_count": t.Int(),
    }

    @classmethod
    def _get_payload(
        cls,
        entity_id: str,
        source: str = INSIGHTS_SOURCES.TRAINING,
        data_slice_id: Optional[str] = None,
        external_dataset_id: Optional[str] = None,
        entity_type: Optional[ENTITY_TYPES] = None,
        row_count: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Union[str, int]]:
        """Construct a payload for a compute request"""
        payload = super()._get_payload(
            entity_id=entity_id,
            source=source,
            data_slice_id=data_slice_id,
            external_dataset_id=external_dataset_id,
            entity_type=entity_type,
            **kwargs,
        )

        if row_count is None:
            raise ValueError("row_count is required")
        payload["rowCount"] = row_count

        return payload

    @property
    def shap_impacts(self) -> List[List[Any]]:
        """SHAP impact values

        Returns
        -------
        shap impacts
            A list of the SHAP impact values
        """
        return cast(List[List[Any]], self.data["shap_impacts"])

    @property
    def base_value(self) -> List[float]:
        """A list of base prediction values"""
        return cast(List[float], self.data["base_value"])

    @property
    def capping(self) -> Optional[Dict[str, Any]]:
        """Capping for the models in the blender"""
        return cast(Optional[Dict[str, Any]], self.data.get("capping"))

    @property
    def link(self) -> Optional[str]:
        """Shared link function of the models in the blender"""
        return cast(Optional[str], self.data.get("link"))

    @property
    def row_count(self) -> int:
        """Number of SHAP impact rows"""
        return cast(int, self.data["row_count"])
