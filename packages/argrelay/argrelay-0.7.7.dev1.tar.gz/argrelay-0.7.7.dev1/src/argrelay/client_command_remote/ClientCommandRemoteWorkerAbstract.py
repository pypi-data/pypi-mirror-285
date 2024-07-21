import os

from argrelay.client_command_remote.ClientCommandRemoteAbstract import ClientCommandRemoteAbstract
from argrelay.client_pipeline import BytesSrcAbstract
from argrelay.enum_desc.ClientExitCode import ClientExitCode
from argrelay.enum_desc.ProcRole import ProcRole
from argrelay.enum_desc.TopDir import TopDir
from argrelay.misc_helper_common import get_argrelay_dir
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
from argrelay.server_spec.CallContext import CallContext

connection_index_file_name = "argrelay_client.connection_index"


def get_var_dir_path() -> str:
    return str(os.path.join(get_argrelay_dir(), TopDir.var_dir.value))


def get_connection_index_file_path() -> str:
    return str(os.path.join(get_var_dir_path(), connection_index_file_name))


class ClientCommandRemoteWorkerAbstract(ClientCommandRemoteAbstract):

    def __init__(
        self,
        call_ctx: CallContext,
        proc_role: ProcRole,
        redundant_connections: list[ConnectionConfig],
        bytes_src: BytesSrcAbstract,
    ):
        super().__init__(
            call_ctx,
            proc_role,
        )
        self.redundant_connections: list[ConnectionConfig] = redundant_connections
        self.bytes_src: BytesSrcAbstract = bytes_src
        self.curr_connection_config: ConnectionConfig = self.redundant_connections[0]

        self.connection_index_file_path: str = get_connection_index_file_path()

    def execute_command(
        self,
    ):
        """
        Implements FS_93_18_57_91 client fail over.
        """
        connections_count = len(self.redundant_connections)
        init_connection_index = self.__load_connection_index()
        for curr_connection_offset in range(connections_count):
            curr_connection_index = (init_connection_index + curr_connection_offset) % connections_count
            self.curr_connection_config = self.redundant_connections[curr_connection_index]

            try:
                self._execute_remotely()
                self.__store_connection_index(curr_connection_index)
                return
            except (
                ConnectionError,
                ConnectionRefusedError,
            ) as e:
                continue

        if self.proc_role is ProcRole.ChildProcWorker:
            # Tell parent what happened (let parent talk the rest):
            exit(ClientExitCode.ConnectionError.value)
        else:
            raise ConnectionError(f"Unable to connect to any of [{connections_count}] configured connections")

    def __load_connection_index(
        self,
    ) -> int:

        if os.path.isfile(self.connection_index_file_path):
            with open(self.connection_index_file_path, "r") as open_file:
                return int(open_file.read())
        else:
            return 0

    def __store_connection_index(
        self,
        curr_connection_index: int,
    ) -> None:
        os.makedirs(
            get_var_dir_path(),
            exist_ok = True,
        )
        with open(self.connection_index_file_path, "w") as open_file:
            open_file.write(str(curr_connection_index))
