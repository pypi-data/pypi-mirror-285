from __future__ import annotations

from typing import TYPE_CHECKING

from vectice.autolog.asset_services.metric_service import MetricService
from vectice.autolog.model_library import ModelLibrary

if TYPE_CHECKING:
    from statsmodels.base.wrapper import ResultsWrapper


class AutologStatsModelWrapperService(MetricService):
    def __init__(self, key: str, asset: ResultsWrapper, data: dict):
        self._asset = asset
        self._key = key

        super().__init__(cell_data=data)

    def get_asset(self):
        return {
            "variable": self._key,
            "model": self._asset,
            "library": ModelLibrary.STATSMODEL,
            "metrics": self._get_statsmodels_metrics(self._asset),
        }
