"""Utilities for user authentication."""

import typing
from warnings import warn

import typer

from neosctl import schema, util
from neosctl.util import (
    check_profile_exists,
    exit_with_output,
    is_success_response,
    process_response,
    upsert_config,
)

app = typer.Typer()


def _auth_url(iam_api_url: str) -> str:
    return "{}".format(iam_api_url.rstrip("/"))


@app.command()
def login(
    ctx: typer.Context,
    password: typing.Optional[str] = typer.Option(None, "--password", "-p", callback=util.sanitize),
    _verbose: util.Verbosity = 0,
) -> None:
    """Login to neos."""
    warn(
        "neosctl auth is deprecated, please use neosctl env",
        FutureWarning,
        stacklevel=2,
    )
    check_profile_exists(ctx)

    if password is None:
        password = typer.prompt(
            f"[{ctx.obj.profile_name}] Enter password for user ({ctx.obj.profile.user})",
            hide_input=True,
        )

    r = util.post(
        ctx,
        "iam",
        f"{_auth_url(ctx.obj.hub_api_url)}/iam/login",
        json={"user": ctx.obj.profile.user, "password": password},
    )

    if not is_success_response(r):
        process_response(r)

    upsert_config(ctx, util.update_profile(ctx, schema.Auth(**r.json())))

    raise exit_with_output(
        msg="Login success",
        exit_code=0,
    )


@app.command()
def logout(
    ctx: typer.Context,
    _verbose: util.Verbosity = 0,
) -> None:
    """Logout from neos."""
    warn(
        "neosctl auth is deprecated, please use neosctl env",
        FutureWarning,
        stacklevel=2,
    )
    check_profile_exists(ctx)

    util.check_refresh_token_exists(ctx)

    r = util.post(
        ctx,
        "iam",
        f"{_auth_url(ctx.obj.hub_api_url)}/iam/logout",
        json={"refresh_token": ctx.obj.profile.refresh_token},
    )

    if not is_success_response(r):
        process_response(r)

    upsert_config(ctx, util.update_profile(ctx, schema.Auth()))

    raise exit_with_output(
        msg="Logout success",
        exit_code=0,
    )
