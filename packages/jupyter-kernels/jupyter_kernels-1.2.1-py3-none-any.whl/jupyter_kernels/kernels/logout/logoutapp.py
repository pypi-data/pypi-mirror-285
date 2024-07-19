# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

import warnings

from ...application_base import JupyterKernelsBaseApp


class KernelLogoutApp(JupyterKernelsBaseApp):
    """An application to logout of a remote kernel provider."""

    description = """
      An application to logout of a remote kernel provider.

      jupyter kernels logout
    """

    _requires_auth = False


    def start(self):
        """Start the app."""
        if len(self.extra_args) > 0:  # pragma: no cover
            warnings.warn("Too many arguments were provided for logout.")
            self.print_help()
            self.exit(1)
        """
        FIXME
        self._fetch(
            "{}/api/iam/v1/logout".format(self.kernels_url),
        )
        """

        self._log_out()
        self.log.info("Successfully logged out.")
