
from .base_tasks import BaseTask
from .supports.helper.helper import get_core_urls_path

class AutoApi:
    tasks = [{'utilities': ['permissions', 'pagination', 'importbase']}, 'serializers', 'viewsets', 'routers']

    def __init__(self, app_name):
        self.app_name = app_name
        self.main_project_urls_path = get_core_urls_path()

    def make_apis(self):
        for task in self.tasks:
            task_obj = BaseTask(self.app_name, task)
            task_obj.run()

    def app_router_register(self):
        print("registering router")
        app_router_layout = f"""\n#*********This is {self.app_name} router registered by autoapi*********\nfrom {self.app_name}.routers.routers import router as {self.app_name}_router\nurlpatterns.append(path('api/',include({self.app_name}_router.urls)))"""
        with open(self.main_project_urls_path,'a') as main_project_urls_obj:
            main_project_urls_obj.write(app_router_layout)

        return True
    
    def make_app_router(self):
        matching_import_router = f"{self.app_name}.routers"
        is_router_registered = False
        with open(self.main_project_urls_path,'r') as urls_file_obj:
            urls_data = urls_file_obj.readlines()
            for item in urls_data:
                if matching_import_router in item:
                    is_router_registered = True
        
        if not is_router_registered:
            self.app_router_register()

                
            


        


    


            

    