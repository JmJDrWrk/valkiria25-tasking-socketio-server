from print_service import Printer

# Initialize logging and socketio
print = Printer(__file__).print

import socketio
from typing import Dict, List
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
        def task_processing_started(sid, task):
            real_task: Task = self.taskManager._task_map.get(task["task_id"])
            real_task.next_state(opt=True)# from waiting_process to processing
            pass

        @sio.event
        def task_processing_ended(sid, task):
            real_task: Task = self.taskManager._task_map.get(task["task_id"])
            real_task.next_state(opt=True) # Or false, should see
            pass

        # Step3 in response of the step 2 when send to service that he needs to tell when he is ready
        @sio.event
        def notify_ready_to_receive_payload(sid, task):

            # Get the task to be sure the client sid is up to date
            real_task: Task = self.taskManager._task_map.get(task["task_id"])
            real_task.next_state(opt=True)# assigned to waiting_upload if 

            client_token: str = real_task.token

            client_sid: str = self.sessionManager.get_session(client_token)

            sio.emit('service_is_ready_to_receive_heavy_payload', task, room=client_sid)

        # Step1 for client, step2 for same user: Make service pulls a task
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
        
            if task.has_assigned_service():
                print('FATAL ERROR: a client tryed to pull an already assigned task!...returning...')
                return
            
            task.assigned_service = token
            task.next_state(opt=True)# waiting_asignment to assigned

            print('Task assigned to service')

            task.pulled = True

            '''Check if task requires file to operate'''
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

            tasks: List[Task]= self.taskManager.get_by_token(real_task.token)
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

            tasks: List[Task] = self.taskManager.get_by_token(real_task.token)
            serialized_tasks = [
                # {"task_id": task.task_id, "client_id": task.client_id, "data": task.data}
                task.__json__()
                for task in tasks
            ]
            target_sid = self.sessionManager.get_session((real_task.token))
            print("target_sid", target_sid)
            sio.emit("your_tasks", {"tasks": serialized_tasks}, room=target_sid)
