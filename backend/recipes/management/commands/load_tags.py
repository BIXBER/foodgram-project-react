import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Tag

DEFAULT_IMPORT_FOLDER_NAME = 'data'
DEFAULT_IMPORT_FILE_NAME = 'tags.csv'
DEFAULT_IMPORT_FILE_PATH = os.path.join(
    settings.BASE_DIR, DEFAULT_IMPORT_FOLDER_NAME,
)

MSG_SUCCESSFUL = 'Import completed successfully!'
MSG_UNSUCCESSFUL = 'Import failed...'
MSG_NO_CHANGES = 'No changes detected.'

ERR_FILE_NOT_EXISTS = (
    f"File with name '{DEFAULT_IMPORT_FILE_NAME}' "
    f"in folder '{DEFAULT_IMPORT_FOLDER_NAME}' is required!",
)
ERR_ARGS_FILE_NOT_EXISTS = ("There is no such file as '{}'")


class Command(BaseCommand):
    help = ("This command perform to import all tags data "
            "from CSV file into database")

    def add_arguments(self, parser):
        parser.add_argument('-f', '--filename', dest='filename',
                            default=DEFAULT_IMPORT_FILE_NAME, nargs='?',
                            type=str, help='specify file name.')

    def handle(self, *args, **options):
        PATH_TO_FILE = os.path.join(
            DEFAULT_IMPORT_FILE_PATH,
            options['filename'],
        )
        count_rows = 0
        try:
            with open(file=PATH_TO_FILE,
                      mode='r',
                      encoding='utf-8') as file:
                data = csv.reader(file)
                for row in data:
                    name, color, slug = row
                    tag, created = Tag.objects.get_or_create(
                        name=name, color=color, slug=slug,
                    )
                    if created:
                        count_rows += 1
            if count_rows == 0:
                self.stdout.write(self.style.NOTICE(MSG_NO_CHANGES))
            else:
                self.stdout.write(self.style.SUCCESS(
                    MSG_SUCCESSFUL + f' {count_rows} rows added.'
                )
                )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(MSG_UNSUCCESSFUL))
            if options['filename']:
                self.stdout.write(self.style.ERROR(
                    ERR_ARGS_FILE_NOT_EXISTS.format(options['filename'])
                )
                )
            else:
                raise CommandError(ERR_FILE_NOT_EXISTS)
