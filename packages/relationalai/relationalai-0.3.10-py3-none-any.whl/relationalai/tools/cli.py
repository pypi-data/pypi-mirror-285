#pyright: reportPrivateImportUsage=false
from __future__ import annotations
import os
import re
import sys
import rich
import json
import click
import shlex
import requests
from pathlib import Path
from rich.table import Table
from datetime import datetime
from rich import box as rich_box
from InquirerPy.base.control import Choice
from .cli_controls import MANUAL_ENTRY, divider, Spinner
from . import cli_controls as controls
from relationalai.clients import azure
from typing import Sequence, cast, Any, List
from relationalai.errors import RelQueryError
from relationalai.loaders.types import LoadType, UnsupportedTypeError
from relationalai.loaders.csv import CSVLoader
from relationalai.loaders.loader import Loader, rel_schema_to_type
from ..clients.types import ImportSource, ImportSourceFile, ImportSourceTable
from ..clients.client import ResourceProvider
from ..tools import debugger as deb
from ..clients import config, snowflake
from relationalai.tools.cli_helpers import (
    COMPUTE_POOL_REGEX,
    EMPTY_STRING_REGEX,
    ENGINE_NAME_ERROR,
    ENGINE_NAME_REGEX,
    UUID,
    RichGroup,
    account_from_url,
    coming_soon,
    ensure_config,
    exit_with_divider,
    exit_with_error,
    filter_profiles_by_platform,
    format_row,
    get_config, get_resource_provider,
    issue_top_level_profile_warning,
    show_dictionary_table,
    show_engines,
    show_imports,
    show_transactions,
    supports_platform,
    unexpand_user_path,
    validate_engine_name
)
from ..clients.config import (
    FIELD_PLACEHOLDER,
    CONFIG_FILE,
    ConfigStore,
    all_configs_including_legacy,
    get_from_snowflake_connections_toml,
    azure_default_props,
    map_toml_value,
    snowflake_default_props,
)
from relationalai.tools.constants import AZURE, AZURE_ENVS, CONTEXT_SETTINGS, SNOWFLAKE
from relationalai.util.constants import DEFAULT_PROFILE_NAME, PARTIAL_PROFILE_NAME, TOP_LEVEL_PROFILE_NAME
from packaging.version import Version

#--------------------------------------------------
# Custom Click Option and Argument Types
#--------------------------------------------------

ImportOption = tuple[list[str], str]

class ImportOptionsType(click.ParamType):
    def __init__(self):
        self.options = {}

    name = "import_options"
    def convert(self, raw, param, ctx) -> ImportOption:
        if ':' not in raw or '=' not in raw:
            self.fail(f"'{raw}' is not a valid import option.", param, ctx)
        raw_key, val = raw.split('=', 1)
        if len(val) == 2 and val[0] == "\\":
            val = val.encode().decode("unicode_escape")
        return (raw_key.split(":"), val)

    @classmethod
    def reduce(cls, kvs:Sequence[ImportOption]):
        options = {}
        for (key_parts, val) in kvs:
            cur = options
            for part in key_parts[:-1]:
                cur = cur.setdefault(part, {})
            cur[key_parts[-1]] = val
        return options

#--------------------------------------------------
# Main group
#--------------------------------------------------

@click.group(cls=RichGroup, context_settings=CONTEXT_SETTINGS)
@click.option("--profile", help="Which config profile to use")
def cli(profile):
    global PROFILE
    PROFILE = profile

#--------------------------------------------------
# Init
#--------------------------------------------------

@cli.command(help="Initialize a new project")
def init():
    init_flow()

#--------------------------------------------------
# Init flow
#--------------------------------------------------

def azure_flow(cfg:config.Config):
    option_selected = check_original_config_flow(cfg, "azure")
    # get the client id and secret
    client_id = controls.text("Client ID:", default=cfg.get("client_id", "") if option_selected else "")
    client_secret = controls.password("Client Secret:", default=cfg.get("client_secret", "") if option_selected else "")
    host = cfg.get("host", "")
    client_credentials_url = cfg.get("client_credentials_url", "")
    if not host or not client_credentials_url:
        env = controls.fuzzy("Select environment:", [*AZURE_ENVS.keys(), "<custom>"])
        if env == "<custom>":
            host = controls.text("Host:")
            client_credentials_url = controls.text("Client Credentials URL:")
        else:
            host = AZURE_ENVS[env]["host"]
            client_credentials_url = AZURE_ENVS[env]["client_credentials_url"]
    # setup the default config
    cfg.fill_in_with_azure_defaults(
        client_id=client_id,
        client_secret=client_secret,
        host=host if host else None,
        client_credentials_url=client_credentials_url if client_credentials_url else None
    )

def snowflake_flow(cfg:config.Config):
    pyrel_config = check_original_config_flow(cfg, "snowflake")
    if not pyrel_config:
        check_snowflake_connections_flow(cfg)

    # get account info
    user = controls.text(
        "SnowSQL user:",
        default=cfg.get("user", ""),
        validator=EMPTY_STRING_REGEX.match,
        invalid_message="User is required"
    )
    cfg.set("user", user)

    password = controls.password(
        "SnowSQL password:",
        default=cfg.get("password", ""),
        validator=EMPTY_STRING_REGEX.match,
        invalid_message="Password is required"
    )
    cfg.set("password", password)

    rich.print("\n  Note: Account ID should look like: myorg-account123")
    rich.print("  Details: https://docs.snowflake.com/en/user-guide/admin-account-identifier\n")
    rich.print("  Alternatively, you can log in to Snowsight, copy the URL, and paste it here.")
    rich.print("  Example: https://app.snowflake.com/myorg/account123/worksheets\n")
    account_or_url = controls.text(
        "Snowflake account:",
        default=cfg.get("account", ""),
        validator=EMPTY_STRING_REGEX.match,
        invalid_message="Account is required"
    )
    account = account_from_url(account_or_url)
    if "." in account:
        rich.print("\n[yellow] Your Account ID should not contain a period (.) character.")
        corrected_account = account.replace(".", "-")
        use_replacement = controls.confirm(f"Use '{corrected_account}' instead", default=True)
        if use_replacement:
            account = corrected_account
    if account_or_url != account:
        rich.print(f"\n[dim]  Account ID: {account}")
    cfg.set("account", account)
    # setup the default config
    cfg.fill_in_with_snowflake_defaults(
        user=user,
        password=password,
        account=account,
    )

def check_original_config_flow(cfg:config.Config, platform:str):
    all_profiles = {}
    for config_file in all_configs_including_legacy():
        file_path = config_file.path
        plt_config = filter_profiles_by_platform(config_file, platform)
        for profile, props in plt_config.items():
            profile_id = (profile, file_path)
            all_profiles[profile_id] = props
    if platform == "snowflake":
        sf_config = get_from_snowflake_connections_toml()
        if sf_config:
            file_path = os.path.expanduser("~/.snowflake/connections.toml")
            for profile, props in sf_config.items():
                profile_id = (profile, file_path)
                all_profiles[profile_id] = props
    if len(all_profiles) == 0:
        return
    max_profile_name_len = max(len(profile) for profile, _ in all_profiles.keys())
    profile_options: List[Choice] = []
    for profile, props in all_profiles.items():
        formatted_name = f"{profile[0]:<{max_profile_name_len}}  {unexpand_user_path(profile[1])}"
        profile_options.append(Choice(value=profile, name=formatted_name))
    selected_profile = controls.select("Use existing profile", list(profile_options), None, mandatory=False)
    if not selected_profile:
        return
    cfg.profile = selected_profile[0]
    if cfg.profile == PARTIAL_PROFILE_NAME:
        cfg.profile = TOP_LEVEL_PROFILE_NAME
    cfg.update(all_profiles[selected_profile])
    return True

