"""SemSpect Workflow Task"""

from collections.abc import Sequence
from time import sleep
from urllib.parse import quote

from cmem.cmempy.config import get_dp_api_endpoint
from cmem_plugin_base.dataintegration.context import ExecutionContext, ExecutionReport
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginParameter
from cmem_plugin_base.dataintegration.entity import (
    Entities,
)
from cmem_plugin_base.dataintegration.parameter.graph import GraphParameterType
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import FixedNumberOfInputs
from cmem_plugin_base.dataintegration.utils import setup_cmempy_user_access

from cmem_plugin_semspect.api import Client


@Plugin(
    label="Update SemSpect",
    description="Tell SemSpect to prepare a Knowledge Graph for visualization.",
    icon=Icon(package=__package__, file_name="logo.svg"),
    parameters=[
        PluginParameter(
            name="base_url",
            label="The URL of the SemSpect application."
            "This needs to be accessible from 'within' DataIntegration.",
            default_value="http://semspect:8080/semspect/",
        ),
        PluginParameter(
            name="database_id",
            label="The SemSpect database ID. Not existing databases will be created.",
            default_value="cmem",
        ),
        PluginParameter(
            name="graph",
            label="Knowledge Graph",
            param_type=GraphParameterType(
                show_di_graphs=True,
                show_graphs_without_class=True,
                show_system_graphs=True,
                allow_only_autocompleted_values=True,
            ),
        ),
        PluginParameter(
            name="dataplatform_base",
            label="The URL of the DataPlatform application."
            "This needs to be accessible from 'within' SemSpect.",
            default_value="",
            advanced=True,
        ),
        PluginParameter(
            name="timeout", label="Timeout (in seconds)", default_value="100", advanced=True
        ),
    ],
)
class Update(WorkflowPlugin):
    """Tell SemSpect to fetch and index a dataset"""

    client: Client

    def __init__(  # noqa: PLR0913
        self, base_url: str, database_id: str, graph: str, dataplatform_base: str, timeout: int
    ) -> None:
        self.base_url = base_url
        self.client = Client(base_url=base_url)
        self.database_id = database_id
        self.graph = graph
        self.dataplatform_base = dataplatform_base
        if int(timeout) < 1:
            raise ValueError("Timeout must be greater than 0")
        self.timeout = int(timeout)
        self._set_ports()

    def execute(
        self,
        inputs: Sequence[Entities],  # noqa: ARG002
        context: ExecutionContext,
    ) -> None:
        """Run the workflow operator."""
        self.log.info("Start")
        setup_cmempy_user_access(context.user)
        if not self.client.is_database(database_id=self.database_id):
            self.client.create_database(database_id=self.database_id)
        database = self.client.get_database(self.database_id)
        download_url = self._get_download_url(token=context.user.token())
        operation = self.client.update_database(
            database=database, url=download_url, description="update"
        )
        max_tries = self.timeout
        while True:
            max_tries -= 1
            operation = self.client.get_operation(operation_id=operation.id)
            context.report.update(
                ExecutionReport(
                    entity_count=1,
                    operation="wrote",
                    operation_desc=f"database update ({operation.status})",
                )
            )
            if operation.status == "done":
                break
            if operation.status == "failed":
                raise ValueError("Database update failed.")
            if max_tries == 0:
                raise ValueError("Database update timeout.")
            sleep(1)
        self.log.info("End")

    def _get_download_url(self, token: str) -> str:
        """Get the graph store download url"""
        url: str = self.dataplatform_base if self.dataplatform_base != "" else get_dp_api_endpoint()
        url += f"/proxy/default/graph?graph={quote(self.graph)}"
        url += "&owlImportsResolution=true"
        url += "&access_token=" + quote(token)
        return url

    def _set_ports(self) -> None:
        """Define input/output ports"""
        self.input_ports = FixedNumberOfInputs([])
        self.output_port = None
