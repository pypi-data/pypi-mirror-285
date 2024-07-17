from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ViewSet
from django.apps import apps
from importlib import import_module
import os
from django.conf import settings

def get_mainapp():
    settings_app = str(settings.SETTINGS_MODULE).split('.')[0]
    return settings_app
    
def getRouters():
    settings_app = get_mainapp()
    if settings_app:
        main_app = import_module(f'{settings_app}.routers')
        return main_app.getRouters()
    
def get_core_urls_path():
    settings_app = get_mainapp()
    if settings_app:
        main_app_urls = os.path.join(settings_app,'urls.py')
        return main_app_urls
      

class ViewSetsHelper:
    def __init__(self,app_name,model_name) -> None:
        self.app_name = app_name
        self.model_name = model_name
        pass
        # self.app_name = app_name
        # self.model_name = model_name
        
    def find_viewsets_for_model(self):
        app_config = apps.get_app_config(self.app_name)
        model = app_config.get_model(str(self.model_name))
        
        registered_viewsets = []
        serializers_for_model = {}  # Define serializers_for_model dictionary

        router = getRouters()
        # Iterate over the registered viewsets in the router
        for prefix, viewset, basename in router.registry:
            if hasattr(viewset, 'queryset') and viewset.queryset.model == model:
                registered_viewsets.append((prefix, viewset, basename))

                # Check if the viewset has a serializer class
                if hasattr(viewset, 'serializer_class'):
                  
                    serializer_class = viewset.serializer_class
                    serializers_for_model = {
                        viewset.__name__ : serializer_class
                    }
                    
        
        return registered_viewsets
    
    
    