def check_snowflake_connections_flow(cfg:config.Config):
    sf_config = get_from_snowflake_connections_toml()
    if not sf_config or len(sf_config) == 0:
        return
    profiles = list(sf_config.keys())
    if len(profiles) == 0:
        return
    profile = controls.fuzzy("Use profile from ~/.snowflake/connections.toml", profiles, mandatory=False)
    if not profile:
        return
    cfg.profile = profile
    cfg.update(sf_config[profile])
    return True

def role_flow(provider:ResourceProvider, cfg:config.Config):
    roles = cast(snowflake.Resources, provider).list_roles()
    result = controls.fuzzy_with_refetch(
            "Select a role:",
            "roles",
            lambda: [r["name"] for r in roles],
            default=cfg.get("role", None),
        )
    if isinstance(result, Exception):
        return
    else:
        role = result
    cfg.set("role", role or FIELD_PLACEHOLDER)
    provider.reset()

def warehouse_flow(provider:ResourceProvider, cfg:config.Config):
    result = controls.fuzzy_with_refetch(
            "Select a warehouse:",
            "warehouses",
            lambda: [w["name"] for w in cast(snowflake.Resources, provider).list_warehouses()],
            default=cfg.get("warehouse", None),
        )
    if not result or isinstance(result, Exception):
        return
    else:
        warehouse = result
    cfg.set("warehouse", warehouse or FIELD_PLACEHOLDER)

def rai_app_flow(provider:ResourceProvider, cfg:config.Config):
    auto_select = None
    if provider.config.get("platform") == "snowflake":
        auto_select=snowflake.RAI_APP_NAME

    result = controls.fuzzy_with_refetch(
            "Select RelationalAI app name:",
            "apps",
            lambda: [w["name"] for w in cast(snowflake.Resources, provider).list_apps()],
            default=cfg.get("rai_app_name", None),
            auto_select=auto_select
        )
    if not result or isinstance(result, Exception):
        return
    else:
        app = result
    cfg.set("rai_app_name", app or FIELD_PLACEHOLDER)
    provider.reset()

def spcs_flow(provider: ResourceProvider, cfg: config.Config):
    role_flow(provider, cfg)
    warehouse_flow(provider, cfg)
    rai_app_flow(provider, cfg)

def create_engine(cfg:config.Config, **kwargs):
    provider = get_resource_provider(None, cfg)
    prompt = kwargs.get("prompt", "Select an engine:")
    result = controls.fuzzy_with_refetch(
        prompt,
        "engines",
        lambda: ["[CREATE A NEW ENGINE]"] + [engine.get("name") for engine in provider.list_engines()],
        default=cfg.get("engine", None),
    )
    if not result or isinstance(result, Exception):
        raise Exception("Error fetching engines")
    else:
        engine = result
    if result == "[CREATE A NEW ENGINE]":
        engine = create_engine_flow(cfg)
        rich.print("")
    return engine

def engine_flow(provider:ResourceProvider, cfg:config.Config, **kwargs):
    if provider.config.get("platform") == "snowflake":
        app_name = cfg.get("rai_app_name", None)
        if not app_name:
            rich.print("[yellow]App name is required for engine selection. Skipping step.\n")
            raise Exception("App name is required for engine selection")
        warehouse = cfg.get("warehouse", None)
        if not warehouse:
            rich.print("[yellow]Warehouse is required for engine selection. Skipping step.\n")
            raise Exception("Warehouse is required for engine selection")
    prompt = kwargs.get("prompt", "Select an engine:")
    engine = create_engine(cfg, prompt=prompt)
    cfg.set("engine", engine or FIELD_PLACEHOLDER)

def gitignore_flow():
    current_dir = Path.cwd()
    prev_dir = None
    while current_dir != prev_dir:
        gitignore_path = current_dir / '.gitignore'
        if gitignore_path.exists():
            # if there is, check to see if raiconfig.toml is in it
            with open(gitignore_path, 'r') as gitignore_file:
                if CONFIG_FILE in gitignore_file.read():
                    return
                else:
                    # if it's not, ask to add it
                    add_to_gitignore = controls.confirm(f"Add {CONFIG_FILE} to .gitignore?", default=True)
                    if add_to_gitignore:
                        with open(gitignore_path, 'a') as gitignore_file:
                            gitignore_file.write(f"\n{CONFIG_FILE}")
                    return
        prev_dir = current_dir
        current_dir = current_dir.parent

def is_valid_bare_toml_key(key):
    pattern = re.compile(r'^[A-Za-z_][A-Za-z0-9_-]*$')
    return bool(pattern.match(key))

def name_profile_flow(cfg: config.Config):
    if cfg.profile != TOP_LEVEL_PROFILE_NAME:
        return
    profile = controls.text("New name for this profile:", default=DEFAULT_PROFILE_NAME)
    if not is_valid_bare_toml_key(profile):
        rich.print(
            "[yellow]Invalid profile name: should contain only alphanumeric characters, dashes, and hyphens"
        )
        return name_profile_flow(cfg)
    config_store = ConfigStore()
    if profile in config_store.get_profiles():
        overwrite = controls.confirm(f"[yellow]Overwrite existing {profile} profile?")
        if overwrite:
            return profile
        else:
            return name_profile_flow(cfg)
    return profile

def save_flow(cfg:config.Config):
    config_store = ConfigStore()
    if cfg.profile != PARTIAL_PROFILE_NAME and cfg.profile in config_store.get_profiles():
        if not controls.confirm(f"Overwrite existing {cfg.profile} profile"):
            rich.print()
            profile_name = controls.text("Profile name:")
            if profile_name:
                cfg.profile = profile_name
            else:
                save_flow(cfg)
                return
    config_store.add_profile(cfg)
    if cfg.profile != PARTIAL_PROFILE_NAME:
        rich.print()
        if config_store.num_profiles() == 1 or controls.confirm("Activate this profile?"):
            config_store.change_active_profile(cfg.profile)
    config_store.save()

