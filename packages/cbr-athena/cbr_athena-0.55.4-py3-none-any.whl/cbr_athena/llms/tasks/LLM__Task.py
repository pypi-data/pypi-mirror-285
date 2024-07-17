from cbr_athena.utils.Random_Guid import Random_Guid
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self


class LLM__Task(Kwargs_To_Self):
    task_id     : Random_Guid
    workflow_id : Random_Guid