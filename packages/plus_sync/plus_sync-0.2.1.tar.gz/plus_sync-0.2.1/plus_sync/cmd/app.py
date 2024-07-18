from typing import Annotated

import typer

from plus_sync.cmd.helpers.options import global_options

app = typer.Typer(no_args_is_help=True, rich_markup_mode='rich')


@app.callback()
def set_config_file(
    config_file: Annotated[
        str,
        typer.Option(
            help='The configuration file to use.',
            envvar='PLUS_SYNC_CONFIG_FILE',
        ),
    ] = 'plus_sync.toml',
):
    """
    Sync data between Gitlab and SinuheMEG or anything else that can be
    reached via gitlab, SFTP or rsync.

    Enter plus_sync init to get started.
    """
    global_options['config_file'] = config_file
