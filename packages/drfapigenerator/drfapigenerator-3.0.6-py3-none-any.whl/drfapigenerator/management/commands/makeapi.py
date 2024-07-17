from django.core.management.base import BaseCommand, CommandError
# from polls.models import Question as Poll
from .utilities import app_management
from .utilities.auto_api import AutoApi


class Command(BaseCommand):
    help = "Automatically generate API components for specified apps"

    def add_arguments(self, parser):
        parser.add_argument("--app", nargs="+", type=str, help="Specify app names to generate APIs for")

    def handle(self, *args, **options):
        all_apps = app_management.get_custom_apps()
        if options.get('app'):
            for app in options["app"]:
                if app in all_apps:
                    auto_api_obj = AutoApi(app)
                    auto_api_obj.make_apis()
                    auto_api_obj.make_app_router()
                    self.stdout.write(self.style.SUCCESS(f'Successfully made API for app "{app}"'))
                else:
                    raise CommandError(f'{app} does not exist!')
        else:
            self.stdout.write(self.style.WARNING("No apps specified. Provide app names with --app"))
