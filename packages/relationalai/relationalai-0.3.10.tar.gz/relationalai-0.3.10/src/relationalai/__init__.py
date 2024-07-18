from __future__ import annotations
import importlib.metadata
from .clients import config as cfg
from . import clients
from . import dsl
from . import debugging
from . import metamodel
from . import rel
from .loaders import csv
from . import analysis
from . import tools
from . import dependencies
from snowflake.connector import SnowflakeConnection
from .errors import RAIException

# Set up global exception handler for debugging
debugging.setup_exception_handler()
debugging.install_warninghook()

__version__ = importlib.metadata.version(__package__ or __name__)

def Model(
    name: str,
    *,
    profile: str | None = None,
    config: cfg.Config | None = None,
    dry_run: bool = False,
    debug: bool | None = None,
    connection: SnowflakeConnection | None = None,
    keep_model: bool = None,
    isolated: bool = None,
    nowait_durable: bool = None,
    format: str = "default",
):
    config = config or cfg.Config(profile=profile)
    if debug is None:
        debug = config.get("debug", False)
    if debug:
        from relationalai.tools.debugger_client import start_debugger_session
        start_debugger_session(config) # @TODO: add config / env vars / kwargs for debug_host and debug_port
    if not config.file_path:
        if cfg.legacy_config_exists():
            message = (
                "Use `rai init` to migrate your configuration file "
                "to the new format (raiconfig.toml)"
            )
        else:
            message = "No configuration file found. Please run `rai init` to create one."
        raise Exception(message)
    if config.get("platform") is None:
        config.set("platform", "snowflake")
    platform = config.get("platform")
    if platform != "snowflake" and connection is not None:
        raise ValueError("The `connection` parameter is only supported with the Snowflake platform")
    if dry_run is None:
        dry_run = config.get("compiler.dry_run", False)
    if keep_model is None:
        keep_model = config.get("model.keep", False)
    if isolated is None:
        isolated = config.get("model.isolated", True)
    if nowait_durable is None:
        nowait_durable = config.get("model.nowait_durable", True)

    try:
        if platform == "azure":
            model = clients.azure.Graph(
                name,
                profile=profile,
                config=config,
                dry_run=dry_run,
                isolated=isolated,
                keep_model=keep_model,
                format=format,
            )
        elif platform == "snowflake":
            model = clients.snowflake.Graph(
                name,
                profile=profile,
                config=config,
                dry_run=dry_run,
                isolated=isolated,
                connection=connection,
                keep_model=keep_model,
                nowait_durable=nowait_durable,
                format=format,
            )
        else:
            raise Exception(f"Unknown platform: {platform}")
    except RAIException as e:
        raise e.clone() from None
    model._client.exec_control(dependencies.generate_query(), lambda res: dependencies.check_dependencies(res, platform, config, name))
    return model

def Resources(profile:str|None=None, config:cfg.Config|None=None):
    config = config or cfg.Config(profile)
    platform = config.get("platform", "snowflake")
    if platform == "azure":
        return clients.azure.Resources(config=config)
    elif platform == "snowflake":
        return clients.snowflake.Resources(config=config)
    else:
        raise Exception(f"Unknown platform: {platform}")

def Graph(name:str, dry_run:bool=False):
    return Model(name, profile=None, dry_run=dry_run)

__all__ = ['Model', 'Resources', 'dsl', 'rel', 'debugging', 'metamodel', 'csv', 'analysis', 'tools']
