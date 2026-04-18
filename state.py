from typing import TypedDict


class AgentState(TypedDict):
    prompt: str
    output: str

    # Multi-score (GEPA idea)
    relevance: float
    specificity: float
    clarity: float

    feedback: str

    # For multiple prompts
    candidate_prompts: list
    best_prompt: str

    # Phase 3 additions
    human_decision: str
    approved_prompt: str
    prompt_history: list[str]

    # # Used attempt in phase 2 before human feedback, now removing this to get rid of the confusion between phase 2 and phase 3. We can always add it back if needed, let's keep the state focused on the current prompt and feedback cycle.
    # attempt: int
