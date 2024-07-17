"""Cancel a model training run"""

from typing import Any, Dict, List, Union

from databricks.model_training.api.engine import get_return_response, run_plural_mapi_request
from databricks.model_training.api.exceptions import DatabricksModelTrainingRequestError
from databricks.model_training.types.training_run import TrainingRun

QUERY_FUNCTION = 'stopFinetunes'
VARIABLE_DATA_NAME = 'getFinetunesData'
OPTIONAL_DATA_NAME = 'stopFinetunesData'
QUERY = f"""
mutation StopFinetunes(${VARIABLE_DATA_NAME}: GetFinetunesInput!, ${OPTIONAL_DATA_NAME}: StopFinetunesInput) {{
  {QUERY_FUNCTION}({VARIABLE_DATA_NAME}: ${VARIABLE_DATA_NAME}, {OPTIONAL_DATA_NAME}: ${OPTIONAL_DATA_NAME}) {{
    id
    name
    status
    createdById
    createdByEmail
    createdAt
    updatedAt
    startedAt
    completedAt
    reason
    isDeleted
  }}
}}"""


def cancel(runs: Union[str, TrainingRun, List[str], List[TrainingRun]]) -> int:
    """Cancel a training run or list of training runs without deleting them.
    If the run does not exist or if the run has already terminated, an error will be raised.

    Args:
        runs (Union[str, TrainingRun, List[str], List[TrainingRun]]): The
            training run(s) to cancel. Can be a single run or a list of runs.

    Returns:
        int: The number of training runs cancelled
    """

    if not runs:
        raise DatabricksModelTrainingRequestError('Must provide training run(s) to cancel')

    runs_list: List[Union[str, TrainingRun]] = [runs] if isinstance(runs,
                                                                    (str, TrainingRun)) else runs  # pyright: ignore

    # Extract run names
    training_run_names = [r if isinstance(r, str) else r.name for r in runs_list]

    filters = {}
    if training_run_names:
        filters['name'] = {'in': training_run_names}

    variables: Dict[str, Dict[str, Any]] = {VARIABLE_DATA_NAME: {'filters': filters}}

    try:
        response = run_plural_mapi_request(
            query=QUERY,
            query_function=QUERY_FUNCTION,
            return_model_type=TrainingRun,
            variables=variables,
        )
        return len(get_return_response(response))
    except Exception as e:
        raise DatabricksModelTrainingRequestError(f'Failed to cancel training run(s) {runs}. Please make sure the run '
                                                  'has not completed or failed and try again.') from e
