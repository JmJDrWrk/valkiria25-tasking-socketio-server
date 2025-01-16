from print_service import Printer
# Initialize logging and socketio
print = Printer(__file__).print

import socketio
from typing import Dict
from task_manager import TaskManager, Task


class WebClients:
    def __init__(self, taskManager: TaskManager):
        self.taskManager: TaskManager = taskManager

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
            sio.emit('your_tasks', {"tasks": serialized_tasks}, room=sid)

        @sio.event
        def push_task(sid, client_identifier, task_data):

            '''
            task_data = {
                sid,
                client_identifier,
                data: raw,
                service: songsplitter
            }
            '''
            # sid = self.clients[client_identifier]

            print('Sid', sid)
            
            task = Task(client_id=client_identifier, data=task_data, last_sid=sid)

            task_identifier = self.taskManager.push_task(task)
            # Create fallback control

            print(f"Client {client_identifier} (SID: {sid}) pushed a task.")
            
            sio.emit('task_pushed', {task_identifier: task_identifier}, room=sid)
            tasks = self.taskManager.get_by_client(client_identifier)
            serialized_tasks = [
                # {"task_id": task.task_id, "client_id": task.client_id, "data": task.data}
                task.__json__()
                for task in tasks
            ]
            sio.emit('your_tasks', {"tasks": serialized_tasks}, room=sid)

        @sio.event
        def register_as_webclient(sid, client_identifier):
            """
            Registers a client with a unique identifier.
            If the client reloads the page, update their session.
            """

            if client_identifier in self.clients:
                # Update session for existing client
                print(
                    f"web client reconnected: {client_identifier} (Old SID: {self.clients[client_identifier]}, New SID: {sid})"
                )
            else:
                # Register new client
                print(f"new web client registered: {client_identifier} (SID: {sid})")

            # Map the unique client identifier to the current session ID
            self.clients[client_identifier] = sid
