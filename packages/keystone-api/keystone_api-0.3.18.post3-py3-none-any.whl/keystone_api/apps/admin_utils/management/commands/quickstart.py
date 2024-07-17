"""
A Django management command for quickly migrating/deploying a development server.

This management command streamlines development by providing a single command
to handle database migrations, static file collection, and web server deployment.

## Arguments

| Argument   | Description                                                      |
|------------|------------------------------------------------------------------|
| --static   | Collect static files                                             |
| --migrate  | Run database migrations                                          |
| --celery   | Launch a Celery worker with a Redis backend                      |
| --gunicorn | Run a web server using Gunicorn                                  |
| --all      | Launch all available services                                    |
"""

import subprocess
from argparse import ArgumentParser

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """A helper utility for quickly migrating/deploying an application instance."""

    help = __doc__

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-line arguments to the parser

        Args:
          parser: The argument parser instance
        """

        group = parser.add_argument_group('quickstart options')
        group.add_argument('--static', action='store_true', help='Collect static files.')
        group.add_argument('--migrate', action='store_true', help='Run database migrations.')
        group.add_argument('--celery', action='store_true', help='Launch a background Celery worker.')
        group.add_argument('--gunicorn', action='store_true', help='Run a web server using Gunicorn.')
        group.add_argument('--all', action='store_true', help='Launch all available services.')

    def handle(self, *args, **options) -> None:
        """Handle the command execution

        Args:
          *args: Additional positional arguments
          **options: Additional keyword arguments
        """

        # Note: `no_input=False` indicates the user should not be prompted for input

        if options['migrate'] or options['all']:
            self.stdout.write(self.style.SUCCESS('Running database migrations...'))
            call_command('migrate', no_input=False)

        if options['static'] or options['all']:
            self.stdout.write(self.style.SUCCESS('Collecting static files...'))
            call_command('collectstatic', no_input=False)

        if options['celery'] or options['all']:
            self.stdout.write(self.style.SUCCESS('Starting Celery worker...'))
            self.run_celery()

        if options['gunicorn'] or options['all']:
            self.stdout.write(self.style.SUCCESS('Starting Gunicorn server...'))
            self.run_gunicorn()

    @staticmethod
    def run_celery() -> None:
        """Start a Celery worker"""

        subprocess.Popen(['redis-server'])
        subprocess.Popen(['celery', '-A', 'keystone_api.apps.scheduler', 'worker'])
        subprocess.Popen(['celery', '-A', 'keystone_api.apps.scheduler', 'beat',
                          '--scheduler', 'django_celery_beat.schedulers:DatabaseScheduler'])

    @staticmethod
    def run_gunicorn(host: str = '0.0.0.0', port: int = 8000) -> None:
        """Start a Gunicorn server

        Args:
          host: The host to bind to
          port: The port to bind to
        """

        command = ['gunicorn', '--bind', f'{host}:{port}', 'keystone_api.main.wsgi:application']
        subprocess.run(command, check=True)
