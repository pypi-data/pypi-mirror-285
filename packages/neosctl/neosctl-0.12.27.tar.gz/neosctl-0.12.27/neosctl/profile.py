"""Profile commands, like profile initialisation, deletion, and listing."""

import re
import typing
from warnings import warn

import click
import typer

from neosctl import schema, util
from neosctl.util import (
    exit_with_output,
    get_user_profile_section,
    prettify_json,
    remove_config,
    upsert_config,
    upsert_credential,
)

app = typer.Typer()


r = re.compile(r"http[s]?:\/\/.*")


def _validate_url(value: str) -> str:
    """Validate a given url is a valid url with schema."""
    m = r.match(value)
    if m is None:
        msg = f"Invalid url, must match pattern: `{r}`."
        raise click.UsageError(msg)
    return value


@app.command()
def init(
    ctx: typer.Context,
    *,
    hostname: typing.Optional[str] = typer.Option(None, "--host", "-h", callback=util.sanitize),
    gateway_api_url: typing.Optional[str] = typer.Option(None, "--gateway-api-url", "-g", callback=util.sanitize),
    hub_api_url: typing.Optional[str] = typer.Option(None, "--hub-api-url", callback=util.sanitize),
    storage_api_url: typing.Optional[str] = typer.Option(None, "--storage-api-url", "-s", callback=util.sanitize),
    username: typing.Optional[str] = typer.Option(None, "--username", "-u", callback=util.sanitize),
    account: typing.Optional[str] = typer.Option("root", "--account", "-a", callback=util.sanitize),
    http_proxy: typing.Optional[str] = typer.Option(None, "--proxy", "-p", callback=util.sanitize),
    ignore_tls: bool = typer.Option(
        False,
        "--ignore-tls",
        help="Ignore TLS errors (useful in local/development environments",
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        help="Don't ask for input, generate api values based on hostname.",
    ),
    _verbose: util.Verbosity = 0,
) -> None:
    """Initialise a profile.

    Create a profile that can be reused in later commands to define which
    services to interact with, and which user to interact as.

    Call `init` on an existing profile will update the existing profile.
    """
    warn(
        "neosctl profile is deprecated, please use neosctl env",
        FutureWarning,
        stacklevel=2,
    )
    typer.echo(f"Initialising [{ctx.obj.profile_name}] profile.")
    bare_host = hostname.replace("http://", "").replace("https://", "") if hostname else ""

    if non_interactive and not (hostname and username):
        raise exit_with_output(
            msg="\nError: --hostname/-h and --username/-u required for non-interactive mode.",
            exit_code=1,
        )

    defaults = {
        "gateway": gateway_api_url
        or ctx.obj.gateway_api_url.replace("unset", "")
        or (f"{hostname}/api/gateway" if hostname else None),
        "storage": storage_api_url
        or ctx.obj.storage_api_url.replace("unset", "")
        or (f"https://saas.{bare_host}" if hostname else None),
        "hub": hub_api_url or ctx.obj.hub_api_url.replace("unset", "") or (f"{hostname}/api/hub" if hostname else None),
    }
    if non_interactive:
        gateway_api_url = defaults["gateway"]
        storage_api_url = defaults["storage"]
        hub_api_url = defaults["hub"]

    urls = {
        "gateway_api_url": gateway_api_url,
        "hub_api_url": hub_api_url,
        "storage_api_url": storage_api_url,
    }
    for key, prompt in [
        ("gateway", "Gateway API url"),
        ("hub", "Hub API url"),
        ("storage", "Storage API url"),
    ]:
        url_key = f"{key}_api_url"
        url = urls[url_key]
        if url is None:
            urls[url_key] = typer.prompt(
                prompt,
                default=defaults[key],
                value_proc=_validate_url,
            )
        else:
            _validate_url(url)

    if username is None:
        kwargs = {}
        if ctx.obj.profile:
            kwargs["default"] = ctx.obj.profile.user
        username_input: str = typer.prompt(
            "Username",
            **kwargs,
        )
        username = username_input

    profile = schema.Profile(  # nosec: B106
        user=username,
        account=account or "",
        access_token="",
        refresh_token="",
        ignore_tls=ignore_tls,
        http_proxy=http_proxy or "",
        **urls,
    )

    upsert_config(ctx, profile)


@app.command()
def delete(
    ctx: typer.Context,
    _verbose: util.Verbosity = 0,
) -> None:
    """Delete a profile."""
    warn(
        "neosctl profile is deprecated, please use neosctl env",
        FutureWarning,
        stacklevel=2,
    )
    typer.confirm(f"Remove [{ctx.obj.profile_name}] profile", abort=True)
    remove_config(ctx)


@app.command()
def view(
    ctx: typer.Context,
    _verbose: util.Verbosity = 0,
) -> None:
    """View configuration for a profile."""
    warn(
        "neosctl profile is deprecated, please use neosctl env",
        FutureWarning,
        stacklevel=2,
    )
    profile = get_user_profile_section(ctx.obj.config, ctx.obj.profile_name)
    raise exit_with_output(
        msg=prettify_json({k: v for k, v in profile.items()}),  # noqa: C416
    )


@app.command()
def credentials(
    ctx: typer.Context,
    access_key_id: str,
    secret_access_key: str,
    _verbose: util.Verbosity = 0,
) -> None:
    """View configuration for a profile."""
    warn(
        "neosctl profile is deprecated, please use neosctl env",
        FutureWarning,
        stacklevel=2,
    )
    upsert_credential(ctx, access_key_id, secret_access_key)


@app.command(name="list")
def list_profiles(
    ctx: typer.Context,
    _verbose: util.Verbosity = 0,
) -> None:
    """List available profiles."""
    warn(
        "neosctl profile is deprecated, please use neosctl env",
        FutureWarning,
        stacklevel=2,
    )
    raise exit_with_output(
        msg=prettify_json(sorted(ctx.obj.config.sections())),
    )
