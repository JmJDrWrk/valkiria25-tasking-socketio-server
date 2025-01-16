# Example usage of TaskManager
from task_manager import TaskManager, Task

if __name__ == "__main__":
    task_manager = TaskManager()

    # Client pushes tasks
    task1_id = task_manager.push_task(Task(client_id="client1", data={"task": "data1"}))
    task2_id = task_manager.push_task(Task(client_id="client2", data={"task": "data2"}))
    print(f"Task 1 ID: {task1_id}")
    print(f"Task 2 ID: {task2_id}")

    # Service pulls tasks
    pulled_task = task_manager.pull_task(task1_id)
    print(f"Pulled Task: {pulled_task}")

    # Attempt to pull a non-existent task
    non_existent_task = task_manager.pull_task("invalid-id")
    print(f"Pulled Task: {non_existent_task}")