def init_flow():
    cfg = config.Config(fetch=False)
    try:
        cfg.clone_profile()
        rich.print("\n[dim]---------------------------------------------------\n")
        rich.print("[bold]Welcome to [green]RelationalAI!\n")
        rich.print("Press Control-S to skip a prompt\n")

        if ConfigStore().get("platform"):
            issue_top_level_profile_warning()

        platform = controls.fuzzy("Host platform:", choices=[SNOWFLAKE, AZURE])
        cfg.set("platform", {
            SNOWFLAKE: "snowflake",
            AZURE: "azure"
        }[platform])

        if platform == SNOWFLAKE:
            snowflake_flow(cfg)
        elif platform == AZURE:
            azure_flow(cfg)
        elif platform:
            rich.print("[yellow]Initialization aborted!")
            rich.print(f"[yellow]Unknown platform: {platform}")
            return

        provider = get_resource_provider(None, cfg)

        rich.print()
        if platform == SNOWFLAKE:
            spcs_flow(provider, cfg)
        engine_flow(provider, cfg)
        profile = name_profile_flow(cfg)
        if profile:
            cfg.profile = profile
        save_flow(cfg)

        gitignore_flow()
        rich.print("")
        rich.print(f"[green]✓ {CONFIG_FILE} saved!")
        rich.print("\n[dim]---------------------------------------------------\n")
    except Exception as e:
        rich.print("")
        rich.print("[yellow bold]Initialization aborted!\n")
        print(e.with_traceback(None))
        rich.print("")

        save = controls.confirm("Save partial config?")
        if save:
            cfg.profile = PARTIAL_PROFILE_NAME
            rich.print("")
            cfg.fill_in_with_defaults()
            save_flow(cfg)
            gitignore_flow()
            rich.print(f"[yellow bold]✓ Saved partial {CONFIG_FILE} ({os.path.abspath(CONFIG_FILE)})")

        divider()

#--------------------------------------------------
# Profile switcher
#--------------------------------------------------

@cli.command(
    name="profile:switch",
    help="Switch to a different profile",
)
@click.option("--profile", help="Profile to switch to")
def profile_switch(profile:str|None=None):
    config_store = ConfigStore()
    current_profile = None
    try:
        current_profile = config_store.get_config().profile or None
    except Exception:
        pass
    profiles = list(config_store.get_profiles().keys())
    divider()
    if not profile:
        if len(profiles) == 0:
            exit_with_error("[yellow]No profiles found")
        profile = controls.fuzzy("Select a profile:", profiles, default=current_profile)
        divider()
    else:
        if profile not in profiles:
            exit_with_error(f"[yellow]Profile '{profile}' not found")
    config_store.change_active_profile(profile)
    config_store.save()
    rich.print(f"[green]✓ Switched to profile '{profile}'")
    divider()

#--------------------------------------------------
# Print config file
#--------------------------------------------------
@cli.command(
    name="config:print",
    help="Print the config file contents with secrets masked",
)
def config_print():
    divider()
    cfg = ensure_config()
    rich.print(f"[bold green]{cfg.file_path}\n")
    with open(cfg.file_path, "r") as f:
        content = f.read()
    for line in content.split("\n"):
        if "client_secret" in line or "password" in line:
            chars = []
            equals_found = False
            for char in line:
                if char == "=":
                    equals_found = True
                    chars.append(char)
                    continue
                if equals_found and char != "\"" and char != " ":
                    chars.append("*")
                else:
                    chars.append(char)
            line = "".join(chars)
        print(line)
    divider()

#--------------------------------------------------
# Explain config
#--------------------------------------------------

@cli.command(
    name="config:explain",
    help="Inspect config status",
)
@click.option(
    "--profile",
    help="Profile to inspect",
)
@click.option(
    "--all-profiles",
    help="Whether to show all profiles in config file",
    is_flag=True,
)
def config_explain(profile:str|None=None, all_profiles:bool=False):
    divider()
    cfg = ensure_config(profile)
    config_store = ConfigStore()

    if config_store.get("platform"):
        issue_top_level_profile_warning()

    rich.print(f"[bold green]{cfg.file_path}")
    if os.getenv("RAI_PROFILE"):
        rich.print(f"[yellow]Environment variable [bold]RAI_PROFILE = {os.getenv('RAI_PROFILE')}[/bold]")
    rich.print("")
    if cfg.profile != TOP_LEVEL_PROFILE_NAME:
        rich.print(f"[bold]\\[{cfg.profile}]")

    for key, value in cfg.items_with_dots():
        if key == "active_profile" and cfg.profile != TOP_LEVEL_PROFILE_NAME:
            continue
        rich.print(f"{key} = [cyan bold]{map_toml_value(mask(key, value))}")

    platform = cfg.get("platform", "snowflake")
    defaults = snowflake_default_props if platform == "snowflake" else azure_default_props

    for key, value in defaults.items():
        if key not in cfg:
            rich.print(f"[yellow bold]{key}[/yellow bold] = ?" + (
                f" (default: {value})" if value and value != FIELD_PLACEHOLDER else ""
            ))

    if all_profiles:
        for profile, props in config_store.get_profiles().items():
            if profile == cfg.profile:
                continue
            if len(props):
                rich.print()
                rich.print(f"[bold]\\[{profile}][/bold]")
                for key, value in props.items():
                    rich.print(f"{key} = [cyan bold]{map_toml_value(mask(key, value))}")

    divider()

def mask(key: str, value: Any):
    if key in ["client_secret", "password"]:
        return "*" * len(str(value))
    return value

#--------------------------------------------------
# Check config
#--------------------------------------------------

@cli.command(
    name="config:check",
    help="Check whether config is valid",
)
def config_check(all_profiles:bool=False):
    error = None
    divider()
    if ConfigStore().get("platform"):
        issue_top_level_profile_warning()

    cfg = ensure_config()

    with Spinner("Connecting to platform...", "Connection successful!", "Error:"):
        try:
            provider = get_resource_provider(None, cfg)
            # Engine is required by both clients if it is not configured check would fail already
            engine_name = cfg.get("engine")
            # This essentially checks if the profile is valid since we are connecting to get the engine
            engine = provider.get_engine(engine_name)
            if not engine:
                error = Exception(f"Configured engine '{engine_name}' not found")
            elif not provider.is_valid_engine_state(engine.get("state")):
                error = Exception(f"Engine '{engine_name}' is in an invalid state: '{engine.get('state')}'")
        except Exception as e:
            error = e
        if error:
            raise error
    if error:
        exit_with_divider(1)
    divider()

#--------------------------------------------------
# Version
#--------------------------------------------------

