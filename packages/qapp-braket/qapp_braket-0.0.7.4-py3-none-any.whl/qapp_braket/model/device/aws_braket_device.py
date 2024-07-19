"""
    QuaO Project aws_braket_device.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from dateutil.parser import parse

from qapp_common.model.device.device import Device
from qapp_common.data.device.circuit_running_option import CircuitRunningOption
from qapp_common.enum.status.job_status import JobStatus
from qapp_common.config.logging_config import logger
from qapp_common.model.provider.provider import Provider


class AwsBraketDevice(Device):

    def __init__(self, provider: Provider,
                 device_specification: str,
                 s3_bucket_name: str,
                 s3_prefix: str):
        super().__init__(provider, device_specification)
        self.s3_folder = (s3_bucket_name, s3_prefix)

    def _produce_histogram_data(self, job_result) -> dict | None:
        logger.debug("[AwsBraketDevice] _produce_histogram_data()")

        return dict(job_result.measurement_counts)

    def _get_provider_job_id(self, job) -> str:
        logger.debug("[AwsBraketDevice] _get_provider_job_id()")

        return job.id

    def _get_job_status(self, job) -> str:
        logger.debug("[AwsBraketDevice] _get_job_status()")

        job_state = job.state()
        logger.debug("[AwsBraketDevice] job status: {0} ".format(job_state))

        if JobStatus.COMPLETED.value.__eq__(job_state):
            job_state = JobStatus.DONE.value
        return job_state

    def _calculate_execution_time(self, job_result):
        logger.debug("[AwsBraketDevice] _calculate_execution_time()")

        if "task_metadata" not in job_result:
            return

        task_metadata = job_result["task_metadata"]

        if task_metadata is None \
                or not bool(task_metadata) \
                or "createdAt" not in task_metadata \
                or "endedAt" not in task_metadata:
            return

        created_at = task_metadata["createdAt"]
        ended_at = task_metadata["endedAt"]

        if created_at is None or ended_at is None:
            return

        created_at = parse(created_at.replace("T", " ").replace("Z", ""))
        ended_at = parse(ended_at.replace("T", " ").replace("Z", ""))

        offset = ended_at - created_at

        self.execution_time = offset.total_seconds()

        logger.debug("[AwsBraketDevice] Execution time calculation was: {0} seconds"
                     .format(self.execution_time))

    def _get_job_result(self, job):
        logger.debug("[AwsBraketDevice] _get_job_result()")

        return job.result()

    def _create_job(self, circuit, options: CircuitRunningOption):
        logger.debug("[AwsBraketDevice] _create_job()")

        job = self.device.run(task_specification=circuit,
                              s3_destination_folder=self.s3_folder,
                              shots=options.shots)
        return job

    def _is_simulator(self) -> bool:
        logger.debug("[AwsBraketDevice] _is_simulator()")

        return "SIMULATOR".__eq__(self.device.type.value)
