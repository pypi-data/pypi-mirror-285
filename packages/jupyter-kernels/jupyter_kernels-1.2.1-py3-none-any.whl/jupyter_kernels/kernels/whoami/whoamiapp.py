# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

import warnings

from ...application_base import JupyterKernelsBaseApp
from ..utils import display_me


class KernelWhoamiApp(JupyterKernelsBaseApp):
    """An application to list the kernels."""

    description = """
      An application to list the kernels.

      jupyter kernels list
    """

    def start(self):
        """Start the app."""
        if len(self.extra_args) > 0:  # pragma: no cover
            warnings.warn("Too many arguments were provided for kernel list.")
            self.print_help()
            self.exit(1)

        response = self._fetch(
            "{}/api/iam/v1/whoami".format(self.kernels_url),
        )
        raw = response.json()
        display_me(raw.get("profile", {}))