def latest_version(package_name):
    """Get the current version of a package on PyPI."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        version = data['info']['version']
        return version
    else:
        return None

@cli.command(help="Print version info")
def version():
    from .. import __version__
    from railib import __version__ as railib_version

    table = Table(show_header=False, border_style="dim", header_style="bold", box=rich_box.SIMPLE)
    def print_version(name, version, latest=None):
        if latest is not None and Version(version) < Version(latest):
            table.add_row(f"[bold]{name}[red]", f"[red bold]{version} → {latest}")
        else:
            table.add_row(f"[bold]{name}", f"[green]{version}")

    divider()
    print_version("RelationalAI", __version__, latest_version("relationalai"))
    print_version("Rai-sdk", railib_version, latest_version("rai-sdk"))
    print_version("Python", sys.version.split()[0])

    try:
        cfg = get_config()
        app_version = None
        if not cfg.file_path:
            table.add_row("[bold]App", "No configuration file found. To create one, run: [green]rai init")
        else:
            platform = cfg.get("platform", None)
            if platform == "snowflake":
                with Spinner("Checking app version"):
                    try:
                        app_version = get_resource_provider().get_version()
                    except Exception as e:
                        if ("Unknown user-defined function" in f"{e}"):
                            app_version = Exception("Unable to acquire app version.\nPlease make sure your Snowflake native application is up and running.")
                        else:
                            app_version = e

                if not isinstance(app_version, Exception):
                    print_version("App", app_version)

    except Exception as e:
        rich.print(f"[yellow]Error checking app version: {e}")
        exit_with_divider(1)

    rich.print(table)

    if isinstance(app_version, Exception):
        error_table = Table(show_header=False, border_style="dim", header_style="bold", box=rich_box.SIMPLE)
        error_table.add_row("App", f"[yellow]{app_version}")
        rich.print(error_table)

    divider()

#--------------------------------------------------
# Debugger
#--------------------------------------------------

@cli.command(help="Open the RAI debugger")
@click.option("--host", help="Host to use", default="0.0.0.0")
@click.option("--port", help="Port to use", default=8080)
@click.option("--new", help="Use the new debugger", is_flag=True, default=False)
@click.option("--profile", help="Profile to use", default=None)

def debugger(host, port, new, profile):
    if new:
        from relationalai.tools import debugger_server
        debugger_server.start_server(host, port, profile)
    else:
        deb.main(host, port)

#--------------------------------------------------
# Engine list
#--------------------------------------------------

@cli.command(name="engines:list", help="List all engines")
@click.option("--state", help="Filter by engine state")
def engines_list(state:str|None=None):
    divider(flush=True)
    ensure_config()
    with Spinner("Fetching engines"):
        try:
            engines = get_resource_provider().list_engines(state)
        except Exception as e:
            exit_with_error(f"\n\n[yellow]Error fetching engines: {e}")

    if len(engines):
        show_engines(engines)
    else:
        exit_with_error("[yellow]No engines found")
    divider()

@cli.command(name="engines:get", help="Get engine details")
@click.option("--name", help="Name of the engine")
def engines_get(name:str|None=None):
    divider(flush=True)
    ensure_config()

    if not name:
        name = controls.text("Engine name:", validator=ENGINE_NAME_REGEX.match, invalid_message=ENGINE_NAME_ERROR)
        rich.print("")

    with Spinner("Fetching engine"):
        try:
            engine = get_resource_provider().get_engine(name)
        except Exception as e:
            exit_with_error(f"\n\n[yellow]Error fetching engine: {e}")

    if engine:
        table = Table(show_header=True, border_style="dim", header_style="bold", box=rich_box.SIMPLE_HEAD)
        table.add_column("Name")
        table.add_column("Size")
        table.add_column("State")
        table.add_row(engine.get("name"), engine.get("size"), engine.get("state"))
        rich.print(table)
    else:
        exit_with_error(f'[yellow]Engine "{name}" not found')
    divider()

#--------------------------------------------------
# Engine create
#--------------------------------------------------

def create_engine_flow(cfg:config.Config, name=None, size=None, pool=None):
    provider = get_resource_provider(None, cfg)
    is_snowflake = cfg.get("platform") == "snowflake"
    is_interactive = name is None or size is None or (is_snowflake and pool is None)

    if not name:
        name = controls.prompt(
            "Engine name:",
            name,
            validator=ENGINE_NAME_REGEX.match,
            invalid_message=ENGINE_NAME_ERROR,
            newline=True
        )

    if is_interactive:
        with Spinner(f"Validating engine '{name}' name", "Engine name validated", "Error:"):
            is_name_valid = validate_engine_name(cfg, name)
        if isinstance(is_name_valid, str):
            rich.print("")
            rich.print(f"[yellow]{is_name_valid}")
            rich.print("")
            return create_engine_flow(cfg)
    else:
        is_name_valid = validate_engine_name(cfg, name)
        if isinstance(is_name_valid, str):
            exit_with_error(f"[yellow]{is_name_valid}")

    rich.print()
    if not size:
        size = controls.fuzzy("Engine size:", choices=provider.get_engine_sizes())
        rich.print("")

    if is_snowflake:
        provider = cast(snowflake.Resources, provider)
        if not pool:
            result = controls.fuzzy_with_refetch(
                "Compute pool:",
                "compute pools",
                provider.list_valid_compute_pools_by_engine_size,
                size,
                manual_entry=True
            )
            if isinstance(result, Exception):
                exit_with_error(f"[yellow]{result}")
            else:
                if result == MANUAL_ENTRY:
                    result = controls.prompt(
                        "Compute pool name:",
                        None,
                        validator=COMPUTE_POOL_REGEX.match,
                        invalid_message="Invalid name: must start with a letter, only letters, numbers, underscores allowed.",
                        newline=True
                    )
                pool = result
        if is_interactive and not pool:
            rich.print("[yellow]No compute pool selected\n")
            redo_engine_size = controls.confirm("Would you like to choose a different engine size?", default=True)
            rich.print("")
            if redo_engine_size:
                return create_engine_flow(cfg, name)
            else:
                return None
    else:
        pool = ""

    create_exception = None

    with Spinner(
        f"Creating '{name}' engine... (this may take several minutes)",
        f"Engine '{name}' created!",
        failed_message="Error:"
    ):
        try:
            provider.create_engine(name, size, pool)
        except Exception as e:
            create_exception = e
            # We do not want to print the success context message if the engine creation fails
            # Since we are raising here and passing a "fail_message", the spinner will print the actual error message
            raise e
    if isinstance(create_exception, Exception):
        if is_interactive and "does not exist" in f"{create_exception}".lower():
            rich.print("")
            redo = controls.confirm("Would you like to choose a different compute pool?", default=True)
            rich.print("")
            if redo:
                return create_engine_flow(cfg, name, size)
        exit_with_error(f"[yellow]{create_exception}")
    return name

@cli.command(name="engines:create", help="Create a new engine")
@click.option("--name", help="Name of the engine")
@click.option("--size", help="Size of the engine")
@click.option("--pool", help="Compute pool name. Note: Snowflake platform only.")
def engines_create(name, size, pool):
    divider(flush=True)
    cfg = ensure_config()
    create_engine_flow(cfg, name, size, pool)
    divider()

#--------------------------------------------------
# Engine delete
#--------------------------------------------------

@cli.command(name="engines:delete", help="Delete an engine")
@click.option("--name", help="Name of the engine")
@click.option("--force", help="Force delete the engine", is_flag=True)
def engines_delete(name, force=False):
    divider(flush=True)
    ensure_config()
    provider = get_resource_provider()
    if not name:
        name = controls.fuzzy_with_refetch(
            "Select an engine:",
            "engines",
            lambda: [engine["name"] for engine in provider.list_engines()],
        )
        if not name or isinstance(name, Exception):
            return
    else:
        try:
            engine = provider.get_engine(name)
            if not engine:
                exit_with_error(f"[yellow]Engine '{name}' not found")
        except Exception as e:
            exit_with_error(f"[yellow]Error fetching engine: {e}")

    del_err = None
    with Spinner(f"Deleting '{name}' engine", f"Engine '{name}' deleted!", "Error:"):
        try:
            provider.delete_engine(name, force)
        except Exception as e:
            if "SETUP_CDC" in f"{e}":
                del_err = Exception("[yellow]Imports are setup to utilize this engine.\nUse '[cyan]rai engines:delete --force[/cyan]' to force delete engines.\nUse '[cyan]rai imports:setup --engine[/cyan]' to set a different engine for imports.")
            else:
                del_err = e
            raise del_err
    if isinstance(del_err, Exception):
        exit_with_divider(1)
    divider()

#--------------------------------------------------
# Import Source flows
#--------------------------------------------------

def import_source_flow(provider: ResourceProvider) -> Sequence[ImportSource]:
    provider_type = type(provider)

    if isinstance(provider, snowflake.Resources):
        return snowflake_import_source_flow(provider)
    elif isinstance(provider, azure.Resources):
        return azure_import_source_flow(provider)
    else:
        raise Exception(f"No import source flow available for {provider_type.__module__}.{provider_type.__name__}")

def snowflake_import_source_flow(provider: snowflake.Resources) -> Sequence[ImportSource]:
    with Spinner("Fetching databases", "Databases fetched"):
        try:
            dbs = provider.list_databases()
        except Exception as e:
            rich.print(f"\n\n[yellow]Error fetching databases: {e}", file=sys.stderr)
            dbs = []
    if len(dbs) == 0:
        exit_with_error("[yellow]No databases found")
    rich.print()
    db = controls.fuzzy("Select a database:", [db["name"] for db in dbs])
    rich.print()

    with Spinner("Fetching schemas", "Schemas fetched"):
        try:
            schemas = provider.list_sf_schemas(db)
        except Exception as e:
            rich.print(f"\n\n[yellow]Error fetching schemas: {e}")
            schemas = []
    if len(schemas) == 0:
        exit_with_error("[yellow]No schemas found")
    rich.print()
    schema = controls.fuzzy("Select a schema:", [s["name"] for s in schemas])
    rich.print()

    with Spinner("Fetching tables", "Tables fetched"):
        try:
            tables = provider.list_tables(db, schema)
        except Exception as e:
            rich.print(f"\n\n[yellow]Error fetching tables: {e}")
            tables = []
    if len(tables) == 0:
        exit_with_error("[yellow]No tables found")
    rich.print()
    if tables:
        tables = controls.fuzzy("Select tables (tab for multiple):", [t["name"] for t in tables], multiselect=True)
    else:
        rich.print("[yellow]No tables found")
        tables = ""
    rich.print()
    if isinstance(tables, list):
        return [ImportSourceTable(db, schema, table) for table in tables]
    else:
        return [ImportSourceTable(db, schema, tables)]

def azure_import_source_flow(provider: azure.Resources) -> Sequence[ImportSource]:
    result = controls.file("Select a file:", allow_freeform=True)
    return [ImportSourceFile(result)] if result else []

def import_source_options_flow(provider: ResourceProvider, source: ImportSource, default_options:dict) -> dict:
    if isinstance(source, ImportSourceFile):
        type: LoadType = default_options.get("type", None)
        if type is None or type == "auto":
            type = Loader.get_type_for(source)
        if type == "csv":
            return import_source_csv_options_flow(provider, source, default_options)

    return default_options

def import_source_csv_options_flow(provider: ResourceProvider, source: ImportSourceFile, default_options:dict) -> dict:
    user_specified_schema = {k.strip(): rel_schema_to_type(v.lower()) for k, v in default_options.get("schema", {}).items()}
    user_specified_syntax = default_options.get("syntax", {})

    if source.is_url():
        # @FIXME: Should maybe prompt user to provide a schema manually for urls?
        return {**default_options, "schema": user_specified_schema}

    # Syntax inference + confirmation for local files ==========================

    syntax = CSVLoader.guess_syntax(source.raw_path)
    syntax.update(user_specified_syntax)

    syntax_table = Table(show_header=True, border_style="dim", header_style="bold", box=rich_box.SIMPLE_HEAD)
    for k in syntax.keys():
        syntax_table.add_column(k)
    syntax_table.add_row(*[
        repr(v)[1:-1] if isinstance(v, str) else
        "[dim]<default>[/dim]" if v is None else
        str(v)
        for v in syntax.values()])

    rich.print(syntax_table)

    if not controls.confirm(f"Use this dialect for {source.name}:", True):
        fail_import_options_flow(
            source,
            "You can manually specify the CSV dialectusing syntax arguments. For example, to set the [cyan]delimiter[/cyan] to [green]tab[/green], run:",
            'syntax:[cyan]delim[/cyan]="[green]\\t[/green]"'
        )

    # Schema inference + confirmation for local files ==========================

    schema, csv_chunk = CSVLoader.guess_schema(source.raw_path, syntax)
    schema.update(user_specified_schema)

    schema_table = Table(show_header=True, border_style="dim", header_style="bold", box=rich_box.SIMPLE_HEAD)
    schema_table.add_column("Field")
    schema_table.add_column("Type")
    schema_table.add_column("Ex.")
    for field, type in schema.items():
        schema_table.add_row(field, type.name, f"[dim]{csv_chunk[field][0]}")

    rich.print(schema_table)

    if not controls.confirm(f"Use this schema for {source.name}:", True):
        field = next(iter(schema.keys()))
        fail_import_options_flow(
            source,
            f"You can manually specify column types using schema arguments. For example, to load the column [cyan]{field}[/cyan] as a [green]string[/green], run:",
            f"schema:[cyan]{field}[/cyan]=[green]string[/green]"
        )

    return {**default_options, "schema": schema, "syntax": syntax}

def fail_import_options_flow(source: ImportSourceFile, message: str, solution_args: str):
    prev_cmd_args = " ".join(shlex.quote(arg) for arg in sys.argv[1:])
    saved_args = []
    if "--source" not in sys.argv:
        saved_args.append(f"--source {shlex.quote(source.raw_path)}")
    if "--name" not in sys.argv:
        saved_args.append(f"--name {shlex.quote(source.name)}")

    saved_args = " " + " ".join(saved_args) if saved_args else ""
    print()
    rich.print(message)
    print()
    rich.get_console().print(f"[dim]    rai {prev_cmd_args}{saved_args}[/dim] {solution_args}", highlight=False)
    divider()
    exit(0)


def parse_source(provider: ResourceProvider, raw: str) -> ImportSource:
    if provider.platform == "azure":
        return ImportSourceFile(raw)
    elif provider.platform == "snowflake":
        parts = raw.split(".")
        assert len(parts) == 3, "Snowflake table imports must be in `database.schema.table` format"
        return ImportSourceTable(*parts)
    else:
        raise Exception(f"Unsupported platform: {provider.platform}")

#--------------------------------------------------
# Imports
#--------------------------------------------------

@supports_platform("snowflake")
@cli.command(name="imports:setup", help="Modify and view imports setup")
@click.option("--engine", help="The engine name to set for imports")
@click.option("--resume", help="Resume imports", is_flag=True)
@click.option("--suspend", help="Suspend imports", is_flag=True)
def imports_setup(engine:str|None=None, resume:bool=False, suspend:bool=False):
    divider(flush=True)
    cfg = ensure_config()
    provider = get_resource_provider()
    data = None
    is_engine_set = True

    if resume or suspend:
        if resume:
            with Spinner("Resuming imports", "Imports resumed", "Error:"):
                provider.change_imports_status(suspend=False)
        if suspend:
            with Spinner("Suspending imports", "Imports suspended", "Error:"):
                provider.change_imports_status(suspend=True)
        exit_with_divider()

    # Passed in engine
    if engine:
        with Spinner("Validating engine", "Engine validated", "Error:"):
                ve = provider.get_engine(engine)
        rich.print()
        if not ve:
            exit_with_error(f"[yellow]Engine[/yellow] '{engine}' [yellow]is invalid.[/yellow]\nPlease use '[cyan]rai engines:create[/cyan]' to create a valid engine.")
        else:
            set_imports_engine(ve.get("name"))
            exit_with_divider()

    # Verify imports setup
    with Spinner("Fetching imports setup", "Imports setup fetched", "Error:"):
        try:
            data = provider.get_imports_status()
        except Exception as e:
            if "SETUP_CDC" in f"{e}":
                is_engine_set = False
            else:
                raise e
    if not is_engine_set:
        rich.print()
        engine = create_engine(cfg, prompt="Select an engine for imports:")
        set_imports_engine(engine)
        exit_with_divider()

    # Engine is already set for imports
    if data:
        rich.print()
        if data["status"].lower() == "suspended":
            rich.print("To resume imports, use '[cyan]rai imports:setup --resume[/cyan]'")
        else:
            rich.print("To suspend imports, use '[cyan]rai imports:setup --suspend[/cyan]'")
        try:
            rich.print()
            with Spinner("Validating imports engine", "Imports engine validated", "Error:"):
                engine = provider.get_engine(data["engine"])
            if not engine:
                rich.print()
                rich.print(f'[yellow]Previously set imports engine[/yellow] "{data["engine"]}" [yellow]is invalid.[/yellow]')
                rich.print()
                engine = create_engine(cfg, prompt="Select an engine for imports:")
                set_imports_engine(engine)
                exit_with_divider()
            data = {**data, **json.loads(data["info"])}
            del data["info"]
            del data["state"]
            data["status"] = data["status"].upper()
            data["createdOn"] = datetime.strptime(data["createdOn"], '%Y-%m-%d %H:%M:%S.%f %z')
            data["lastSuspendedOn"] = datetime.strptime(data["lastSuspendedOn"], '%Y-%m-%d %H:%M:%S.%f %z') if data["lastSuspendedOn"] else "N/A"
            show_dictionary_table(
                data,
                lambda k, v: {k: v, "style": "red"} if k == "engine" and not engine else format_row(k, v)
            )
        except Exception as e:
            exit_with_error(f"\n\n[yellow]Error fetching imports setup: {e}")
    divider()

def set_imports_engine(name:str|None=None):
    cfg = ensure_config()
    provider = get_resource_provider()
    if not name:
        name = controls.fuzzy_with_refetch(
            "Select an engine for imports:",
            "engines",
            lambda: [engine["name"] for engine in provider.list_engines()],
            not_found_message="No valid engines found."
        )
        if not name or isinstance(name, Exception):
            if not name:
                confirm = controls.confirm("Would you like to create a new engine for imports?", default=True)
                if confirm:
                    rich.print()
                    name = create_engine_flow(cfg)
                    rich.print()
                else:
                    return
            else:
                return
    with Spinner("Setting imports engine", "Imports engine set to [cyan]'"+name+"'[/cyan]", "Error:"):
        provider.set_imports_engine(name)

@supports_platform("snowflake")
@cli.command(name="imports:get", help="Get specific import details")
@click.option("--id", help="Filter by import id")
def imports_get(id:str|None=None):
    divider(flush=True)
    ensure_config()
    provider = get_resource_provider()
    import_streams = []
    import_response = []
    with Spinner("Fetching imports", "Imports fetched", "Error:"):
        import_response = provider.list_imports()
        if not import_response:
            exit_with_error("[yellow]No imports found")

    if not id:
        show_imports(import_response, showId=True)
        id = controls.fuzzy("Select an import id:", [i["id"] for i in import_response], default=id, show_index=True)

    details_list = [{"name": item['name'], "model": item['model']} for item in import_response if item['id'] == id]
    if not details_list:
        rich.print()
        exit_with_error(f"[yellow]Import '{id}' not found")

    details = details_list[0]

    rich.print()
    with Spinner("Fetching import details ", "Import details fetched", "Error:"):
        import_streams = provider.get_import_stream(details.get("name"), details.get("model"))
    if len(import_streams) > 0:
        rich.print()
        show_dictionary_table(import_streams[-1], format_row)
    divider()

#--------------------------------------------------
# Imports list
#--------------------------------------------------

@cli.command(name="imports:list", help="List objects imported into RAI")
@click.option("--id", help="Filter by import id")
@click.option("--name", help="Filter by import name")
@click.option("--model", help="Filter by model")
@click.option("--status", help="Filter by import status")
@click.option("--creator", help="Filter by import creator")
def imports_list(id:str|None=None, name:str|None=None, model:str|None=None, status:str|None=None, creator:str|None=None):
    divider(flush=True)
    ensure_config()
    provider = get_resource_provider()
    data = None
    error = None
    with Spinner("Fetching imports config", "Imports config fetched", "Error:"):
        try:
            data = provider.get_imports_status()
        except Exception as e:
            if "SETUP_CDC" in f"{e}":
                error = Exception("Imports are not configured.\n[yellow]To start use '[cyan]rai imports:setup[/cyan]' to set up an engine for imports.")
            else:
                error = e
            raise error
    if isinstance(error, Exception):
        exit_with_divider(1)

    if data:
        rich.print()
        ds = f"[red]{data['status'].upper()}[/red]" if data["status"].lower() == "suspended" else data["status"].upper()
        rich.print(f"Imports status: {ds}")

    imports = None

    rich.print()
    with Spinner("Fetching imports", "Imports fetched", "Error:"):
        imports = provider.list_imports(id, name, model, status, creator)
    if len(imports) == 0:
        exit_with_error("[yellow]No imports found")

    rich.print()
    show_imports(imports)
    divider()

#--------------------------------------------------
# Imports waiting
#--------------------------------------------------

def poll_imports(provider: ResourceProvider, source:str, model:str, no_wait_notice:bool=False):
    spinner = Spinner(
        "Waiting for imports to load "
        "(Ctrl-C to stop waiting - imports will continue loading in the background)",
    )
    with spinner:
        try:
            provider.poll_imports(source, model)
            rich.print("\n\n[green]All imports loaded")
        except KeyboardInterrupt:
            rich.print("\n\n[yellow]Imports will continue loading in the background")
            rich.print(f"[yellow]Use [cyan]rai imports:wait --model {model}[/cyan] to resume waiting")
            if no_wait_notice:
                rich.print("[yellow]Use [cyan]--no-wait[/cyan] to skip waiting")

@cli.command(name="imports:wait", help="Wait for a list of imports to load")
@click.option("--source", help="Imports to wait for", multiple=True, type=str)
@click.option("--model", help="Model", type=str)
def imports_wait(source: List[str], model: str):
    divider(flush=True)
    ensure_config()
    provider = get_resource_provider()

    if not model:
        with Spinner("Fetching models", "Models fetched"):
            try:
                models = [model["name"] for model in provider.list_graphs()]
            except Exception as e:
                exit_with_error(f"\n\n[yellow]Error fetching models: {e}")
        if not models:
            exit_with_error("[yellow]No models found")
        rich.print()
        model = controls.fuzzy("Select a model:", models)
        rich.print()

    if not source:
        with Spinner("Fetching imports", "Imports fetched", "Error:"):
            imports = provider.list_imports(model=model)
        if not imports:
            exit_with_error("[yellow]No imports found")
        def is_loaded(import_):
            status = import_["status"]
            if status is None:
                return False
            return status.upper() == "LOADED"
        loaded_imports = [i for i in imports if is_loaded(i)]
        other_imports = [i for i in imports if not is_loaded(i)]
        if loaded_imports:
            rich.print()
            rich.print("[yellow]The following imports are already loaded:")
            show_imports(loaded_imports)
            if not other_imports:
                rich.print()
                exit_with_error("[yellow]No imports to wait for")
        if not other_imports:
            exit_with_error("[yellow]No imports found")
        rich.print()
        source = controls.fuzzy(
            "Select imports (tab for multiple):",
            [i["name"] for i in other_imports],
            multiselect=True
        )
        if not source:
            exit_with_divider()

    rich.print()
    poll_imports(provider, source, model, no_wait_notice=False)

    divider()

#--------------------------------------------------
# Imports stream
#--------------------------------------------------

@supports_platform("snowflake")
@cli.command(name="imports:stream", help="Stream objects into RAI")
@click.option("--source", help="Source", multiple=True)
@click.option("--model", help="Model")
@click.option("--rate", help="Rate")
@click.option("--resume", help="Name of the import to resume")
@click.option("--suspend", help="Name of the import to suspend")
@click.option("--no-wait", help="Don't wait for imports to load", is_flag=True)
@click.argument('options', nargs=-1, type=ImportOptionsType())
def imports_stream(
    source: Sequence[str],
    model: str|None,
    rate: int|None,
    resume: bool|None,
    suspend: bool|None,
    no_wait: bool|None,
    options: Sequence[ImportOption],
):
    divider(flush=True)
    ensure_config()
    provider = get_resource_provider()
    default_options = ImportOptionsType.reduce(options)

    # Resume or suspend import stream
    if resume or suspend:
        import_name = resume if resume else suspend
        is_suspend = True if suspend else False
        with Spinner("Acquiring import", "Import stream fetched", "Error:"):
            stream = provider.list_imports(name=import_name)
        if not stream:
            rich.print()
            rich.print(f"[yellow]Import '{import_name}' not found")
            exit_with_divider()
        rich.print()
        with Spinner(
            f"{'Resume' if resume else 'Suspend'}ing import stream",
            f"Import stream {'resumed' if resume else 'suspended'}",
            "Error:"
        ):
            provider.change_stream_status(import_name, model=stream[0]["model"], suspend=is_suspend)
        exit_with_divider()

    # Model/database selection & validation
    if not model:
        with Spinner("Fetching models", "Models fetched"):
            try:
                models = ["[CREATE MODEL]"] + [model["name"] for model in provider.list_graphs()]
            except Exception as e:
                exit_with_error(f"\n\n[yellow]Error fetching models: {e}")

        rich.print()
        model = controls.fuzzy("Select a model:", models)
        if model == "[CREATE MODEL]":
            model = controls.text("Model name:")
            rich.print()
            with Spinner("Creating model", "Model created"):
                provider.create_graph(model)
        rich.print()
    else:
        db = provider.get_database(model)
        if not db:
            rich.print()
            with Spinner("Creating model", "Model created"):
                provider.create_graph(model)
    try:
        if not source:
            sources = import_source_flow(provider)
        else:
            sources = [parse_source(provider, source_) for source_ in source]
    except Exception as e:
        exit_with_error(f"[yellow]Error: {e}")

    for import_source in sources:
        try:
            options = import_source_options_flow(provider, import_source, default_options)
            with Spinner(f"Creating stream for {import_source.name}", f"Stream for {import_source.name} created"):
                provider.create_import_stream(import_source, model, rate, options=options)
        except UnsupportedTypeError as err:
            exit_with_error(f"\n\n[yellow]The [bold]{provider.platform}[/bold] integration doesn't support streaming from [bold]'{err.type}'[/bold] sources.")
        except Exception as e:
            if "use setup_cdc()" in f"{e}":
                exit_with_error("\n\n[yellow]Imports are not configured.\n[yellow]To start use '[cyan]rai imports:setup[/cyan]' to set up an engine for imports.")
            elif "stream already exists" in f"{e}":
                exit_with_error(f"\n\n[yellow]Stream [cyan]'{import_source.name.upper()}'[/cyan] already exists.")
            elif "engine not found" in f"{e}":
                exit_with_error("\n\n[yellow]Stream engine not found. Please use '[cyan]rai imports:setup[/cyan]' to set up an engine for imports.")
            else:
                rich.print()
                exit_with_error(f"\n[yellow]Error creating stream: {e}")
    wait = not no_wait
    if wait:
        poll_imports(provider, [source.name for source in sources], model, no_wait_notice=True)
    else:
        rich.print(f"\nRun '[cyan]rai imports:list --model {model}[/cyan]' to check import status.")
        rich.print(f"\nRun '[cyan]rai imports:wait --model {model}[/cyan]' to poll until the imports are loaded.")

    divider()

#--------------------------------------------------
# Imports snapshot
#--------------------------------------------------

@supports_platform("azure")
@cli.command(name="imports:snapshot", help="Load an object once into RAI")
@click.option("--source", help="Source")
@click.option("--model", help="Model")
@click.option("--name", help="Import name")
@click.option("--type", help="Import as type", default="auto", type=click.Choice(["auto", *Loader.type_to_loader.keys()]))
@click.argument('options', nargs=-1, type=ImportOptionsType())
def imports_snapshot(source:str|None, model:str|None, name:str|None, type:str|None, options):
    divider(flush=True)
    ensure_config()
    provider = get_resource_provider()
    default_options = ImportOptionsType.reduce(options)
    default_options["type"] = type

    if not model:
        with Spinner("Fetching models", "Models fetched"):
            try:
                models = [model["name"] for model in provider.list_graphs()]
            except Exception as e:
                exit_with_error(f"\n\n[yellow]Error fetching models: {e}")
        if len(models) == 0:
            exit_with_error("[yellow]No models found")
        rich.print()
        model = controls.fuzzy("Select a model:", models)
        rich.print()

    sources = [parse_source(provider, source)] if source else import_source_flow(provider)
    for import_source in sources:
        try:
            import_source.name = name if name else controls.text("name:", import_source.name)
            options = import_source_options_flow(provider, import_source, default_options)
            with Spinner(f"Creating snapshot for {import_source.name}", f"Snapshot for {import_source.name} created"):
                provider.create_import_snapshot(import_source, model, options=options)
        except UnsupportedTypeError as err:
            exit_with_error(f"\n\n[yellow]The [bold]{provider.platform}[/bold] integration doesn't support loading [bold]'{err.type}'[/bold] files.")
        except RelQueryError as e:
            exit_with_error(f"\n\n[yellow]Error creating snapshot: {e.pprint()}")
        except Exception as e:
            exit_with_error(f"\n\n[yellow]Error creating snapshot: {e}")
    divider()

#--------------------------------------------------
# Imports delete
#--------------------------------------------------

@cli.command(name="imports:delete", help="Delete an import from RAI")
@click.option("--object", help="Object")
@click.option("--model", help="Model")
def imports_delete(object, model):
    divider(flush=True)
    ensure_config()
    provider = cast(snowflake.Resources, get_resource_provider())
    if not model:
        with Spinner("Fetching models", "Models fetched"):
            try:
                models = [model["name"] for model in provider.list_graphs()]
            except Exception as e:
                exit_with_error(f"\n\n[yellow]Error fetching models: {e}")
        if len(models) == 0:
            rich.print()
            exit_with_error("[yellow]No models found")
        rich.print()
        model = controls.fuzzy("Select a model:", models)
        rich.print()

    with Spinner(f"Fetching imports for {model}", "Imports fetched"):
        try:
            imports = provider.list_imports(model=model)
        except Exception as e:
            exit_with_error(f"\n\n[yellow]Error fetching imports: {e}")

    if not imports:
        rich.print()
        exit_with_error("[yellow]No imports to delete")
    if object:
        objects = [object]
    else:
        if len(imports) == 0:
            exit_with_error("[yellow]No imports found")
        rich.print()
        objects = controls.fuzzy("Select objects (tab for multiple):", [t["name"] for t in imports], multiselect=True)
        rich.print()

    for object in objects:
        with Spinner(f"Removing {object}", f"{object} removed"):
            try:
                provider.delete_import(object, model)
            except Exception as e:
                exit_with_error(f"\n\n[yellow]Error deleting import: {e}")
    divider()

#--------------------------------------------------
# Exports list
#--------------------------------------------------

@supports_platform("snowflake")
@cli.command(name="exports:list", help="List objects exported out of RAI")
@click.option("--model", help="Model")
def exports_list(model):
    divider(flush=True)
    ensure_config()
    provider = cast(snowflake.Resources, get_resource_provider())
    coming_soon()
    if not model:
        with Spinner("Fetching models", "Models fetched"):
            try:
                models = [model["name"] for model in provider.list_graphs()]
            except Exception as e:
                exit_with_error(f"\n\n[yellow]Error fetching models: {e}")
        if len(models) == 0:
            exit_with_error("[yellow]No models found")
        rich.print()
        model = controls.fuzzy("Select a model:", models)
        rich.print()

    with Spinner(f"Fetching exports for {model}", "Exports fetched"):
        try:
            exports = provider.list_exports(model, "")
        except Exception as e:
            exit_with_error(f"\n\n[yellow]Error fetching exports: {e}")

    rich.print()
    if len(exports):
        table = Table(show_header=True, border_style="dim", header_style="bold", box=rich_box.SIMPLE_HEAD)
        table.add_column("Object")
        for imp in exports:
            table.add_row(imp.get("name"))
        rich.print(table)
    else:
        rich.print("[yellow]No exports found")
    divider()

#--------------------------------------------------
# Exports delete
#--------------------------------------------------

@supports_platform("snowflake")
@cli.command(name="exports:delete", help="Delete an export from RAI")
@click.option("--export", help="export")
@click.option("--model", help="Model")
def exports_delete(export, model):
    divider(flush=True)
    ensure_config()
    provider = cast(snowflake.Resources, get_resource_provider())
    coming_soon()
    if not model:
        with Spinner("Fetching models", "Models fetched"):
            try:
                models = [model["name"] for model in provider.list_graphs()]
            except Exception as e:
                exit_with_error(f"\n\n[yellow]Error fetching models: {e}")
        if len(models) == 0:
            exit_with_error("[yellow]No models found")
        rich.print()
        model = controls.fuzzy("Select a model:", models)
        rich.print()

    # @FIXME It seems like we should just fuzzy list exports but this was the original behavior
    source_names = [export] if export else [source.name for source in import_source_flow(provider)]
    for source_name in source_names:
        with Spinner(f"Removing {source_name}", f"{source_name} removed"):
            try:
                provider.delete_export(model, "", source_name)
            except Exception as e:
                rich.print(f"\n\n[yellow]Error deleting export: {e}")
    divider()

#--------------------------------------------------
# Transactions get
#--------------------------------------------------

@cli.command(name="transactions:get", help="Get transaction details")
@click.option("--id", help="Transaction id")
def transactions_get(id):
    divider()
    ensure_config()
    provider = get_resource_provider()
    transaction = None
    if not id:
        id = controls.text("Transaction id:", mandatory=True, validator=UUID.match, invalid_message="Invalid transaction id")
        rich.print("")

    with Spinner("Fetching transaction", "Transaction fetched"):
        try:
            transaction = provider.get_transaction(id)
        except Exception as e:
            exit_with_error(f"\n\n[yellow]Error fetching transaction: {e}")
    rich.print()
    if transaction:
        show_dictionary_table(transaction, format_row)
    divider()

#--------------------------------------------------
# Transactions list
#--------------------------------------------------

@cli.command(name="transactions:list", help="List transactions")
@click.option("--id", help="Filter by transaction id", type=str)
@click.option("--state", help="Filter by transaction state", type=str)
@click.option("--engine", help="Filter by transaction engine", type=str)
@click.option("--limit", default=20, help="Limit", type=int)
@click.option("--all-users", is_flag=True, default=False, help="Show transactions from all users")
def transactions_list(id, state, engine, limit, all_users):
    divider()
    cfg = ensure_config()
    provider = get_resource_provider()
    with Spinner("Fetching transactions", "Transactions fetched"):
        try:
            transactions = provider.list_transactions(
                id=id,
                state=state,
                engine=engine,
                limit=max(limit, 100),
                all_users=all_users,
                created_by=cfg.get("user", None),
            )
        except Exception as e:
            exit_with_error(f"\n\n[yellow]Error fetching transactions: {e}\n")

    if len(transactions) == 0:
        exit_with_error("[yellow]No transactions found")

    rich.print()
    show_transactions(transactions, limit)
    divider()

#--------------------------------------------------
# Transaction cancel
#--------------------------------------------------

@cli.command(name="transactions:cancel", help="Cancel a transaction")
@click.option("--id", help="Transaction ID")
@click.option("--all-users", is_flag=True, help="Show transactions from all users")
def transactions_cancel(id, all_users):
    divider()
    cfg = ensure_config()
    provider = get_resource_provider()
    if id is None:
        with Spinner("Fetching transactions", "Transactions fetched"):
            try:
                transactions = provider.list_transactions(
                    limit=20,
                    only_active=True,
                    all_users=all_users,
                    created_by=cfg.get("user", None),
                )
            except Exception as e:
                exit_with_error(f"\n\n[yellow]Error fetching transactions: {e}")

        if not transactions:
            exit_with_error("\n[yellow]No active transactions found")

        show_transactions(transactions, 20)

        id = controls.fuzzy("Select a transaction to cancel:", [t["id"] for t in transactions])
        print()

    with Spinner("Cancelling transaction", "Transaction cancelled", "Error:"):
        provider.cancel_transaction(id)
    divider()

#--------------------------------------------------
# Main
#--------------------------------------------------

if __name__ == "__main__":
    # app = EventApp()
    # app.run()
    cli()
