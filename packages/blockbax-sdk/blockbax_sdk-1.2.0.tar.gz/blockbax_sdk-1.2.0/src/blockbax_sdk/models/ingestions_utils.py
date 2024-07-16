from datetime import datetime
from typing_extensions import TypeAlias
from typing import Dict, Iterable, List, Optional, Tuple

from .measurement import Measurement
from .ingestion import Ingestion, IngestedSeries
from .type_hints import IngestionId, SubjectExternalId, MetricExternalId

import collections

import logging

logger = logging.getLogger(__name__)


def split_ingestion_id_into_external_ids(
    ingestion_id: IngestionId,
) -> Optional[Tuple[SubjectExternalId, MetricExternalId]]:
    if "$" not in ingestion_id:
        return None
    splits = ingestion_id.split("$")
    if len(splits) != 2:
        return None
    return splits[0], splits[1]


class Batch:
    batch: Dict[IngestionId, List[Measurement]]
    count: int

    def __init__(self) -> None:
        self.batch = collections.OrderedDict()
        self.count = 0

    def add(self, ingestion_id: IngestionId, measurement: Measurement):
        self.batch.setdefault(ingestion_id, []).append(measurement)
        self.count += 1

    def create_series_request(self) -> IngestedSeries:
        return IngestedSeries(
            series=[
                Ingestion(
                    ingestion_id=ingestion_id,
                    measurements=measurements,
                )
                for ingestion_id, measurements in self.batch.items()
            ]
        )


class Batcher:
    batches: List[Batch]
    current: Batch
    total: int

    def __init__(self) -> None:
        self.batches = []
        self.current = Batch()
        self.total = 0

    def next(self, force: bool = False) -> Iterable[IngestedSeries]:
        for batch in self.batches[:]:  # loop over a copy
            yield batch.create_series_request()
            self.batches.remove(batch)

        if self.current.count == 500 or (force and self.current.count > 0):
            yield self.current.create_series_request()
            self.current = Batch()

    def add(self, measurements: List[Tuple[IngestionId, Measurement]]):
        for ingested_measurements in measurements:
            ingestion_id, measurement = ingested_measurements
            if self.current.count == 500:
                self.batches.append(self.current)
                self.current = Batch()
            self.current.add(ingestion_id=ingestion_id, measurement=measurement)
        self.total += len(measurements)


IngestedMeasurement: TypeAlias = Tuple[IngestionId, Measurement]

SubjectGroupedMeasurements: TypeAlias = Dict[
    SubjectExternalId, List[IngestedMeasurement]
]
IngestionGroupedMeasurements: TypeAlias = List[IngestedMeasurement]

TimeGroupedIngestedMeasurements: TypeAlias = Dict[
    datetime, Tuple[SubjectGroupedMeasurements, IngestionGroupedMeasurements]
]


def create_series_batches(
    ingestions: List[Ingestion],
) -> Iterable[IngestedSeries]:
    measurements: TimeGroupedIngestedMeasurements = {}

    # sort on timestamp
    for ingestion in ingestions:
        external_id_result = split_ingestion_id_into_external_ids(
            ingestion.ingestion_id
        )
        for measurement in ingestion.measurements:
            timestamp = datetime.min  # send as soon as posible if no date is provided
            if measurement.date is not None:
                timestamp = datetime.fromtimestamp(measurement.date / 1000.0)
            measurements.setdefault(timestamp, ({}, []))

            if external_id_result is not None:
                subject_external_id, metric_external_id = external_id_result
                measurements[timestamp][0].setdefault(subject_external_id, []).append(
                    (ingestion.ingestion_id, measurement)
                )
            else:
                measurements[timestamp][1].append((ingestion.ingestion_id, measurement))

    batcher = Batcher()

    for _, ingested_measurments in collections.OrderedDict(
        sorted(measurements.items())
    ).items():
        # unpack for clarity
        (
            multi_subjects_grouped_measurements,
            ingestion_grouped_measurements,
        ) = ingested_measurments

        # Add measurements per subject to ensure that the same measurements per subject for this timestamp are ingesteed together
        for (
            _,
            subject_grouped_measurements,
        ) in multi_subjects_grouped_measurements.items():
            batcher.add(subject_grouped_measurements)

        # Add the rest of the ingestions for this timestamp
        batcher.add(ingestion_grouped_measurements)

        yield from batcher.next()

    yield from batcher.next(force=True)  # force remaining batch
