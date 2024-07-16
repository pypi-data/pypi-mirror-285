import logging
from sws_api_client.sws_api_client import SwsApiClient
from dataclasses import (dataclass, asdict)
from typing import List, Dict, Optional, Literal
import json
import time
logger = logging.getLogger(__name__)


@dataclass
class TaskDataset:
    domain: str
    dataset: str

@dataclass
class PluginPayload:
    datasets: List[TaskDataset]
    parameters: Dict

    def to_dict(self) -> Dict:
        return asdict(self)

# fake upate

# Define Status and DetailStatus as Literal types
Status = Literal['ACTIVE', 'ARCHIVED']
DetailStatus = Literal['CREATED', 'EXECUTION_PREPARED', 'EXECUTION_PROCESSING', 'EXECUTION_PROCESSED', 'STOP_REQUESTED', 'RETRIED', 'ENDED', 'ARCHIVED']
Outcome = Literal['SUCCESS', 'FAILURE']
@dataclass
class TaskInfo:
    detail_status: DetailStatus
    ended_on: Optional[str]
    description: str
    updated_on: str
    created_on: str
    service_user: str
    tags: Dict[str, str]
    output: Dict
    input: Dict
    task_type: str
    context: str
    progress: int
    user: str
    outcome: Outcome
    group: Optional[str]
    status: Status

@dataclass
class TaskResponse:
    task_id: str
    info: TaskInfo

@dataclass
class TaskCreateResponse:
    task_id: str

class TaskManager:

    def __init__(self, sws_client: SwsApiClient, endpoint: str = 'task_manager_api') -> None:
        self.sws_client = sws_client
        self.endpoint = endpoint

    def update_current(self, progress: Optional[int] = None):
        if not self.sws_client.current_task_id:
            raise ValueError("A current task ID must be provided.")
        if not self.sws_client.current_execution_id:
            raise ValueError("A current task ID must be provided.")
        taskId = self.sws_client.current_task_id
        executionId = self.sws_client.current_execution_id

        path = f'/task/{taskId}/execution/{executionId}/status'
        data = {
            'progress': progress
        }
        self.sws_client.discoverable.put(self.endpoint, path, data=data)

    def create_plugin_task(self,
            pluginId:str,
            slow:bool,
            payload: PluginPayload,
            description: Optional[str],
            group: Optional[str] = None,
            parentTaskId: Optional[str] = None,
            user:Optional[str] = None
        ) -> TaskCreateResponse:
        
        path = 'task/create'

        data = {
            "user": user,
            "context": "IS",
            "type": "RUN_PLUGIN",
            "description": f"Run plugin {pluginId}" if description is None else description,
            "input":{
                "slow": slow,
                "pluginId": pluginId,
                "payload": payload.to_dict()
            },
            "config": {
                "repeatable":True
            },
            "parentTaskId": parentTaskId
        }

        if group:
            data['group'] = group

        response = self.sws_client.discoverable.post(self.endpoint, path, data=data)
        if response:
            return self.get_task_create_response(response)
        else:
            return None

    def get_task_response(self, task: Dict) -> TaskResponse:
        return TaskResponse(
            task_id=task['taskId'],
            info=TaskInfo(
                detail_status=task.get('info').get('detailStatus'),
                ended_on=task.get('info').get('endedOn'),
                description=task.get('info').get('description'),
                updated_on=task.get('info').get('updatedOn'),
                created_on=task.get('info').get('createdOn'),
                service_user=task.get('info').get('serviceUser'),
                tags=task.get('info').get('tags'),
                output=task.get('info').get('output'),
                input=json.loads(task.get('info').get('input', '{}')),  # Default to an empty dictionary if 'input' is missing
                task_type=task.get('info').get('taskType'),
                context=task.get('info').get('context'),
                progress=task.get('info').get('progress'),
                user=task.get('info').get('user'),
                outcome=task.get('info').get('outcome'),
                status=task.get('info').get('status'),
                group=task.get('info').get('group')
            )
        )
    
    def get_task_create_response(self, task: Dict) -> TaskCreateResponse:
        return TaskCreateResponse(
            task_id=task['taskId']
        )


    def get_task(self, task_id: str) -> Optional[TaskResponse]:
        path = f'/task/{task_id}'
        response = self.sws_client.discoverable.get(self.endpoint, path)

        if response:
            return self.get_task_response(response)
        else:
            return None

    def get_tasks_by_ids(self, task_ids: List[str]) -> List[TaskResponse]:
        path = f'/task/by-ids'
        response = self.sws_client.discoverable.post(self.endpoint, path, data={"ids":task_ids})
        # the response is an object like this: {id, data?, error?}[]
        # we need to convert the task object to a TaskResponse object and return a list of TaskResponse objects
        if response:
            return [self.get_task_response(obj.get('data')) for obj in response if obj.get('data')]
    
    def wait_completion(self, task_id: str, poll_interval: int = 10) -> TaskResponse:
        """
        Wait for a task to reach the 'ENDED' status and return the task outcome.

        Args:
            task_id (str): The ID of the task.
            poll_interval (int, optional): The interval (in seconds) between status checks. Defaults to 10.

        Returns:
            str: The final outcome of the task.
        """
        not_created_counter = 0
        while True:
            task_response = self.get_task(task_id)

            if not task_response and not_created_counter > 5:
                raise ValueError(f"Task with ID {task_id} not found.")
            elif not task_response:
                not_created_counter += 1
            else:
                not_created_counter = 0
            
                task_status = task_response.info.detail_status
                logger.info(f"Task {task_id} status: {task_status}")
                if task_status == 'ENDED':
                    return task_response

                time.sleep(poll_interval)

    def wait_completion_by_ids(self, task_ids: List[str], poll_interval: int = 10) -> List[TaskResponse]:
        """
        Wait for a list of tasks to reach the 'ENDED' status and return the task outcomes.

        Args:
            task_ids (List[str]): The IDs of the tasks.
            poll_interval (int, optional): The interval (in seconds) between status checks. Defaults to 10.

        Returns:
            List[str]: The final outcomes of the tasks.
        """
        completed_tasks = []
        while True:
            tasks_response = self.get_tasks_by_ids(task_ids)
            completed_tasks = [task for task in tasks_response if task.info.detail_status == 'ENDED']
            if len(completed_tasks) == len(task_ids):
                return completed_tasks

            time.sleep(poll_interval)
    