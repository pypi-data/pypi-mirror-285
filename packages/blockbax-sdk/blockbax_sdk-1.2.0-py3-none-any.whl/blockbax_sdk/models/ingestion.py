from typing import List, TypedDict

from .base import BlockbaxModel
from .type_hints import IngestionId
from .measurement import Measurement
from pydantic import PrivateAttr

import logging

logger = logging.getLogger(__name__)


class IngestionIdOverride(TypedDict):
    metric_id: IngestionId


class Ingestion(BlockbaxModel):
    ingestion_id: IngestionId
    measurements: List[Measurement] = []
    _measurement_count: int = PrivateAttr(default=len(measurements))
    _sorted: bool = PrivateAttr(default=False)

    def __init__(self, ingestion_id: IngestionId, measurements: List[Measurement] = []):
        super().__init__(ingestion_id=ingestion_id, measurements=measurements)
        self._measurement_count = len(self.measurements)
        self._sorted = False

    def sort(self):
        if not self._sorted:
            # If no timestamp is set it means that the measurement has to be send as soon
            # This is because the timestmap will be infered when it is received
            self.measurements.sort(key=lambda m: m.date if m.date is not None else 0)
            self._sorted = True

    def get_sorted_measurements(self) -> List[Measurement]:
        self.sort()
        return self.measurements

    def add_measurement(self, new_measurement: Measurement, sort: bool = False) -> None:
        if (
            len(self.measurements) > 0
            and new_measurement.get_data_type() != self.measurements[-1].get_data_type()
        ):
            inconsistent_use_of_data_type_error = f"Inconsistent use of data types, data type: {new_measurement.get_data_type()} does not equal data type of previous measurement added to this ingestion: {self.measurements[-1].get_data_type()}"
            raise ValueError(inconsistent_use_of_data_type_error)

        self.measurements.append(new_measurement)
        self._measurement_count += 1
        latest_measurement_date = self.measurements[-1].date
        if (
            latest_measurement_date is not None
            and new_measurement.date is not None
            and latest_measurement_date > new_measurement.date
        ):
            self._sorted = False

        if sort:
            self.sort()

    def clear(self):
        self.measurements.clear()
        self._measurement_count = 0

    def get_measurement_count(self):
        return len(self.measurements)


class IngestedSeries(BlockbaxModel):
    series: List[Ingestion]
