from typing import Callable
from functools import wraps
import uuid


from nema.data.data_collection import DataCollection
from nema.workflow import Workflow


def run(
    data_collection: DataCollection,
    enable_API_calls=True,
    job_id=None,
):
    # create random string if not provided
    actual_job_id = job_id if job_id else str(uuid.uuid4())

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):

            if enable_API_calls:
                data_collection.sync_data_from_API(actual_job_id)

            result = func(*args, **kwargs)

            data_collection.save_updates_locally(actual_job_id)

            return result

        return wrapper

    return decorator
