from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)


def optimize_prompt(state):
    # --- DEBUGGING: Check terminal to see what is arriving ---
    print(f"DEBUG: State received in node: {state}")

    # --- STEP 1: Capture variables ---
    # We use .get() but ensure we handle None or empty strings
    use_case = state.get("use_case") if state.get("use_case") else "LinkedIn Post"
    audience = state.get("audience") if state.get("audience") else "Students"
    tone = state.get("tone") if state.get("tone") else "Professional"
    goal = state.get("goal") if state.get("goal") else "Awareness"
    prompt = state.get("prompt", "")

    # --- STEP 2: The Instruction ---
    instruction = f"""
You are an expert prompt engineer. 

Transform the input content into a HIGHLY SPECIFIC prompt based on the following context:

Use Case: {use_case}
Target Audience: {audience}
Tone: {tone}
Goal: {goal}

STRICT RULES:
- Follow the selected use case exactly.
- DO NOT mix formats.
- DO NOT ignore the use case.
- DO NOT be generic.

FORMAT RULES:

If Use Case = "LinkedIn Post":
- Hook (1 line)
- Insight/Value (2-3 lines)
- Call to Action (engagement, leads, awareness)

If Use Case = "Blog Post":
- Title
- Sections
- Conclusion

If Use Case = "Cold Email":
- Subject Line
- Opening (1-2 lines)
- Problem Statement (1-2 lines)
- Solution/Value (2-3 lines)
- Call to Action (1 line)

If Use Case = "Ad Copy":
- Headline (1 line)
- Description (2-3 lines)
- Call to Action (1 line)

Input Content: {prompt}

OUTPUT:
Return ONLY the improved prompt.
"""

    response = llm.invoke(instruction)
    optimized_text = response.content.strip()

    # --- STEP 3: Generate multiple candidates ---
    candidates = [
        optimized_text,
        f"Alternative 1: {optimized_text}",
        f"Alternative 2: {optimized_text}",
    ]

    # Add candidates to state
    state["candidate_prompts"] = candidates

    # --- STEP 4: MANDATORY - Return all keys to keep state alive ---
    return {
        "prompt": prompt,
        "improved_prompt": optimized_text,
        "use_case": use_case,
        "audience": audience,
        "tone": tone,
        "goal": goal,
        "attempt": state.get("attempt", 0) + 1,
    }
