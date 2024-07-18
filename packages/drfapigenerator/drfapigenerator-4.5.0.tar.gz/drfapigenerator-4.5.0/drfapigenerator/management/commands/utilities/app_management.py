from django.apps import apps
import os

def get_project_module_name():
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Navigate up until reaching the directory containing manage.py
    while not os.path.exists(os.path.join(script_dir, 'manage.py')):
        script_dir = os.path.dirname(script_dir)
    # Extract the project module name from the directory path
    project_module_name = script_dir
    return project_module_name

def get_custom_apps():
    custom_apps = []

    # Get the project's module name
    project_module_name = get_project_module_name()

    # Iterate over all installed apps
    for app_config in apps.get_app_configs():
        app_module = app_config.module
        # print(app_config.label)
        app_module_name = app_module.__name__
        if os.path.exists(os.path.join(project_module_name,app_module_name)):
            custom_apps.append(app_config.label)

    return custom_apps