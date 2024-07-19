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

from typing import Dict, Any

import numpy as np
import pandas as pd

from dagworks.tracking import pandas_stats
from dagworks.tracking import stats

"""Module that houses functions to compute statistics on numpy objects
Notes:
 - we should assume numpy v1.0+ so that we have a string type
"""


@stats.compute_stats.register
def compute_stats_numpy(result: np.ndarray, node_name: str, node_tags: dict) -> Dict[str, Any]:
    try:
        df = pd.DataFrame(result)  # hack - reuse pandas stuff
    except ValueError:
        return {
            "observability_type": "unsupported",
            "observability_value": {
                "unsupported_type": str(type(result)) + f" with dimensions {result.shape}",
                "action": "reach out to the DAGWorks team to add support for this type.",
            },
            "observability_schema_version": "0.0.1",
        }
    return {
        "observability_type": "dagworks_describe",
        "observability_value": pandas_stats._compute_stats(df),
        "observability_schema_version": "0.0.3",
    }
