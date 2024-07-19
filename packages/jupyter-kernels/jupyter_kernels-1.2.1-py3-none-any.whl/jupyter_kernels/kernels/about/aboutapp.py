# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

from pathlib import Path

from datalayer.application import NoStart
from rich.console import Console
from rich.markdown import Markdown

from ...application_base import JupyterKernelsBaseApp


HERE = Path(__file__).parent


class KernelAboutApp(JupyterKernelsBaseApp):
    """Kernel About application."""

    description = """
      An application to print useful information
      about jupyter kernels.
    """

    _requires_auth = False


    def start(self):
        try:
            super().start()
            console = Console()
            with open(HERE / "about.md") as readme:
                markdown = Markdown(readme.read())
            console.print(markdown)
        except NoStart:
            pass
        self.exit(0)
