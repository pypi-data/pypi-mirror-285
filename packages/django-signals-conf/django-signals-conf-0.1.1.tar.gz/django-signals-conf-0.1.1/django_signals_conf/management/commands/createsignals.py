import os

from django.core.management.base import BaseCommand


example_content = '\"""For more information please see: https://docs.djangoproject.com/en/2.2/topics/signals/\n\
Example here:\n\
from django.db.models.signals import post_save\n\
from django.dispatch import receiver\n\
\n\
from .models import <ModelA>\n\
\n\
\n\
@receiver(post_save, sender=<ModelA>)\n\
def do_something(sender, instance, created, **kwargs):\n\
    pass\n\
\"""'


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--app', dest='app_label',
            help='Only look for fixtures in the specified app.',
        )

    def create_file_signals(self, app_dir):
        f_signals = os.path.join(app_dir, 'signals.py')
        with open(f_signals, "w", encoding='utf-8') as new_file:
            new_file.write(example_content)

    def update_file_init(self, app_dir):
        classname_app_config = ''.join([i.capitalize() for i in self.app_label.split('_')])
        init_file_path = os.path.join(app_dir, '__init__.py')
        with open(init_file_path, "r+") as f:
            first_char = f.read(1)
            if not first_char:
                f.write(f"default_app_config = '{self.app_label}.apps.{classname_app_config}Config'")
            else:
                print("File is NOT empty")

    def update_file_apps(self, app_dir):
        init_file_path = os.path.join(app_dir, 'apps.py')
        with open(init_file_path, "a") as f:
            f.write("\n")
            f.write("    def ready(self):\n")
            f.write("        from . import signals")
            f.close()

    def handle(self, *args, **options):
        self.app_label = options['app_label']
        self.validate_app_exists()
        app_dir = os.path.join(os.getcwd(), self.app_label)
        self.create_file_signals(app_dir)
        self.update_file_init(app_dir)
        self.update_file_apps(app_dir)
        print('done')

    def validate_app_exists(self):
        if not os.path.exists(os.path.join(os.getcwd(), self.app_label)):
            raise FileNotFoundError(f"{self.app_label} doesn't exist")
