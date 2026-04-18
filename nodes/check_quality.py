def check_quality(state):
    score = (state["relevance"] + state["specificity"] + state["clarity"]) / 3

    print(f"\n🎯 Avg Score: {score}")

    if score >= 8 or state["attempt"] >= 3:
        return "end"
    else:
        return "improve"
