# from abc import ABC, abstractmethod
from django.apps import apps
from .supports.base_exists import BaseHelper


class BaseTask:
    def __init__(self, app_name, task_type):
        self.app_name = app_name
        self.type = task_type
        self.models_list = self.extract_models()

    def run(self):
        if isinstance(self.type, str):
            for model in self.models_list:
                task = BaseHelper(self.app_name, self.type, model.__name__)
                task.run()
        elif isinstance(self.type, dict):
            for key, items in self.type.items():
                for item in items:
                    for model in self.models_list:
                        task = BaseHelper(self.app_name, item, model.__name__, key)
                        task.run()

    def extract_models(self):
        app_config = apps.get_app_config(self.app_name)
        return list(app_config.get_models())



    
        