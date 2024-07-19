from typing                                             import Optional
from cbr_athena.schemas.for_fastapi.GPT_Prompt_Simple   import GPT_Prompt_Simple

class GPT_Prompt_With_System(GPT_Prompt_Simple):
    system_prompts: Optional[list[str]] = None