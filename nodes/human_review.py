def human_review(state):
    print("\n📢 HUMAN REVIEW STAGE\n")

    print("Generated Output:\n")
    print(state["output"])

    print("\n📊 Scores:")
    print("Relevance:", state.get("relevance"))
    print("Specificity:", state.get("specificity"))
    print("Clarity:", state.get("clarity"))

    print("\n💡 Suggested Prompts:\n")

    for i, p in enumerate(state.get("candidate_prompts", []), 1):
        print(f"{i}. {p}")

    decision = input("\nChoose: accept / reject / edit: ").lower()

    if decision == "accept":
        approved = state["prompt"]

    elif decision == "edit":
        approved = input("Enter your custom prompt: ")

    else:
        approved = state["prompt"]

    print("\n✅ Approved Prompt:\n", approved)

    return {
        "approved_prompt": approved,  # ✅ FIXED
        "human_decision": decision,
        "attempt": state.get("attempt", 0),
    }
