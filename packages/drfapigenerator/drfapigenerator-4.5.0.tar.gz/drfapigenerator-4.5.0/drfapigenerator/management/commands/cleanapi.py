from django.core.management.base import BaseCommand, CommandError
# from polls.models import Question as Poll


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("--app", nargs="+", type=str)

    def handle(self, *args, **options):
        if options.get('app'):
            for app in options["app"]:
                # raise CommandError('Poll "%s" does not exist' % poll_id)
                self.stdout.write(
                    self.style.SUCCESS('Successfully maked api for app "%s"' % app)
                )
        else:
            self.stdout.write(
                    self.style.SUCCESS("Successfully maked api ")
                )
            