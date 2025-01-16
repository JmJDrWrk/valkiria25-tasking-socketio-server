from print_service import Printer
# Initialize logging and socketio
print = Printer(__file__).print

from typing import List, Optional
from threading import Lock
import uuid


# Task class
class Task:
    def __init__(self, token: str, data: dict, last_sid:str='ukn', task_type:str='standard', assigned_service:str=None):
        """
        Represents a task created by a client.

        :param client_id: Unique identifier of the client that created the task.
        :param data: The payload/data associated with the task.
        """
        self.task_id = str(uuid.uuid4())  # Generate a unique task ID
        self.token = token
        self.data = data
        self.processed = False
        self.updated = False
        self.locked = False  # To lock while being modified
        self.progress = 0
        self.state = "Waiting For Being Processed"
        self.last_sid = last_sid
        self.pulled = False

        self.task_type = task_type#heavy_load/built_in_data
        self.assigned_service = assigned_service

    def __repr__(self):
        return f"Task(task_id={self.task_id}, token={self.token}, data={self.data})"

    def __json__(self):
        return {
            "task_id": self.task_id,
            "token": self.token,
            "data": self.data,
            "processed": self.processed,
            "updated": self.updated,
            "locked": self.locked,
            "progress": self.progress,
            "state": self.state,
            "pulled": self.pulled,
            "task_type": self.task_type,
            "assigned_service": self.assigned_service


        }


# TaskManager class
class TaskManager:
    def __init__(self):
        """
        Manages tasks. Allows clients to push tasks and services to pull tasks.
        """
        self._tasks: List[Task] = []  # List to store tasks
        self._task_map = {}  # Dictionary for O(1) task lookup by task_id
        self._lock = Lock()  # Ensure thread-safe operations

    def get_by_token(self, token: str) -> List[Task]:
        """
        Retrieves all tasks associated with a specific client identifier.

        :param client_identifier: The unique identifier of the client.
        :return: A list of Task instances associated with the client.
        """
        with self._lock:
            return [task for task in self._tasks if task.token == token]

    def push_task(self, task: Task) -> str:
        """
        Adds a task to the manager and returns its identifier.

        :param task: Task instance to be added.
        :return: The unique identifier of the task.
        """
        with self._lock:
            self._tasks.append(task)
            self._task_map[task.task_id] = task
            print(f"Task added: {task}")
            return task.task_id

    def pull_task(self, task_identifier: str) -> Optional[Task]:
        """
        Retrieves and removes a specific task by its identifier, unless it is locked.

        :param task_identifier: The unique identifier of the task to pull.
        :return: The Task instance if found and not locked, or None if no matching task exists or it is locked.
        """
        with self._lock:
            task: Task = self._task_map.get(task_identifier)
            if not task:
                print(f'task with id {task_identifier} not found, getting first')
                print('all tasks', self._tasks[0].__json__())
                available_tasks = [t for t in self._tasks if not t.pulled]
                
                if len(available_tasks) <= 0:
                    print('No tasks avaliable')
                    return None

                task: Task = available_tasks[0]
                print('found', task)
            
            if task:
                if task.pulled:
                    print('Task already pulled, Wait until it ends processing')
                    return None
                
                if task.locked:
                    print(
                        f"Task with ID {task_identifier} is locked and cannot be pulled."
                    )
                    return None
                # Remove from both the list and dictionary
                # self._tasks.remove(task)
                # del self._task_map[task_identifier]
                task.pulled = True
                print(f"Task pulled: {task}")
                return task
            print(f"No task found with ID: {task_identifier}")
            return None

    def __repr__(self):
        return f"TaskManager(tasks={self._tasks})"
