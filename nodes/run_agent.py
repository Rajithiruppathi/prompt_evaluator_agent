from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


def run_agent(state):
    original_prompt = state["prompt"]
    attempt = state.get("attempt", 0) + 1
    print(f"\n🔹 Improving Prompt (Attempt {'attempt'})...\n")

    improvement_instruction = f"""
You are an expert Prompt Engineer.

Your task is to REWRITE and IMPROVE the following prompt.

DO NOT explain.
DO NOT give suggestions.
ONLY return the improved prompt.

Make it:
- More structured
- More clear
- More enforceable
IMPORTANT:
- DO NOT remove any critical instructions from the original prompt.
- DO NOT shorten the prompt significantly. Keep all important details.
- Preserve all validation rules and logic
- Only improve clarity, structure, and enforceability.

PROMPT TO IMPROVE:
------------------
{original_prompt}
"""

    response = llm.invoke(improvement_instruction)

    improved_prompt = response.content.strip()

    print("✅ Improved Prompt Generated\n")

    return {
        **state,
        "improved_prompt": improved_prompt,
        "attempt": attempt,
    }
