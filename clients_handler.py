from print_service import Printer

# Initialize logging and socketio
print = Printer(__file__).print

import json
import socketio
from typing import Dict, List
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
        def my_tasks(sid):
            tasks = self.taskManager.get_by_token(self.sessionManager.get_session_by_sid(sid))
            serialized_tasks = [
                task.__json__()
                for task in tasks
            ]
            sio.emit("your_tasks", {"tasks": serialized_tasks}, room=sid)

        # Step 1: Triggered by web client: Create a task pushing its data
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
            
            task: Task = Task(token=token, data=task['task']['data'], last_sid=sid, task_type=task['task']['task_type'])
            
            task_identifier = self.taskManager.push_task(task)
            task.next_state(opt=True) # pushed-> waiting_asignment

            # Create fallback control
            # Its important to notice, that here is not possible to get decrypted info of the user, as long
            # as we only have access to the session manager but not to the auth service!!
            print(f"Client **** (SID: {sid}) pushed a task.")

            sio.emit("task_pushed", {task_identifier: task_identifier}, room=sid)
            # tasks: List[Task] = self.taskManager.get_by_token(token)
            # serialized_tasks = [
            #     # {"task_id": task.task_id, "client_id": task.client_id, "data": task.data}
            #     task.__json__()
            #     for task in tasks
            # ]
            # sio.emit("your_tasks", {"tasks": serialized_tasks}, room=sid)

        """This channel is for heavy-load-tasks"""

        @sio.event
        def end_pushing_data(sid, task):
            print('t', task)

            real_task: Task = self.taskManager._task_map.get(task['task_id'])
            real_task.next_state(opt=True)# uploading to uploaded
            real_task.next_state(opt=True)# uploaed to waiting_process
            service_token:str = real_task.assigned_service

            service_sid:str = self.sessionManager.get_session(service_token)

            print('sending file_transfer_complete event to service')
            sio.emit('file_transfer_complete', task, room=service_sid)

        # Step 5 after client receives service notification and starts uploading content
        @sio.event
        def push_task_data(sid, chunkData):
            print('pushing data')
            # print('c', chunkData)
        
            pure_task = chunkData['task']

            webClient: WebClient = WebClient(
                **self.sessionManager.authenticationService.decrypt_token_to_json(
                    self.sessionManager.get_session_by_sid(sid)
                )
            )
            if not webClient:
                print("webClient not valid!")
                return False

            # get real task from task_id
            real_task: Task = self.taskManager._task_map.get(pure_task['task_id'])

            if real_task.state == 'waiting_upload':
                real_task.next_state(opt=True)
            # real_task.progress_upload = (int(chunkData['chunkNumber'])+1)/int(chunkData['totalChunks']) * 100

            # print('new percentage', real_task.progress_upload)

            service_sid = self.sessionManager.get_session(
                    real_task.assigned_service
                )
            
            if not service_sid:
                print('service_sid, not found!. Maybe the service has disconnected!')
                return None

            sio.emit(
                "service_task_data_in",
                chunkData,
                room=service_sid
            )
        
        @sio.event
        def delete_task(sid, taskId):
            real_task: Task = self.taskManager.delete(taskId)
            print('task deleted', real_task)
            sio.emit('update_now', {}, room=sid)

        #Requiers
        @sio.event
        def retrieve_task_file(sid, task):
            real_task: Task = self.taskManager._task_map.get(task['task_id'])
            service_token:str = real_task.assigned_service
            service_sid:str = self.sessionManager.get_session(service_token)
            sio.emit('retrieve_file_from_task', task , room=service_sid)

        #NOt needed if serviceCLient updates this when finished
        # def files_for_task(sid, task):
        #     real_task: Task = self.taskManager._task_map.get(task['task_id'])
        #     service_token:str = real_task.assigned_service
        #     service_sid:str = self.sessionManager.get_session(service_token)
        #     sio.emit('webclientapi_files_for_task', task, room=...)