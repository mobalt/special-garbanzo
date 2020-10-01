import copy

from prunner import loaders
from prunner.tasks import STANDARD_TASKS


class Executioner:
    def __init__(
        self, config_dir, variables, dryrun=False, verbose=False, tasks=STANDARD_TASKS
    ):
        self.variables = {
            "PRUNNER_CONFIG_DIR": config_dir,
            "DRYRUN": dryrun,
            "VERBOSE": verbose,
            **variables,
        }
        yaml_file = f"{config_dir}/pipelines.yaml"
        self.pipeline_loader = loaders.YamlLoader(yaml_file)

        self.tasks = {}
        self.add_tasks(tasks)

    def add_tasks(self, tasks):
        for task in tasks:
            task_instance = task.from_settings(self.variables)
            self.tasks[task.task_name()] = task_instance

    def execute_pipeline(self, pipeline_name):
        self.variables["PIPELINE_NAME"] = pipeline_name
        pipeline = self.pipeline_loader.get_section(pipeline_name)

        for i, task in enumerate(pipeline):
            task: dict = copy.deepcopy(task)
            task_name, task_value = task.popitem()

            if task_name not in self.tasks:
                raise Exception("That task is not available: ", task_name)

            print("-" * 80)
            if type(task_value) == str:
                print(f"Task {i}: {task_name} = {task_value}")
            else:
                print(f"Task {i}: {task_name}\n{task_value}")

            updates = self.tasks[task_name].execute(task_value, self.variables)
            if updates is None or type(updates) != dict:
                updates = {}
            if self.variables["VERBOSE"]:
                new_variables = {
                    k: v for k, v in updates.items() if k not in self.variables
                }
                mutations = {k: v for k, v in updates.items() if k in self.variables}
                print("Mutations = ", mutations)
                print("New Values = ", new_variables)
            self.variables = {
                **self.variables,
                **updates,
            }
