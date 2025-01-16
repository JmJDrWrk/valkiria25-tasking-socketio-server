from print_service import Printer

# Initialize logging and socketio
print = Printer(__file__).print

import json
import socketio
from typing import Dict
from task_manager import TaskManager, Task
from client import WebClient
from session_manager import SessionManager


class WebClients:
    def __init__(self, sessionManager: SessionManager, taskManager: TaskManager):
        self.taskManager: TaskManager = taskManager
        self.sessionManager: SessionManager = sessionManager
        self.clients: Dict[str, str] = {}

    def forward(self, sio: socketio.Server):

        @sio.event
        def myTasks(sid, client_identifier):
            tasks = self.taskManager.get_by_client(client_identifier)
            serialized_tasks = [
                # {"task_id": task.task_id, "client_id": task.client_id, "data": task.data}
                task.__json__()
                for task in tasks
            ]
            sio.emit("your_tasks", {"tasks": serialized_tasks}, room=sid)

        @sio.event
        def push_task(sid, task):

            token: str = self.sessionManager.get_session_by_sid(sid)

            client_as_json: dict = (
                self.sessionManager.authenticationService.decrypt_token_to_json(token)
            )
            print("loaded client_as_json", client_as_json)
            client: WebClient = WebClient(**client_as_json)

            print("loaded webclient", client.__json__())

            print('t', task)

            task = Task(token=token, data=task['task']['data'], last_sid=sid, task_type=task['task']['task_type'])

            task_identifier = self.taskManager.push_task(task)
            # Create fallback control
            # Its important to notice, that here is not possible to get decrypted info of the user, as long
            # as we only have access to the session manager but not to the auth service!!
            print(f"Client **** (SID: {sid}) pushed a task.")

            sio.emit("task_pushed", {task_identifier: task_identifier}, room=sid)
            tasks = self.taskManager.get_by_token(token)
            serialized_tasks = [
                # {"task_id": task.task_id, "client_id": task.client_id, "data": task.data}
                task.__json__()
                for task in tasks
            ]
            sio.emit("your_tasks", {"tasks": serialized_tasks}, room=sid)

        """This channel is for heavy-load-tasks"""

        @sio.event
        def push_task_data(sid, task, chunk):
            webClient: WebClient = WebClient(
                **self.sessionManager.authenticationService.decrypt_token_to_json(
                    self.sessionManager.get_session_by_sid(sid)
                )
            )
            if not webClient:
                print("webClient not valid!")
                return False

            # get real task from task_id
            real_task: Task = self.taskManager._task_map.get(task["task_id"])

            print("real_task", real_task.__json__())

            service_sid = self.sessionManager.get_session(
                    real_task.assigned_service
                )

            if not service_sid:
                print('service_sid, not found!. Maybe the service has disconnected!')
                return None

            sio.emit(
                "service_task_data_in",
                chunk,
                room=service_sid
            )
