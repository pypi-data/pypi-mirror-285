import os
from django.core.management.base import BaseCommand, CommandError
from .helper.helper import ViewSetsHelper
import importlib.resources as resources
from pathlib import Path

class BaseHelper(BaseCommand):
    def __init__(self, app_name, task_type, model_name, utilities=None):
        super().__init__()
        self.app_name = app_name
        self.type = task_type
        self.model = model_name
        self.utilities = utilities
        self.file_extension = '.py'
        self.data_extension = '.txt'
        self.backup_types = ['routers']

        self.initialize_paths()
        self.initialize_names()

    def initialize_paths(self):
        if self.utilities:
            self.model_type_stru = os.path.join(self.app_name, self.utilities, f"{self.type}{self.file_extension}")
            self.model_type_data_file = os.path.join('drfapigenerator', 'management', 'commands', 'data', self.utilities, f"{self.type}{self.data_extension}")
            self.model_type_date_file_backup = os.path.join('drfapigenerator', 'management', 'commands', 'data', self.utilities, f"backup{self.data_extension}")
        else:
            self.model_type_stru = os.path.join(self.app_name, self.type, f"{self.model.lower()}_{self.type}{self.file_extension}")
            if self.type in self.backup_types:
                self.model_type_stru = os.path.join(self.app_name, self.type, f"{self.type}{self.file_extension}")
            self.model_type_data_file = os.path.join('drfapigenerator', 'management', 'commands', 'data', self.type, f"{self.type}{self.data_extension}")
            self.model_type_date_file_backup = os.path.join('drfapigenerator', 'management', 'commands', 'data', self.type, f"backup{self.data_extension}")
            self.model_type_date_file_backup_import = os.path.join('drfapigenerator', 'management', 'commands', 'data', self.type, f"import{self.data_extension}")

    def initialize_names(self):
        self.viewset_name = f"{self.model.lower()}Viewsets"
        self.model_serializer = f"{self.model.lower()}_serializers"
        self.list_serializer = f"{self.model}ListSerializers"
        self.retrieve_serializer = f"{self.model}RetrieveSerializers"
        self.write_serializer = f"{self.model}WriteSerializers"
        self.model_permission_class = f"{self.model.title()}{self.type.title()}"
        self.api_endpoint = self.model.lower()
        self.router_viewset_name = f"{self.model.lower()}_viewsets"

    def read_data(self, file_path, read_or_read_lines):
        # Convert file_path to Path object
        path = Path(file_path)
        # Convert the path to a module path by replacing slashes with dots
        dir_path = '.'.join(path.parts[:-1])
        # Get the file name
        file_name = path.name
        
        try:
            with resources.open_text(dir_path, file_name) as file:
                if read_or_read_lines == 'read':
                    file_content = file.read()
                else:
                    file_content = file.readlines()
                return file_content
        except ModuleNotFoundError as e:
            print(f"Error: {e}")
            raise e

    
    def is_exists(self):
        return os.path.exists(self.model_type_stru)

    def code_exists(self):
        if os.path.exists(self.model_type_stru):
            content = self.read_data(self.model_type_stru,'read')
            if self.viewset_name in content:
                return True
        return False

    def formatter(self, base_data):
        return base_data.format(
            router_viewset_name=self.router_viewset_name,
            api_endpoint=self.api_endpoint,
            app_name=self.app_name,
            viewset_name=self.viewset_name,
            model_name=self.model,
            model_serializer=self.model_serializer,
            model_list_serializers=self.list_serializer,
            model_retrieve_serializers=self.retrieve_serializer,
            model_write_serializers=self.write_serializer,
            model_permission=self.model_permission_class,
        )

    def import_class(self):

        data = self.read_data(self.model_type_date_file_backup_import,'read')
        formatted_data = self.formatter(data)
        lines = self.read_data(self.model_type_stru,'readlines')

        with open(self.model_type_stru, 'w') as file:
            lines.insert(2, f"{formatted_data}\n")
            file.writelines(lines)

    def creatInitFile(self,dir_path):
        dir_path = os.path.dirname(dir_path)
        init_file_path = os.path.join(dir_path, '__init__.py')
        print(init_file_path)
        with open(init_file_path, 'w') as file:
            file.write('')

    def create(self):
        
        os.makedirs(os.path.dirname(self.model_type_stru), exist_ok=True)
        self.creatInitFile(self.model_type_stru)

        if self.type not in self.backup_types or not self.is_exists():
            base_data = self.read_data(self.model_type_data_file,'read')
        
        else:
           
            if self.code_exists():
                return False
            base_data = self.read_data(self.model_type_date_file_backup,'read')
            self.import_class()

        formatted_data = self.formatter(base_data)
        with open(self.model_type_stru, 'a') as file:
            file.write(formatted_data)
        
        return True

    def run(self):
        try:
            viewset_obj = ViewSetsHelper(self.app_name, self.model)
            viewsets = viewset_obj.find_viewsets_for_model()
        except:
            viewsets = None

        if viewsets:
            self.stdout.write(self.style.ERROR(f'{self.type} for model {self.model} viewset name {viewsets[1][2]} already exists!'))
        else:
            if self.is_exists() and self.type not in self.backup_types:
                self.stdout.write(self.style.ERROR(f'{self.type} for {self.model} models already exists!'))
            else:
                if self.create():
                    self.stdout.write(self.style.SUCCESS(f'{self.type} for {self.model} models created successfully!'))
