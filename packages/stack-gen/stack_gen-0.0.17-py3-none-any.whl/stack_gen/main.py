import click
import os
import sys
import functools
from loguru import logger


logger.configure(
    handlers=[
        {
            "sink": sys.stdout,
            "colorize": True,
            "backtrace": False,
            "diagnose": True,
            "format": "{message}",
        },
    ]
)


def clean_on_fail(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logger.info("Your template is being cloned and generated...\n")
            func(*args, **kwargs)
            logger.info("Your template has been generated !\n")
        except Exception as e:
            logger.exception(e)
            os.system(f"rm -rf {kwargs['repository']}")
            exit(1)
        finally:
            os.system(f"rm -rf {kwargs['repository']}")

    return wrapper


@click.command()
@click.option(
    "repository",
    "-r",
    prompt="""Repository name containing the template to generate""",
    help="Name of the repository containing the cookicutter template",
)
@click.option(
    "--user",
    "-u",
    prompt="Github user owning the repository",
    help="Github user on which stack generator searches for template repository",
)
@click.option("--access_token", "-gac", help="GITHUB access token")
@clean_on_fail
def main(repository, user, access_token):
    exit_status = os.system(f"git clone git@github.com:{user}/{repository}.git --quiet")
    if exit_status != 0:
        raise Exception(f"Repository {repository} not found")

    if os.path.isfile(f"{repository}/requirements.txt"):
        exit_status = os.system(
            f"pip install -r {repository}/requirements.txt --quiet",
        )

    if access_token:
        with open(
            f"{repository}/app/{{{{cookiecutter.project_slug}}}}/.env", "a+"
        ) as file:
            file.write(f'\nGITHUB_ACCESS_TOKEN="{access_token}"')

    exit_status = os.system("pip install cookiecutter --quiet")
    if exit_status != 0:
        raise Exception(
            f"Error while running 'pip install cookiecutter --quiet', please check your connexion"
        )
    exit_status = os.system(f"cookiecutter {repository}/app")
    if exit_status != 0:
        raise Exception(f"Error while running 'cookiecutter {repository}/app'")


if __name__ == "__main__":
    main()
