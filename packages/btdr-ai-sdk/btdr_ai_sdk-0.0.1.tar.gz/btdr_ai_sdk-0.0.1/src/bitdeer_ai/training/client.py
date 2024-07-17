from typing import Optional
import grpc
from . import training_pb2
from . import training_pb2_grpc
from .model import (
    CreateTrainingJob,
    GetTrainingJob,
    ListTrainingJobs,
    GetTrainingJobWorkers,
    GetTrainingJobLogs,
)


class TrainingClient:
    def __init__(self, host='localhost:8080', token=None):
        """
        Initializes a TrainingClient object.

        Args:
            host (str): The host address of the server. Defaults to 'localhost:8080'.
        """
        self.channel = grpc.insecure_channel(f'{host}')
        self.stub = training_pb2_grpc.TrainingServiceStub(self.channel)
        self.token = token

    def create_training_job(
        self,
        project_id: str,
        job_name: str,
        job_type: training_pb2.JobType,
        worker_spec: str,
        num_workers: int,
        worker_image: Optional[str] = None,
        commands: Optional[list] = None,
        arguments: Optional[list] = None,
        envs: Optional[list] = None,
        working_dir: Optional[str] = None,
        volume_name: Optional[str] = None,
        volume_mount_path: Optional[str] = None,
        base_image_mode: Optional[bool] = False,
        enable_image_inspection: Optional[bool] = False,
    ) -> CreateTrainingJob:
        """Create a training job.

        Args:
            project_id: The ID of the project.
            job_name: The job name of the training job.
            job_type: The type of the training job.
            worker_spec: The spec of the worker.
            num_workers: The number of workers.
            worker_image: The image of the worker.
            commands: The commands.
            arguments: The arguments.
            envs: The environment variables.
            working_dir: The working directory.
            volume_name: The name of the volume.
            volume_mount_path: The path of the volume mount.
            base_image_mode: The base image mode.
            enable_image_inspection: The enable image inspection.

        Returns:
            training_job_id: The ID of the created training job.

        Raises:
            ValueError: Job type is invalid.
            TimeoutError: Timeout to create Training Job.
            RuntimeError: Failed to create Training Job.
        """
        metadata = [('x-api-key', f'{self.token}')]
        request = training_pb2.CreateTrainingJobRequest(
            project_id=project_id,
            job_name=job_name,
            job_type=job_type,
            worker_spec=worker_spec,
            num_workers=num_workers,
            worker_image=worker_image,
            commands=commands,
            arguments=arguments,
            envs=envs,
            working_dir=working_dir,
            volume_name=volume_name,
            volume_mount_path=volume_mount_path,
            base_image_mode=base_image_mode,
            enable_image_inspection=enable_image_inspection,
        )
        response = self.stub.CreateTrainingJob(request, metadata=metadata)
        res = CreateTrainingJob.from_pb(response)
        return res    
    

    def get_training_job(self, training_job_id) -> GetTrainingJob:
        """Get a training job.

        Args:
            training_job_id: The ID of the training job.

        Returns:
            project_id: The ID of the project.
            job_name: The display name of the training job.
            job_type: The type of the training job.
            num_workers: The number of workers.
            worker_image: The image of the worker.
            args: The arguments.
            volume_name: The name of the volume.
            volume_mount_path: The path of the volume mount.
            created_at: The creation time of the training job.
        """
        metadata = [('x-api-key', f'{self.token}')]
        request = training_pb2.GetTrainingJobRequest(training_job_id=training_job_id)
        response = self.stub.GetTrainingJob(request, metadata=metadata)
        res = GetTrainingJob.from_pb(response)
        return res
    
    def list_training_jobs(self) -> ListTrainingJobs:
        """List training jobs.

        Returns:
            training_jobs: The list of training jobs.
        """
        metadata = [('x-api-key', f'{self.token}')]
        request = training_pb2.ListTrainingJobsRequest()
        response = self.stub.ListTrainingJobs(request, metadata=metadata)
        res = ListTrainingJobs.from_pb(response)
        return res
    
    def delete_training_job(self, training_job_id):
        """Delete a training job.

        Args:
            training_job_id: The ID of the training job.

        Raises:
            TimeoutError: Timeout to delete Training Job.
            RuntimeError: Failed to delete Training Job.
        """
        metadata = [('x-api-key', f'{self.token}')]
        request = training_pb2.DeleteTrainingJobRequest(training_job_id=training_job_id)
        response = self.stub.DeleteTrainingJob(request, metadata=metadata)
        return response
    
    def resume_training_job(self, training_job_id):
        """Resume a training job.
        
        Args:
            training_job_id: The ID of the training job.
        """
        metadata = [('x-api-key', f'{self.token}')]
        request = training_pb2.ResumeTrainingJobRequest(training_job_id=training_job_id)
        response = self.stub.ResumeTrainingJob(request, metadata=metadata)
        return response

    def suspend_training_job(self, training_job_id):
        """Suspend a training job.

        Args:
            training_job_id: The ID of the training job.
        """
        metadata = [('x-api-key', f'{self.token}')]
        request = training_pb2.SuspendTrainingJobRequest(training_job_id=training_job_id)
        response = self.stub.SuspendTrainingJob(request, metadata=metadata)
        return response

    def get_training_job_workers(self, training_job_id) -> GetTrainingJobWorkers:
        """Get workers of a training job.

        Args:
            training_job_id: The ID of the training job.

        Returns:
            workers: The list of workers.
        """
        metadata = [('x-api-key', f'{self.token}')]
        request = training_pb2.GetTrainingJobWorkersRequest(training_job_id=training_job_id)
        response = self.stub.GetTrainingJobWorkers(request, metadata=metadata)
        res = GetTrainingJobWorkers.from_pb(response)
        return res
    
    def get_training_job_logs(self, training_job_id, worker_name, follow):
        """Get logs of a training job.

        Args:
            training_job_id: The ID of the training job.

        Returns:
            logs: The list of logs.
        """
        metadata = [('x-api-key', f'{self.token}')]
        request = training_pb2.GetTrainingJobLogsRequest(training_job_id=training_job_id, worker_name=worker_name, follow=follow)
        response = self.stub.GetTrainingJobLogs(request, metadata=metadata)
        for log in response:
            res = GetTrainingJobLogs.from_pb(log)
            yield res