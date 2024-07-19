"""
    QuaO Project qapp_braket_device.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
import time

from qapp_common.model.device.device import Device
from qapp_common.data.device.circuit_running_option import CircuitRunningOption
from qapp_common.enum.status.job_status import JobStatus
from qapp_common.config.logging_config import logger
from qapp_common.model.provider.provider import Provider


class QappBraketDevice(Device):

    def __init__(self, provider: Provider, device_specification: str):
        super().__init__(provider, device_specification)

    def _create_job(self, circuit, options: CircuitRunningOption):
        logger.debug("[QappBraketDevice] _create_job()")

        start_time = time.time()

        job = self.device.run(task_specification=circuit, shots=options.shots)

        self.execution_time = time.time() - start_time

        return job

    def _produce_histogram_data(self, job_result) -> dict:
        logger.debug("[QappBraketDevice] _produce_histogram_data()")

        return dict(job_result.measurement_counts)

    def _get_provider_job_id(self, job) -> str:
        logger.debug("[QappBraketDevice] _get_provider_job_id()")

        return job.id

    def _get_job_status(self, job) -> str:
        logger.debug("[QappBraketDevice] _get_job_status()")

        job_state = job.state()
        logger.debug("[AwsBraketDevice] job status: {0} ".format(job_state))

        if JobStatus.COMPLETED.value.__eq__(job_state):
            job_state = JobStatus.DONE.value

        return job_state

    def _is_simulator(self) -> bool:
        logger.debug("[QappBraketDevice] _is_simulator()")

        return True

    def _calculate_execution_time(self, job_result):
        logger.debug("[QappBraketDevice] _is_simulator()")

        logger.debug("[QappBraketDevice] Execution time calculation was: {0} seconds"
                     .format(self.execution_time))

    def _get_job_result(self, job):
        logger.debug("[QappBraketDevice] _get_job_result()")

        return job.result()
