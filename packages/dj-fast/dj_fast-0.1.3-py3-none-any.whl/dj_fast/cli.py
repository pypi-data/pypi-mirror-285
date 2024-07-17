import logging
import os
import secrets
import subprocess
from pathlib import Path

import click
import inquirer
import pytz
from django.core.management import execute_from_command_line
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
def init():
    env_path = os.path.join(os.getcwd(), '.env')
    env_created = os.path.exists(env_path)

    if env_created:
        click.echo('Project is already initialized.')
    else:
        click.echo('\nWelcome to DjangoFast!')
        click.echo('Let\'s get started.\n')

    project_name = click.prompt('Enter the name of your project', default='MyProject')

    if not env_created and click.confirm('Do you want to create a .env file?', default=True):
        secret_key = secrets.token_urlsafe(50)
        timezones = pytz.all_timezones
        questions = [
            inquirer.List(
                'timezone',
                message="Select your timezone",
                choices=timezones,
                default='UTC',
            ),
        ]
        answers = inquirer.prompt(questions)
        timezone = answers['timezone']
        with open(env_path, 'w') as f:
            f.write(f"PROJECT_NAME='{project_name}'\n\n")
            f.write(f"DJANGO_SECRET_KEY='{secret_key}'\n")
            f.write(f"DEBUG='True'\n")
            f.write(f"DJANGO_ENV='development'\n")
            f.write(f"TIME_ZONE='{timezone}'\n\n")
            f.write(f"AWS_ACCESS_KEY_ID=''\n")
            f.write(f"AWS_SECRET_ACCESS_KEY=''\n")
            f.write(f"AWS_STORAGE_BUCKET_NAME=''\n\n")
            f.write(f"MAILGUN_API_KEY=''\n")
            f.write(f"MAILGUN_DOMAIN=''\n\n")
            f.write(f"STRIPE_SECRET_KEY=''\n")
            f.write(f"STRIPE_PUBLIC_KEY=''\n")

        click.echo('.env file successfully created.')
        load_dotenv(dotenv_path=env_path)

    if click.confirm('Do you want to run initial migrations?', default=True):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
        execute_from_command_line(['manage.py', 'migrate'])
        click.echo('Initial migrations completed.')

    if click.confirm('Do you want to create a superuser?', default=True):
        execute_from_command_line(['manage.py', 'createsuperuser'])
        click.echo('Superuser created.')

    click.echo('Everything is set up!')


@cli.command()
@click.argument('app_name')
@click.option('-l', '--list', 'list_view', is_flag=True, help='Create a list view for the app')
@click.option('-d', '--detail', 'detail_view', is_flag=True, help='Create a detail view for the app')
def startapp(app_name, list_view, detail_view):
    app_dir = Path('apps') / app_name
    templates_dir = Path('templates') / app_name
    app_dir.mkdir(parents=True, exist_ok=True)
    templates_dir.mkdir(parents=True, exist_ok=True)
    execute_from_command_line(['django-admin', 'startapp', app_name, str(app_dir)])
    create_basic_app_files(app_name, list_view, detail_view, app_dir, templates_dir)
    update_main_urls_and_settings(app_name)
    init_and_write_app_configs(app_name, app_dir)
    click.echo(f"App {app_name} created successfully.")

    update_main_urls_and_settings(app_name)

    init_and_write_app_configs(app_name, app_dir)

    click.echo(f"App {app_name} created successfully{' with optional views and templates' if list_view or detail_view else ''}.")


def create_basic_app_files(app_name, list_view, detail_view, app_dir, templates_dir):
    urls_path = app_dir / 'urls.py'
    views_path = app_dir / 'views.py'
    urls_content = "from django.urls import path\nfrom . import views\n\nurlpatterns = [\n"
    views_content = "from django.shortcuts import render\nfrom django.views import generic\nfrom django.http import Http404\n\n"

    if list_view:
        urls_content += f"    path('', views.{app_name.capitalize()}ListView.as_view(), name='{app_name.lower()}_list'),\n"
        views_content += f"""class {app_name.capitalize()}ListView(generic.ListView):
    model = None
    template_name = '{app_name}/list.html'

    def get_queryset(self):
        return [
            {{'id': 1, 'list': True}}
        ]
"""
        list_template_path = templates_dir / "list.html"
        list_template_content = f"<h1>{app_name.capitalize()} List</h1>\n<p>Placeholder for list view.</p>"
        with open(list_template_path, 'w') as f:
            f.write(list_template_content)

    if detail_view:
        urls_content += f"    path('<int:pk>/', views.{app_name.capitalize()}DetailView.as_view(), name='{app_name.lower()}_detail'),\n"
        views_content += f"""class {app_name.capitalize()}DetailView(generic.DetailView):
    model = None
    template_name = '{app_name}/detail.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        data = [
            {{'id': 1, 'detail': True}}
        ]
        for item in data:
            if item['id'] == pk:
                return item
        raise Http404("Object does not exist")
"""
        detail_template_path = templates_dir / "detail.html"
        detail_template_content = f"<h1>{app_name.capitalize()} Detail</h1>\n<p>Placeholder for detail view.</p>"
        with open(detail_template_path, 'w') as f:
            f.write(detail_template_content)

    with open(urls_path, 'w') as f:
        f.write(urls_content + "]")
    with open(views_path, 'w') as f:
        f.write(views_content)

    if not list_view and not detail_view:
        with open(urls_path, 'w') as f:
            f.write("from django.urls import path\n\nurlpatterns = []")


