from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


# def optimize_prompt(state):
#   print("\n🔁 Generating multiple improved prompts...\n")

# ✅ Always safely get attempt
#  attempt = state.get("attempt", 0)

# print("Attempt:", attempt)

# feedback = state.get("feedback", "")
# improved_prompt = state.get("improved_prompt", "")


# 🔹 Simple prompt improvement logic (can upgrade later)
def optimize_prompt(state):
    prompt = state["prompt"]
    feedback = state["feedback"]

    improved_prompt = f"""
You are a prompt engineering expert. 
Rewrite the following prompt to significantly improve its relevance, specificity, and clarity.

DO NOT return the same prompt.
You MUST expand it into a detailed, structured version.

Original Prompt:
{prompt}

Feedback:
{feedback}

RULES:
- Make it more specific and detailed
- Add structured formatting (steps, constraints,output format if needed)
- DO NO keep it generic
- DO NOT return the same prompt
- Make it clearly better than original

Return only the improved prompt.
"""

    # Call your LLM here (example)
    response = llm.invoke(improved_prompt)

    return {
        **state,
        "prompt": response.content.strip(),
        "improved_prompt": response.content.strip(),
        "attempt": state.get("attempt", 0) + 1,
    }
