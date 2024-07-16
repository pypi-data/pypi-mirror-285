from typing import Dict, Iterable, List, Optional

import logging

from .ingestion import Ingestion, IngestedSeries
from .measurement import Measurement
from . import ingestions_utils


logger = logging.getLogger(__name__)


class IngestionCollection:
    __ingestions: Dict[str, Ingestion]

    def __init__(self):
        self.__ingestions = {}

    def __getitem__(self, ingestion_id: str) -> Optional[Ingestion]:
        return self.__ingestions.get(ingestion_id)

    def __setitem__(self, ingestion_id: str, ingestion: Ingestion):
        self.__ingestions[ingestion_id] = ingestion

    def __contains__(self, ingestion_id: str) -> bool:
        return ingestion_id in self.__ingestions

    def add(self, ingestion_id: str, measurement: Measurement) -> None:
        if ingestion_id not in self.__ingestions:
            self.__ingestions[ingestion_id] = Ingestion(
                ingestion_id=ingestion_id, measurements=[]
            )
        self.__ingestions[ingestion_id].add_measurement(measurement)

    def get_all_ids(self) -> List[str]:
        return list(self.__ingestions.keys())

    def create_series_to_send(
        self,
        ingestion_ids: Optional[List[str]] = None,
    ) -> Iterable[IngestedSeries]:
        ingestions_to_send: List[Ingestion] = [
            ingestion
            for ingestion_id, ingestion in self.__ingestions.items()
            if ingestion_ids is None or ingestion_id in ingestion_ids
        ]

        yield from ingestions_utils.create_series_batches(
            ingestions=ingestions_to_send,
        )

    def clear_all(self):
        for ingestion in self.__ingestions.values():
            ingestion.clear()
