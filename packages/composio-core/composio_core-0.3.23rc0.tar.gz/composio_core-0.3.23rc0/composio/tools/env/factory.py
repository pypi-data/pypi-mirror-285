import atexit
import threading
import typing as t
from enum import Enum

from composio.exceptions import ComposioSDKError
from composio.tools.env.base import Workspace
from composio.tools.env.docker.workspace import DockerWorkspace
from composio.tools.env.e2b.workspace import E2BWorkspace
from composio.tools.env.flyio.workspace import FlyIOWorkspace
from composio.tools.env.host.workspace import HostWorkspace
from composio.utils.logging import get as get_logger


class ExecEnv(Enum):
    """Workspace execution environment."""

    HOST = "host"
    DOCKER = "docker"
    FLYIO = "flyio"
    E2B = "e2b"


class WorkspaceFactory:
    """Workspace factory class."""

    _recent: Workspace
    """Most recently used workspace"""

    _workspaces: t.Dict[str, Workspace] = {}
    """Collection of workspaces"""

    _lock: threading.Lock = threading.Lock()
    """Lock for `_recent`"""

    @classmethod
    def get_recent_workspace(cls) -> Workspace:
        """Get most recent workspace."""
        with cls._lock:
            return cls._recent

    @classmethod
    def set_recent_workspace(cls, workspace: Workspace) -> Workspace:
        """Get most recent workspace."""
        with cls._lock:
            cls._recent = workspace
        return workspace

    @classmethod
    def new(cls, wtype: ExecEnv, **kwargs: t.Any) -> Workspace:
        """Create a new workspace."""
        get_logger().debug(f"Creating workspace with {wtype=} and {kwargs=}")
        workspace: Workspace
        if wtype == ExecEnv.HOST:
            workspace = HostWorkspace(**kwargs)
        elif wtype == ExecEnv.DOCKER:
            workspace = DockerWorkspace(**kwargs)
        elif wtype == ExecEnv.E2B:
            workspace = E2BWorkspace(**kwargs)
        else:
            workspace = FlyIOWorkspace(**kwargs)

        cls._workspaces[workspace.id] = workspace
        workspace.setup()
        return cls.set_recent_workspace(workspace=workspace)

    @classmethod
    def get(cls, id: t.Optional[str] = None) -> Workspace:
        """Get workspace by `id` or the most recent one."""
        if id is None:
            return cls.get_recent_workspace()

        if id not in cls._workspaces:
            raise ComposioSDKError(f"Workspace with ID: {id} not found.")

        workspace = cls._workspaces[id]
        return cls.set_recent_workspace(workspace=workspace)

    @classmethod
    def close(cls, id: str) -> None:
        """Teardown the workspace with given ID."""
        if id not in cls._workspaces:
            return
        cls._workspaces[id].teardown()

    @classmethod
    def teardown(cls) -> None:
        """Teardown the workspace factory."""
        for workspace in cls._workspaces.values():
            get_logger(name="factory").debug("Tearing down %s", workspace)
            workspace.teardown()


@atexit.register
def _teardown() -> None:
    """Teardown the workspace factory at exit."""
    logger = get_logger(name="atexit")
    logger.debug("Tearing down workspace factory")
    WorkspaceFactory.teardown()
