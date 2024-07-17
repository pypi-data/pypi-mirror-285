# DjangoFast

DjangoFast is your all-in-one Django toolkit, designed to get you up and running with minimal fuss. If you're tired of repetitive setups and just want to start building, you've come to the right place.

## Getting Started

These instructions will guide you through setting up and running DjangoFast on your local machine. Let's keep it simple and straightforward.

### Prerequisites

Make sure you have these installed:

- Python 3.8+
- [Poetry](https://python-poetry.org/)

### Installation

1. **Clone the repository**:

    ```bash
    git clone your_repository_url
    cd djangofast
    ```

2. **Install dependencies using Poetry**:

    ```bash
    poetry install
    ```

3. **Activate the virtual environment**:

    ```bash
    poetry shell
    ```

### CLI Commands

DjangoFast comes with a few handy CLI commands. Here's what you need to know:

#### Initialize a New Project

To kick off a new DjangoFast project, just run:

```bash
python djangofast.py init
```

This command does a lot for you:

- Prompts you for the project name.
- Creates a `.env` file with the necessary environment variables.
- Runs initial migrations.
- Optionally creates a superuser.

**Steps Involved**:

1. The script checks if a `.env` file already exists.
2. If not, it prompts you to enter the project name and other configuration details like timezone.
3. It generates a `.env` file with the specified configurations.
4. Runs Django migrations to set up the database schema.
5. Optionally creates a Django superuser.

#### Create a New App with Optional Views

To create a new Django app with optional list and detail views, use the `startapp` command:

python djangofast.py startapp <app_name> --list --detail

Replace `<app_name>` with the name of your app. The optional `--list` and `--detail` flags create list and detail views, respectively.

**Steps Involved**:

1. Creates the app directory under `apps/<app_name>`.
2. Creates a corresponding templates directory under `templates/<app_name>`.
3. Generates basic files for the app, including `views.py`, `urls.py`, and optional templates for list and detail views.
4. Updates the main project's `urls.py` and settings to include the new app.

#### Precommit Checks

To run precommit checks, which include sorting imports with `isort` and running Django tests, use the `precommit` command:

python djangofast.py precommit

This command will:

- Run `isort` to automatically sort your imports.
- Run Django tests to ensure everything is working correctly.

### How It Works

**Initialization (`init`)**:

- Prompts the user for initial setup information.
- Creates and configures the project environment.
- Sets up the database and superuser.

**Start App (`startapp`)**:

- Automates the creation of a new Django app.
- Generates necessary files and directories.
- Adds basic views and templates if specified.

**Precommit (`precommit`)**:

- Ensures code quality and correctness by sorting imports and running tests.

### Example Usage

**Initialize the Project**:

python djangofast.py init

**Create a New App**:

python djangofast.py startapp myapp --list --detail

**Run Precommit Checks**:

python djangofast.py precommit

### Additional Information

**Project Structure**:

- `apps/`: Contains all the Django apps for the project.
- `templates/`: Contains the templates for each app.
- `main/`: Contains the main project settings and configuration files.

**Configuration**:

- The `.env` file stores environment-specific settings.
- Use `dotenv` to load environment variables from the `.env` file.

This setup provides a streamlined way to manage your Django projects, ensuring consistency and reducing the overhead of repetitive tasks.
