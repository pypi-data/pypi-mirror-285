import os
from pathlib import Path

import click

from .blueprint import add_blueprint
from .filelib.all_files import GlobalFileLib
from .filelib.app import AppFileLib
from .filelib.favicon import favicon
from .filelib.flask_imp_logo import flask_imp_logo
from .filelib.head_tag_generator import head_tag_generator
from .filelib.water_css import water_css
from .helpers import Sprinkles as Sp


def init_app(
    name,
    _full: bool = False,
    _slim: bool = False,
    _minimal: bool = False,
    pyconfig: bool = False,
):
    click.echo(f"{Sp.OKGREEN}Creating App: {name}")

    cwd = Path.cwd()

    app_folder = cwd / name

    if app_folder.exists():
        click.echo(f"{Sp.FAIL}{name} folder already exists!{Sp.END}")
        click.confirm("Are you sure you want to continue?", abort=True)

    # Folders
    folders = {
        "root": app_folder,
        "extensions": app_folder / "extensions",
        "resources": app_folder / "resources",
        "resources/static": app_folder / "resources" / "static",
        "resources/templates": app_folder / "resources" / "templates",
    }

    if _minimal:
        folders.update(
            {
                "resources/static/css": app_folder / "resources" / "static" / "css",
                "resources/static/img": app_folder / "resources" / "static" / "img",
            }
        )

    if not _minimal:
        folders.update(
            {
                "resources/cli": app_folder / "resources" / "cli",
                "resources/error_handlers": app_folder / "resources" / "error_handlers",
                "resources/templates/errors": app_folder
                / "resources"
                / "templates"
                / "errors",
            }
        )

    if not _slim:
        folders.update(
            {
                "models": app_folder / "models",
                "blueprints": app_folder / "blueprints",
                "resources/context_processors": app_folder
                / "resources"
                / "context_processors",
                "resources/filters": app_folder / "resources" / "filters",
                "resources/routes": app_folder / "resources" / "routes",
            }
        )

    # Files
    files = {
        "root/__init__.py": (
            folders["root"] / "__init__.py",
            AppFileLib.init_py.format(app_name=name)
            if not _slim
            else AppFileLib.slim_init_py.format(app_name=name)
            if not _minimal
            else AppFileLib.minimal_init_py.format(app_name=name),
        ),
        "resources/static/favicon.ico": (
            folders["resources/static"] / "favicon.ico",
            favicon,
        ),
        "extensions/__init__.py": (
            folders["extensions"] / "__init__.py",
            AppFileLib.extensions_init_py
            if not _slim
            else AppFileLib.slim_extensions_init_py,
        ),
    }

    if pyconfig:
        files["root/config.py"] = (
            folders["root"] / "config.py",
            AppFileLib.default_config_py.format(secret_key=os.urandom(24).hex())
            if _full
            else AppFileLib.default_slim_config_py.format(
                secret_key=os.urandom(24).hex()
            ),
        )
    else:
        files["root/config.toml"] = (
            folders["root"] / "config.toml",
            AppFileLib.default_config_toml.format(secret_key=os.urandom(24).hex())
            if _full
            else AppFileLib.default_slim_config_toml.format(
                secret_key=os.urandom(24).hex()
            ),
        )

    if _minimal:
        files.update(
            {
                "resources/templates/index.html": (
                    folders["resources/templates"] / "index.html",
                    GlobalFileLib.minimal_templates_index_html.format(
                        head_tag=head_tag_generator(
                            no_js=True,
                        ),
                        static_path="static",
                        index_py=folders["resources"] / "index.py",
                        index_html=folders["resources/templates"] / "index.html",
                        init_py=folders["root"] / "__init__.py",
                    ),
                ),
                "resources/static/css/main.css": (
                    folders["resources/static/css"] / "water.css",
                    water_css,
                ),
                "resources/static/img/flask-imp-logo.png": (
                    folders["resources/static/img"] / "flask-imp-logo.png",
                    flask_imp_logo,
                ),
                "resources/routes.py": (
                    folders["resources"] / "routes.py",
                    GlobalFileLib.minimal_collections_routes_py,
                ),
            }
        )

    if not _minimal:
        files.update(
            {
                "resources/cli/cli.py": (
                    folders["resources/cli"] / "cli.py",
                    GlobalFileLib.collections_cli_py.format(app_name=name)
                    if not _slim
                    else GlobalFileLib.slim_collections_cli_py,
                ),
                "resources/error_handlers/error_handlers.py": (
                    folders["resources/error_handlers"] / "error_handlers.py",
                    GlobalFileLib.collections_error_handlers_py,
                ),
                "resources/templates/errors/400.html": (
                    folders["resources/templates/errors"] / "400.html",
                    GlobalFileLib.templates_errors_400_html,
                ),
                "resources/templates/errors/401.html": (
                    folders["resources/templates/errors"] / "401.html",
                    GlobalFileLib.templates_errors_401_html,
                ),
                "resources/templates/errors/403.html": (
                    folders["resources/templates/errors"] / "403.html",
                    GlobalFileLib.templates_errors_403_html,
                ),
                "resources/templates/errors/404.html": (
                    folders["resources/templates/errors"] / "404.html",
                    GlobalFileLib.templates_errors_404_html,
                ),
                "resources/templates/errors/405.html": (
                    folders["resources/templates/errors"] / "405.html",
                    GlobalFileLib.templates_errors_405_html,
                ),
                "resources/templates/errors/500.html": (
                    folders["resources/templates/errors"] / "500.html",
                    GlobalFileLib.templates_errors_500_html,
                ),
            }
        )

    if not _slim:
        files.update(
            {
                "models/__init__.py": (
                    folders["models"] / "__init__.py",
                    AppFileLib.models_init_py.format(app_name=name),
                ),
                "models/example_user_table.py": (
                    folders["models"] / "example_user_table.py",
                    AppFileLib.models_example_user_table_py,
                ),
                "resources/context_processors/context_processors.py": (
                    folders["resources/context_processors"] / "context_processors.py",
                    GlobalFileLib.collections_context_processors_py,
                ),
                "resources/filters/filters.py": (
                    folders["resources/filters"] / "filters.py",
                    GlobalFileLib.collections_filters_py,
                ),
                "resources/routes/routes.py": (
                    folders["resources/routes"] / "routes.py",
                    GlobalFileLib.collections_routes_py,
                ),
                "resources/templates/index.html": (
                    folders["resources/templates"] / "index.html",
                    GlobalFileLib.templates_index_html,
                ),
            }
        )

    # Loop create folders
    for folder, path in folders.items():
        if not path.exists():
            path.mkdir(parents=True)
            click.echo(f"{Sp.OKGREEN}App folder: {folder}, created{Sp.END}")
        else:
            click.echo(
                f"{Sp.WARNING}App folder already exists: {folder}, skipping{Sp.END}"
            )

    # Loop create files
    for file, (path, content) in files.items():
        if not path.exists():
            if (
                file == "resources/static/favicon.ico"
                or file == "resources/static/img/flask-imp-logo.png"
            ):
                path.write_bytes(bytes.fromhex(content))
                continue

            path.write_text(content, encoding="utf-8")

            click.echo(f"{Sp.OKGREEN}App file: {file}, created{Sp.END}")
        else:
            click.echo(f"{Sp.WARNING}App file already exists: {file}, skipping{Sp.END}")

    if not _minimal:
        add_blueprint(
            f"{name}/blueprints",
            "www",
            _init_app=True,
            _cwd=folders["blueprints"] if not _slim else folders["root"],
            pyconfig=pyconfig,
        )

    click.echo(" ")
    click.echo(f"{Sp.OKBLUE}==================={Sp.END}")
    click.echo(f"{Sp.OKBLUE}Flask app deployed!{Sp.END}")
    click.echo(f"{Sp.OKBLUE}==================={Sp.END}")
    click.echo(" ")
    if name == "app":
        click.echo(f"{Sp.OKBLUE}Your app has the default name of 'app'{Sp.END}")
        click.echo(f"{Sp.OKBLUE}Flask will automatically look for this!{Sp.END}")
        click.echo(f"{Sp.OKBLUE}Run: flask run --debug{Sp.END}")
    else:
        click.echo(f"{Sp.OKBLUE}Your app has the name of '{name}'{Sp.END}")
        click.echo(f"{Sp.OKBLUE}Run: flask --app {name} run --debug{Sp.END}")
    click.echo(" ")
