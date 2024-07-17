import asyncio
import inspect
from functools import wraps

import click
import typer

from launchflow.cli import posthog


class UTyper(typer.Typer):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("pretty_exceptions_enable", False)
        super().__init__(*args, **kwargs)

    def command(self, *args, **kwargs):
        decorator = super().command(*args, **kwargs)

        def add_runner(f):
            @wraps(f)
            def runner(*args, **kwargs):
                try:
                    if inspect.iscoroutinefunction(f):
                        results = asyncio.run(f(*args, **kwargs))
                    else:
                        results = f(*args, **kwargs)
                    return results
                finally:
                    ctx = click.get_current_context()
                    root = ctx
                    while root.parent is not None:
                        root = root.parent
                    disable = root.params.get("disable_usage_statistics", False)
                    if not disable:
                        split_cmd = ctx.command_path.split(" ")
                        cmd = "_".join(split_cmd)
                        posthog.record_event(cmd)

            return decorator(runner)

        return add_runner
