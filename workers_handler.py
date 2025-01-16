from print_service import Printer

# Initialize logging and socketio
print = Printer(__file__).print

import socketio
from typing import Dict
from task_manager import TaskManager, Task
from session_manager import SessionManager
from client import UnbalancedService, WebClient


class RemoteLocalClients:
    def __init__(self, sessionManager: SessionManager, taskManager: TaskManager):
        self.taskManager: TaskManager = taskManager
        self.sessionManager: SessionManager = sessionManager

        self.clients: Dict[str, str] = {}

    def forward(self, sio: socketio.Server):


        @sio.event
        def notify_ready_to_receive_payload(sid, task):

            # Get the task to be sure the client sid is up to date
            real_task: Task = self.taskManager._task_map.get(task["task_id"])

            client_token: str = real_task.token

            client_sid: str = self.sessionManager.get_session(client_token)

            sio.emit('service_is_ready_to_receive_heavy_payload', task, room=client_sid)

        @sio.event
        def pull_task(sid, task_identifier: str):
            # TODO: Check it is a worker and in client make the opposite

            token: str = self.sessionManager.get_session_by_sid(sid)
            # Even if there is a worker between, this method should only be accesed by a service
            client: UnbalancedService = UnbalancedService(
                **self.sessionManager.authenticationService.decrypt_token_to_json(token)
            )

            # Return first from the non pulled tasks
            task: Task = self.taskManager.pull_task(task_identifier)

            if not task:
                print('Not any task!')
                return False
        
            task.assigned_service = token
            print('Task assigned to service')

            task.pulled = True

            if task.task_type == 'heavy_load':
                print('This pulled task is "heavy_load"')
                print('Notify service to receive heavy-load')
                sio.emit("prepare_for_heavy_load", task.__json__(), room=sid)
            
            elif task.task_type == 'standard':
                print('Sending standard task to be processed')
                sio.emit("begin_process", task.__json__(), room=sid)

            

        @sio.event
        def update_task(sid, task):
            print("task", task)
            real_task: Task = self.taskManager._task_map.get(task["task_id"])
            print("real_task", real_task.__json__())
            real_task.progress = task["progress"]

            tasks = self.taskManager.get_by_token(real_task.token)
            serialized_tasks = [
                # {"task_id": task.task_id, "client_id": task.client_id, "data": task.data}
                task.__json__()
                for task in tasks
            ]
            target_sid = self.sessionManager.get_session((real_task.token))
            print("target_sid", target_sid)
            sio.emit("your_tasks", {"tasks": serialized_tasks}, room=target_sid)

        @sio.event
        def task_ended(sid, task):
            print("task", task)
            real_task: Task = self.taskManager._task_map.get(task["task_id"])
            print("real_task", real_task.__json__())

            real_task.processed = task["processed"]
            real_task.state = task["state"]
            # TODO: change for like and advice of that there are changes

            tasks = self.taskManager.get_by_token(real_task.token)
            serialized_tasks = [
                # {"task_id": task.task_id, "client_id": task.client_id, "data": task.data}
                task.__json__()
                for task in tasks
            ]
            target_sid = self.sessionManager.get_session((real_task.token))
            print("target_sid", target_sid)
            sio.emit("your_tasks", {"tasks": serialized_tasks}, room=target_sid)