def update_main_urls_and_settings(app_name):
    project_urls_path = Path('main') / 'urls.py'
    settings_file = Path('main') / 'settings' / 'base.py'
    try:
        update_urls_file(project_urls_path, app_name)
        update_settings_file(settings_file, app_name)
    except Exception as e:
        click.echo(f"Error updating configurations: {str(e)}")


def update_urls_file(urls_path, app_name):
    with open(urls_path, 'r') as file:
        lines = file.readlines()

    try:
        start_index = next(i for i, line in enumerate(lines) if 'urlpatterns' in line and '[' in line)
        end_index = next(i for i, line in enumerate(lines[start_index:], start_index) if ']' in line)
    except StopIteration:
        raise ValueError("urlpatterns declaration not found in urls.py")

    new_url = f"path('{app_name.lower()}/', include('apps.{app_name}.urls')),"
    admin_url = "path('admin/', admin.site.urls),"

    url_patterns = [line.strip() for line in lines[start_index+1:end_index] if 'path(' in line]

    if new_url not in url_patterns:
        url_patterns.append(new_url)

    if admin_url in url_patterns:
        url_patterns.remove(admin_url)

    url_patterns_sorted = sorted(url_patterns, key=lambda s: s.lower())

    if admin_url.strip() in [line.strip() for line in lines[start_index+1:end_index]]:
        url_patterns_sorted.append(admin_url.strip())

    new_urlpatterns_block = ['urlpatterns = [\n'] + [f"    {url}\n" for url in url_patterns_sorted] + [']\n']

    lines = lines[:start_index] + new_urlpatterns_block + lines[end_index+1:]

    with open(urls_path, 'w') as file:
        file.writelines(lines)

    logger.info(f"Updated urlpatterns in {urls_path} to include {app_name}.")


def update_settings_file(settings_path, app_name):
    with open(settings_path, 'r') as file:
        lines = file.readlines()

    try:
        start_index = next(i for i, line in enumerate(lines) if 'LOCAL_APPS = [' in line)
        end_index = next(i for i, line in enumerate(lines[start_index:]) if ']' in line) + start_index
    except StopIteration:
        raise Exception("LOCAL_APPS definition not found in settings.")

    new_app_config = f"    'apps.{app_name}.apps.{app_name.capitalize()}Config',\n"

    lines.insert(end_index, new_app_config)

    local_apps = sorted(set(lines[start_index + 1:end_index + 1]), key=lambda x: x.strip().lower())
    lines[start_index + 1:end_index + 1] = local_apps

    with open(settings_path, 'w') as file:
        file.writelines(lines)

    logger.info(f"Updated LOCAL_APPS in {settings_path} to include {app_name}.")


def init_and_write_app_configs(app_name, app_dir):
    init_path = app_dir / '__init__.py'
    with open(init_path, 'w') as file:
        file.write(f"default_app_config = 'apps.{app_name}.apps.{app_name.capitalize()}Config'\n")

    apps_path = app_dir / 'apps.py'
    apps_content = f"""from django.apps import AppConfig

class {app_name.capitalize()}Config(AppConfig):
    name = 'apps.{app_name}'
    verbose_name = '{app_name.capitalize()}'
"""
    with open(apps_path, 'w') as file:
        file.write(apps_content)


@cli.command()
def precommit():
    logger.info("Running isort...")
    subprocess.run(['isort', '.'], check=True)

    logger.info("Running Django tests...")
    subprocess.run(['python', 'manage.py', 'test'], check=True)


if __name__ == '__main__':
    cli()
