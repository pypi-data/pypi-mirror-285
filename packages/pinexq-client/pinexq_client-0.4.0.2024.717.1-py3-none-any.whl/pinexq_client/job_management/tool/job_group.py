from typing import Union, Self

import httpx

from pinexq_client.job_management import Job
from pinexq_client.job_management.hcos import JobQueryResultHco
from pinexq_client.job_management.model import JobStates


class JobGroup:
	"""
	A wrapper class for a group of jobs for easier execution and waiting

	Attributes:
		_client:
			The http client
		_jobs:
			List of jobs in the group
	"""

	_client: httpx.Client

	def __init__(self, client: httpx.Client):
		self._jobs: list[Job] = []
		self._client = client

	@classmethod
	def from_query_result(cls, client: httpx.Client, job_query_result: JobQueryResultHco) -> Self:
		"""
		Initializes a `JobGroup` object from a JobQueryResultHco object
		Args:
			client: The http client
			job_query_result: The JobQueryResultHco object whose jobs are to be added to the JobGroup

		Returns:
			The newly created `JobGroup` instance
		"""
		instance = cls(client)
		for job in job_query_result.iter_flat():
			instance.add_jobs(Job.from_hco(instance._client, job))
		return instance

	def add_jobs(self, jobs: Union[Job, list[Job]]) -> Self:
		"""
		Add a job or multiple jobs to the group

		Args:
			jobs: A job or a list of job objects to be added to the JobGroup

		Returns:
			This `JobGroup` object
		"""

		if isinstance(jobs, list):
			self._jobs.extend(jobs)
		else:
			self._jobs.append(jobs)
		return self

	def start_all(self) -> Self:
		"""
		Start all jobs

		Returns:
			This `JobGroup` object
		"""
		for job in self._jobs:
			job.start()
		return self

	def wait_all(self, timeout_ms: int | None = None) -> Self:
		"""
		Wait for all jobs to complete

		Args:
			timeout_ms:
				Timeout in milliseconds
		Returns:
			This `JobGroup` object
		"""
		for job in self._jobs:
			try:
				if timeout_ms is None:
					job.wait_for_state(JobStates.completed)
				else:
					job.wait_for_state(JobStates.completed, timeout_ms=timeout_ms)
				job.refresh()
			except Exception:
				pass
		return self

	def incomplete_job_count(self) -> int:
		"""
		Returns the count of incomplete jobs

		Returns:
			Count of incomplete jobs
		"""
		return sum(1 for job in self._jobs if job.get_state() == JobStates.processing or JobStates.pending)

	def jobs_with_error(self) -> list[Job]:
		"""
		Returns the list of jobs that produced errors

		Returns:
			List of jobs that produced errors
		"""
		return [job for job in self._jobs if job.get_state() == JobStates.error]

	def remove(self, job_name: str) -> Self:
		"""
		Removes all jobs from the group whose name matches the provided name

		Args:
			job_name:
				The name of the job(s) to be removed
		Returns:
			This `JobGroup` object
		"""
		self._jobs = [job for job in self._jobs if job.get_name() != job_name]
		return self

	def clear(self) -> Self:
		"""
		Removes all jobs from the group

		Returns:
			This `JobGroup` object
		"""
		self._jobs = []
		return self

	def get_jobs(self) -> list[Job]:
		"""
		Returns the list of jobs in the group

		Returns:
			List of jobs in the group
		"""
		return self._jobs
