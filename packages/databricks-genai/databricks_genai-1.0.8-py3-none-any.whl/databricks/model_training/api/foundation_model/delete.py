"""Delete a model training run"""

from typing import Any, Dict, List, Union

from databricks.model_training.api.engine import get_return_response, run_plural_mapi_request
from databricks.model_training.api.exceptions import DatabricksModelTrainingRequestError
from databricks.model_training.types import TrainingRun

QUERY_FUNCTION = 'deleteFinetunes'
VARIABLE_DATA_NAME = 'getFinetunesData'
QUERY = f"""
mutation DeleteFinetunes(${VARIABLE_DATA_NAME}: GetFinetunesInput!) {{
  {QUERY_FUNCTION}({VARIABLE_DATA_NAME}: ${VARIABLE_DATA_NAME}) {{
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


def delete(runs: Union[str, TrainingRun, List[str], List[TrainingRun]]) -> int:
    """Cancel and delete training runs

    Stop a list of runs currently running in the MosaicML platform.

    Args:
        runs (``Optional[List[str] | List[``:class:`~databricks.model_training.types.training_run.TrainingRun` ``]]``):
            A list of runs or training_run names to stop. Using 
            :class:`~databricks.model_training.types.training_run.TrainingRun` objects is most efficient. 
            See the note below.
        reason (``Optional[str]``): A reason for stopping the finetune run
        timeout (``Optional[float]``): Time, in seconds, in which the call should complete.
            If the call takes too long, a :exc:`~concurrent.futures.TimeoutError`
            will be raised. If ``future`` is ``True``, this value will be ignored.
        future (``bool``): Return the output as a :class:`~concurrent.futures.Future`. If True, the
            call to :func:`delete` will return immediately and the request will be
            processed in the background. This takes precedence over the ``timeout``
            argument. To get the list of :class:`~databricks.model_training.types.training_run.TrainingRun` output,
            use ``return_value.result()`` with an optional ``timeout`` argument.

    Raises:
        DatabricksGenAIError: Raised if stopping any of the requested runs failed

    Returns: Int representing the number of runs that were successfully deleted
    """
    if not runs:
        raise DatabricksModelTrainingRequestError('Must provide training run(s) to delete')

    training_runs_list: Union[List[str], List[TrainingRun]] = []
    if isinstance(runs, (str, TrainingRun)):
        training_runs_list = [runs]
    else:
        training_runs_list = runs
    # Extract run names
    training_run_names = [r.name if isinstance(r, TrainingRun) else r for r in training_runs_list]

    filters = {}
    if training_run_names:
        filters['name'] = {'in': training_run_names}

    variables: Dict[str, Dict[str, Any]] = {VARIABLE_DATA_NAME: {'filters': filters}}

    response = run_plural_mapi_request(
        query=QUERY,
        query_function=QUERY_FUNCTION,
        return_model_type=TrainingRun,
        variables=variables,
    )
    return len(get_return_response(response))
