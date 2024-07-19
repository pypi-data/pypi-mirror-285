# Copyright (C) 2023-Present DAGWorks Inc.
#
# For full terms email support@dagworks.io.
#
# This software and associated documentation files (the "Software") may only be
# used in production, if you (and any entity that you represent) have agreed to,
# and are in compliance with, the DAGWorks Enterprise Terms of Service, available
# via email (support@dagworks.io) (the "Enterprise Terms"), or other
# agreement governing the use of the Software, as agreed by you and DAGWorks,
# and otherwise have a valid DAGWorks Enterprise license for the
# correct number of seats and usage volume.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import logging
from typing import Callable, Optional, Dict, Any, List

from hamilton import node
from hamilton import graph as h_graph
from hamilton_sdk import adapters

from dagworks.api import constants
from dagworks.api import clients

import os


logger = logging.getLogger(__name__)


def get_node_name(node_: node.Node, task_id: Optional[str]) -> str:
    if task_id is not None:
        return f"{task_id}-{node_.name}"
    return node_.name


LONG_SCALE = float(0xFFFFFFFFFFFFFFF)


class DAGWorksTracker(adapters.HamiltonTracker):
    """This class extends the OS tracker and adds minor things."""

    def __init__(
        self,
        project_id: int,
        api_key: str,
        username: str,
        dag_name: str,
        tags: Dict[str, str] = None,
        client_factory: Callable[
            [str, str, str], clients.DAGWorksClient
        ] = clients.BasicSynchronousDAGWorksClient,
        hamilton_api_url=os.environ.get("DAGWORKS_API_URL", constants.DAGWORKS_API_URL),
        hamilton_ui_url=os.environ.get("DAGWORKS_UI_URL", constants.DAGWORKS_UI_URL),
    ):
        """This hooks into Hamilton execution to track DAG runs in DAGWorks.

        :param project_id: the ID of the project
        :param api_key: the API key to use.
        :param username: the username for the API key.
        :param dag_name: the name of the DAG.
        :param tags: any tags to help curate and organize the DAG
        :param client_factory: a factory to create the client to phone DAGWorks with.
        :param dagworks_api_url: API endpoint.
        :param dagworks_ui_url: UI Endpoint.
        """
        super(DAGWorksTracker, self).__init__(
            project_id=project_id,
            api_key=api_key,
            username=username,
            dag_name=dag_name,
            tags=tags,
            client_factory=client_factory,
            hamilton_api_url=hamilton_api_url,
            hamilton_ui_url=hamilton_ui_url,
        )

    def pre_graph_execute(
        self,
        run_id: str,
        graph: h_graph.FunctionGraph,
        final_vars: List[str],
        inputs: Dict[str, Any],
        overrides: Dict[str, Any],
    ):
        """Creates a DAG run."""
        # need this because client requested this feature. Injecting things into the inputs.
        dw_run_id = super().pre_graph_execute(run_id, graph, final_vars, inputs, overrides)
        dw_run_url = f"{self.hamilton_ui_url}/dashboard/project/{self.project_id}/runs/{dw_run_id}"
        if inputs is not None:
            inputs["__dw_run_id"] = dw_run_id
            inputs["__dw_run_url"] = dw_run_url


class AsyncDAGWorksAdapter(adapters.HamiltonTracker):
    def __init__(
        self,
        project_id: int,
        api_key: str,
        username: str,
        dag_name: str,
        tags: Dict[str, str] = None,
        client_factory: Callable[
            [str, str, str], clients.DAGWorksClient
        ] = clients.BasicAsynchronousDAGWorksClient,
        hamilton_api_url=os.environ.get("DAGWORKS_API_URL", constants.DAGWORKS_API_URL),
        hamilton_ui_url=os.environ.get("DAGWORKS_UI_URL", constants.DAGWORKS_UI_URL),
    ):
        super(AsyncDAGWorksAdapter, self).__init__(
            project_id=project_id,
            api_key=api_key,
            username=username,
            dag_name=dag_name,
            tags=tags,
            client_factory=client_factory,
            hamilton_api_url=hamilton_api_url,
            hamilton_ui_url=hamilton_ui_url,
        )
