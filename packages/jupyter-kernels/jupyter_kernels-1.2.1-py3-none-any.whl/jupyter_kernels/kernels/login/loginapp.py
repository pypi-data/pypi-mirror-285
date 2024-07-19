# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

import warnings

from ...application_base import JupyterKernelsBaseApp


class KernelLoginApp(JupyterKernelsBaseApp):
    """An application to log into a remote kernel provider."""

    description = """
      An application to log into a remote kernel provider.

      jupyter kernels login
    """

    def start(self):
        """Start the app."""
        if len(self.extra_args) > 0:  # pragma: no cover
            warnings.warn("Too many arguments were provided for login.")
            self.print_help()
            self.exit(1)

        if self.token and self.username:
            self.log.info("Successfully logged in.")
