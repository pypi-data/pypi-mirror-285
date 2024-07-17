# Overview
The Training Service Python SDK provides a simple and efficient interface for managing training jobs on a server. It allows users to create, list, get details, and manage training jobs with ease. This SDK communicates with the server using gRPC and provides a range of functionalities for handling training jobs, including creation, retrieval, listing, deletion, suspension, and resumption.

# Installation
To install the Training Service Python SDK, you can use pip:

```
pip install training-sdk
```

# Usage
## Initialization
To use the Training Service SDK, you need to initialize the TrainingClient object with the host address of target server and an API Key for authentication.

```python
from training.client import TrainingClient

# Initialize the client
client = TrainingClient(host='test-api.bitdeer.ai:80', token='api-key')
```

## Creating a Training Job
To create a training job, use the `create_training_job` method. You need to provide various parameters such as project_id, job_name, job_type, worker_spec, num_workers, and optional parameters like worker_image, working_dir, requirements_file, entry_point, args, volume_name, and volume_mount_path.

```python
from training.training_pb2 import JobType

job = client.create_training_job(
    project_id='your_project_id',
    job_name='example_job',
    job_type=JobType.YOUR_JOB_TYPE,
    worker_spec='spec_of_worker',
    num_workers=2,
    worker_image='worker_image_url',
    working_dir='/path/to/working/dir',
    requirements_file='requirements.txt',
    entry_point='main.py',
    args=['--arg1', 'value1'],
    volume_name='volume_name',
    volume_mount_path='/mount/path'
)
print(f'Training job created with ID: {job.training_job_id}')
```

## Retrieving a Training Job
To retrieve details of a specific training job, use the `get_training_job` method with the training_job_id.

```python
job = client.get_training_job(training_job_id='your_training_job_id')
print(f'Job Name: {job.job_name}')
```

## Listing Training Jobs
To list all training jobs, use the `list_training_jobs` method.

```python
jobs = client.list_training_jobs()
for job in jobs.training_jobs:
    print(f'Job ID: {job.training_job_id}, Job Name: {job.job_name}')
```

## Deleting a Training Job
To delete a specific training job, use the `delete_training_job` method with the training_job_id.

```python
client.delete_training_job(training_job_id='your_training_job_id')
print('Training job deleted successfully.')
```

## Resuming a Training Job
To resume a suspended training job, use the `resume_training_job` method with the training_job_id.

```python
client.resume_training_job(training_job_id='your_training_job_id')
print('Training job resumed successfully.')
```

## Suspending a Training Job
To suspend an active training job, use the `suspend_training_job` method with the training_job_id.

```python
client.suspend_training_job(training_job_id='your_training_job_id')
print('Training job suspended successfully.')
```

## Getting Training Job Workers
To get details of workers associated with a specific training job, use the `get_training_job_workers` method with the training_job_id.

```python
workers = client.get_training_job_workers(training_job_id='your_training_job_id')
for worker in workers.workers:
    print(f'Worker Name: {worker.name}')
```

## Getting Training Job Logs
To stream logs of a specific training job, use the `get_training_job_logs` method with the training_job_id, worker_name, and follow flag.

```python
logs = client.get_training_job_logs(training_job_id='your_training_job_id', worker_name='worker_name', follow=True)
for log in logs:
    print(log.message)
```

## Error Handling
The SDK raises various exceptions to handle errors:

- ValueError: Raised when the job type is invalid.
- TimeoutError: Raised when there is a timeout creating or deleting a training job.
- RuntimeError: Raised when there is a failure in creating or deleting a training job.

Make sure to handle these exceptions in your code to ensure smooth operation.

```python
try:
    job = client.create_training_job(
        project_id='your_project_id',
        job_name='example_job',
        job_type=training_pb2.JobType.YOUR_JOB_TYPE,
        worker_spec='spec_of_worker',
        num_workers=2
    )
except ValueError as e:
    print(f'Error: {e}')
except TimeoutError as e:
    print(f'Timeout Error: {e}')
except RuntimeError as e:
    print(f'Runtime Error: {e}')
```