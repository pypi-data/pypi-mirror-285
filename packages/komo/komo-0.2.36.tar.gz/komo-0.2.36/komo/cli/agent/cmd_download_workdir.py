import os

import click

from komo import printing
from komo.agent.core import download_workdir


@click.command("download-workdir")
@click.option("--upload-id", type=str, required=True)
def cmd_download_workdir(
    upload_id: str,
):
    download_workdir(
        upload_id,
        os.getcwd(),
    )
    printing.success(f"Workdir {upload_id} successfully downloaded")
