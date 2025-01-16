from print_service import Printer
# Initialize logging and socketio
print = Printer(__file__).print

import socketio
from typing import Dict
from task_manager import TaskManager, Task


class RemoteLocalClients:
    def __init__(self, taskManager: TaskManager):
        self.taskManager: TaskManager = taskManager

        self.clients: Dict[str, str] = {}

    def forward(self, sio: socketio.Server):

        @sio.event
        def pull_task(sid, task_identifier: str):
            task: Task = self.taskManager.pull_task(task_identifier)


        @sio.event
        def register_as_worker(sid, client_identifier):
            """
            Registers a client with a unique identifier.
            If the client reloads the page, update their session.
            """

            # Require Auth for log as worker

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
