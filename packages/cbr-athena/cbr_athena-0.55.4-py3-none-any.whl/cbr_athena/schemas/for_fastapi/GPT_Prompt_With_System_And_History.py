from typing                                                import Optional
from cbr_athena.schemas.for_fastapi.GPT_History            import GPT_History
from cbr_athena.schemas.for_fastapi.GPT_Prompt_With_System import GPT_Prompt_With_System


class GPT_Prompt_With_System_And_History(GPT_Prompt_With_System):
    histories      : Optional[list[GPT_History]] = None