from print_service import Printer
# Initialize logging and socketio
print = Printer(__file__).print
# import eventlet
import socketio

from task_manager import TaskManager, Task
import time
class LoadBalancer:

    def __init__(self, taskManager: TaskManager):
        self.taskManager = taskManager

    def process_task(self, task: Task, sio: socketio.Server):
        """
        Processes a single task. You can define the actual processing logic here.
        
        :param task: Task instance that needs to be processed.
        """
        print(f"Sending task to be processed: {task.task_id} with data: {task.data}")
        
        # # Simulate task processing with a delay (e.g., a time-consuming operation)
        # while task.progress <100:
        #     time.sleep(1)
        #     task.progress += 10
        #     print('task process:', f'{task.progress}/100', 'sid', task.last_sid)
        #     # sio.emit('updated', 'A task is being processed and progress has been updated')
        #     # eventlet.spawn(sio.emit, 'updated', 'A task is being processed and progress has been updated')
        #     # eventlet.spawn(sio.emit, 'updated', 'A task is being processed and progress has been updated', room=task.last_sid)
            
        # task.processed = True  # Mark the task as processed (or any other task state change)
        # print(f"Task {task.task_id} processed.")

    def keepProcessing(self, sio: socketio.Server):
        """
        Continuously processes tasks from the TaskManager in an infinite loop.
        """
        while True:
            # Fetch all pending tasks (this can be adjusted as needed)
            pending_tasks = [task for task in self.taskManager._tasks if not task.processed]
            
            if pending_tasks:
                for task in pending_tasks:
                    self.process_task(task, sio)  # Process the task
            else:
                print("No pending tasks to process. Waiting...")
            print('..> task will be processed now')

            time.sleep(5)