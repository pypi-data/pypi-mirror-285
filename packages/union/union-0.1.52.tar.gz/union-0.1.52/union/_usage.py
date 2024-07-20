"""Module to track usage and errors."""

import logging
from functools import partial
from os import getenv
from pathlib import Path
from typing import Any

import click
import flytekit
from flytekit.clis.sdk_in_container.utils import get_level_from_cli_verbosity, pretty_print_exception
from flytekit.exceptions.base import FlyteException
from flytekit.loggers import upgrade_to_rich_logging
from importlib_metadata import version
from rich_click.rich_command import RichGroup

import union

SENTRY_DSN = "https://8a7049a7fe42d7fe7b12e1b0d2171d21@o4507249423810560.ingest.us.sentry.io/4507249829281792"
SENTRY_DEBUG_DSN = "https://f9933bb58495729cffc5f6b97ea8502e@o4507249423810560.ingest.us.sentry.io/4507249428201472"
UNION_USAGE_STATS_ENABLED_ENV = "UNION_USAGE_STATS_ENABLED"
UNION_DEBUG_USAGE_STATS_ENV = "UNION_DEBUG_USAGE_STATS"


# Re-implementation of ErrorHandlingCommand.invoke to send error to sentry first
# Details: ErrorHandlingCommand.invoke captures the error and calls exit(1). This means
# we need to override `ErrorHandlingCommand.invoke` and capture the exceptions before
# `exit(1)`
# https://github.com/flyteorg/flytekit/blob/db2ff9e4e14bdcec2c96388af33f0a3357459fe0/flytekit/clis/sdk_in_container/utils.py#L123-L141
def custom_invoke(ctx: click.Context, self) -> Any:
    verbose = ctx.params["verbose"]
    log_level = get_level_from_cli_verbosity(verbose)
    upgrade_to_rich_logging(log_level=log_level)
    try:
        return RichGroup.invoke(self, ctx)
    except Exception as e:
        import sentry_sdk

        sentry_sdk.capture_exception(e)

        if verbose > 0:
            click.secho("Verbose mode on")
            if isinstance(e, FlyteException):
                raise e.with_traceback(None)
            raise e
        pretty_print_exception(e)
        exit(1)


# Only show exceptions caused by unionai and flytekit.clients
PACKAGE_PATHS_TO_TRACK = union.__path__ + flytekit.clients.__path__


def _sentry_exit_callback(pending, timeout):
    """Silence 'Sentry is attempted to send... message"""
    pass


def _filter_exceptions(event, hint):
    """Filter out exceptions that are not from the unionai SDK."""
    try:
        source = event.get("exception") or event.get("threads")

        # Ignore events without a stack trace
        if source is None:
            return None

        last_frame = source["values"][0]["stacktrace"]["frames"][-1]
        exc_origin_path = last_frame["abs_path"]

        if not any(exc_origin_path.startswith(p) for p in PACKAGE_PATHS_TO_TRACK):
            return None
    except Exception:
        return None

    return event


def _configure_tracking_cli(main: click.Group) -> click.Group:
    """Configures the the unionai to catch exceptions."""
    main.invoke = partial(custom_invoke, self=main)
    _init_tracking()
    return main


def _init_tracking():
    """Initializes tracking."""
    # Check if this is a development environment
    unionai_git_path = Path(union.__path__[0]).parent / ".git"
    in_dev_env = unionai_git_path.exists()

    # If UNIONAI_DEBUG_SENTRY_ENV != "0", then enable user stats for development.
    # If UNIONAI_DEBUG_SENTRY_ENV == "0", then disable user stats for development. (Default)
    enable_tracking_for_dev = getenv(UNION_DEBUG_USAGE_STATS_ENV, "0") != "0" and in_dev_env

    # If UNION_USAGE_STATS_ENABLED_ENV != "0", then enable user stats collection. (Default)
    # If UNION_USAGE_STATS_ENABLED_ENV == "0", then disable user stats collection.
    enable_usage_stats = getenv(UNION_USAGE_STATS_ENABLED_ENV, "1") != "0" and enable_tracking_for_dev

    if not enable_usage_stats:
        return

    import sentry_sdk
    from sentry_sdk.integrations.atexit import AtexitIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_logging = LoggingIntegration(
        level=logging.DEBUG,  # Capture debug and above as breadcrumbs
        event_level=logging.ERROR,  # Send errors as events
    )

    if enable_tracking_for_dev:
        # Use debug DSN for development, so we do not put these errors into the production tracker
        dsn = SENTRY_DEBUG_DSN
        release = "dev"
        environment = "development"
    else:
        dsn = SENTRY_DSN
        release = version("union")
        environment = "production"

    sentry_sdk.init(
        dsn=dsn,
        auto_enabling_integrations=False,
        before_send=_filter_exceptions,
        integrations=[AtexitIntegration(callback=_sentry_exit_callback), sentry_logging],
        enable_tracing=False,
        release=release,
        environment=environment,
        debug=enable_tracking_for_dev,
    )
