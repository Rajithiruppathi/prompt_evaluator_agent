def check_quality(state):
    avg = (state["relevance"] + state["specificity"] + state["clarity"]) / 3
    attempt = state.get("attempt", 0)

    if avg >= 7 and attempt < 2:
        return "end"

    return "improve"
