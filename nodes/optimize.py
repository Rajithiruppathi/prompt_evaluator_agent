from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


def optimize(state):
    print("\n🔁 Generating multiple improved prompts...\n")

    # ✅ Always safely get attempt
    attempt = state.get("attempt", 0)

    print("Attempt:", attempt)

    feedback = state.get("feedback", "")
    prompt = state.get("prompt", "")

    # 🔹 Simple prompt improvement logic (can upgrade later)
    candidate_prompts = [
        f"Improve the following prompt for clarity and specificity:\n\n{prompt}",
        f"Rewrite this prompt to make it more structured and detailed:\n\n{prompt}",
        f"Enhance this prompt by making it more actionable and precise:\n\n{prompt}",
    ]

    print("\n🆕 Candidate Prompts:")

    for i, p in enumerate(candidate_prompts, 1):
        print(f"{i}. {p}\n")

    return {
        # "candidate_prompts": candidate_prompts,
        # "attempt": attempt + 1,  # ✅ SAFE increment
        "prompt": state["improved_prompt"],  # 🔥 THIS LIN
        "attempt": attempt,
    }
