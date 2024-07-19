# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

from pathlib import Path

from ._version import __version__
from .application_base import JupyterKernelsBaseApp

from .kernels.about.aboutapp import KernelAboutApp
from .kernels.console.consoleapp import KernelConsoleApp
from .kernels.create.createapp import KernelCreateApp
from .kernels.exec.execapp import KernelExecApp
from .kernels.list.listapp import KernelListApp
from .kernels.login.loginapp import KernelLoginApp
from .kernels.logout.logoutapp import KernelLogoutApp
from .kernels.pause.pauseapp import KernelPauseApp
from .kernels.envs.envssapp import KernelEnvironmentsApp
from .kernels.start.startapp import KernelStartApp
from .kernels.stop.stopapp import KernelStopApp
from .kernels.terminate.terminateapp import KernelTerminateApp
from .kernels.whoami.whoamiapp import KernelWhoamiApp


HERE = Path(__file__).parent


class JupyterKernelsApp(JupyterKernelsBaseApp):
    description = """
      The Jupyter Kernels application.
    """

    _requires_auth = False


    subcommands = {
        "about": (KernelAboutApp, KernelAboutApp.description.splitlines()[0]),
        "console": (
            KernelConsoleApp,
            KernelConsoleApp.description.splitlines()[0],
        ),
        "create": (KernelCreateApp, KernelCreateApp.description.splitlines()[0]),
        "exec": (KernelExecApp, KernelExecApp.description.splitlines()[0]),
        "list": (KernelListApp, KernelListApp.description.splitlines()[0]),
        "login": (KernelLoginApp, KernelLoginApp.description.splitlines()[0]),
        "logout": (KernelLogoutApp, KernelLogoutApp.description.splitlines()[0]),
        "pause": (KernelPauseApp, KernelPauseApp.description.splitlines()[0]),
        "envs": (KernelEnvironmentsApp, KernelEnvironmentsApp.description.splitlines()[0]),
        "start": (KernelStartApp, KernelStartApp.description.splitlines()[0]),
        "stop": (KernelStopApp, KernelStopApp.description.splitlines()[0]),
        "terminate": (
            KernelTerminateApp,
            KernelTerminateApp.description.splitlines()[0],
        ),
        "whoami": (KernelWhoamiApp, KernelWhoamiApp.description.splitlines()[0]),
    }


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------


main = launch_new_instance = JupyterKernelsApp.launch_instance


if __name__ == "__main__":
    main()
