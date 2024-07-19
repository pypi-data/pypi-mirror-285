"""Command line interface for neosctl."""

import configparser
import importlib.metadata
import logging
import os
import sys
import typing

import click
import typer
from rich.logging import RichHandler

from neosctl import (
    auth,
    constant,
    env,
    info,
    profile,
    schema,
    services,
    util,
)

logger_ = logging.getLogger(__name__)

VERBOSITY = {
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG,
}


def _generate_common_schema(
    profile_name: str,
    config: configparser.ConfigParser,
    credential: configparser.ConfigParser,
    env: configparser.ConfigParser,
    active_env: typing.Optional[schema.Env] = None,
    active_core: typing.Optional[schema.Core] = None,
    profile: typing.Union[schema.Profile, schema.OptionalProfile, None] = None,
) -> schema.Common:
    """Generate a common schema object.

    Set the default api values using user_profile and cli provided defaults.
    """
    return schema.Common(
        profile_name=profile_name,
        config=config,
        credential=credential,
        env=env,
        profile=profile,
        active_env=active_env,
        active_core=active_core,
    )


def _version_callback(*, value: bool) -> None:
    """Get current cli version."""
    if value:
        version = importlib.metadata.version("neosctl")
        typer.echo(f"neosctl {version}")
        raise typer.Exit


def setup_logging(verbose: int = 0) -> None:
    """Configure the logging."""
    logging.basicConfig(
        level=VERBOSITY.get(verbose, logging.DEBUG),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                show_level=False,
                show_path=False,
                show_time=False,
                tracebacks_suppress=[click],
            ),
        ],
    )
    asyncio_logger = logging.getLogger("asyncio")
    asyncio_logger.disabled = True
    root_logger = logging.getLogger("")
    root_logger.setLevel(VERBOSITY.get(verbose, logging.DEBUG))


def _callback(
    ctx: typer.Context,
    version: typing.Optional[bool] = typer.Option(  # noqa: ARG001
        None,
        "--version",
        callback=_version_callback,
        help="Print version and exit.",
    ),
    profile: str = typer.Option(
        os.getenv("NEOSCTL_PROFILE", constant.DEFAULT_PROFILE),
        "--profile",
        "-p",
        help="Profile name",
        callback=util.sanitize,
    ),
    env_override: typing.Optional[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Active env override",
        callback=util.sanitize,
    ),
    core_override: typing.Optional[str] = typer.Option(
        None,
        "--core",
        "-c",
        help="Active core override",
        callback=util.sanitize,
    ),
) -> None:
    """Inject common configuration defaults into context.

    Allow missing user_profile to support profile generation etc.
    """
    verbose = set(sys.argv) & {"-v", "-vv", "-vvv"}
    # If short verbosity is passed strip the `-` to get count of `v`s for verbosity setting.
    verbose = len(verbose.pop()) - 1 if verbose else 0

    # If full verbose flag is passed in, get count of flags
    if "--verbose" in sys.argv:
        verbose = sys.argv.count("--verbose")

    setup_logging(verbose)

    config = util.read_config_dotfile()
    env = util.read_env_dotfile()
    credential = util.read_credential_dotfile()
    user_profile = util.get_user_profile(config, profile, allow_missing=True)
    active_env = util.get_active_env(env, env_override)
    active_core = util.get_active_core(active_env, core_override)

    logger = logging.getLogger("neosctl.error")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(constant.LOG_FILEPATH)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    common_schema = _generate_common_schema(
        profile_name=profile,
        config=config,
        credential=credential,
        env=env,
        profile=user_profile,
        active_env=active_env,
        active_core=active_core,
    )

    ctx.obj = common_schema


app = typer.Typer(name="neosctl", callback=_callback, help="Interact with NEOS environments and cores.")
app.add_typer(profile.app, name="profile", help="Manage profiles. [DEPRECATED]")
app.add_typer(
    auth.app,
    name="auth",
    callback=util.user_profile_callback,
    help="Manage authentication status. [DEPRECATED]",
)
app.add_typer(services.iam.app, name="iam", callback=util.user_profile_callback, help="Manage access policies.")
app.add_typer(
    services.storage.app,
    name="storage",
    callback=util.user_profile_callback,
    help="Interact with Storage (as a service).",
)
app.add_typer(
    services.gateway.app,
    name="gateway",
    callback=util.user_profile_callback,
    help="Interact with Gateway service.",
)
app.add_typer(
    services.registry.app,
    name="registry",
    callback=util.user_profile_callback,
    help="Manage cores and search data products.",
)

app.add_typer(env.app, name="env", help="Manage environments.")
app.add_typer(info.app, name="info", help="Informational commands.")
