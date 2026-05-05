from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=150)


def evaluate_prompt(state):
    print("\n📊 Evaluating Candidates...\n")

    candidates = state.get("candidate_prompts") or [state["prompt"]]

    # ✅ Get context
    original = state.get("original_prompt", state["prompt"])
    use_case = state.get("use_case", "")
    audience = state.get("audience", "")
    tone = state.get("tone", "")
    goal = state.get("goal", "")

    best_score = -1
    best_prompt = None

    best_r = best_s = best_c = best_intent = 0

    for candidate in candidates:
        eval_instruction = f"""
You are evaluating prompt quality.

ORIGINAL USER INTENT:
{original}

CONTEXT:
Use Case: {use_case}
Audience: {audience}
Tone: {tone}
Goal: {goal}

CANDIDATE PROMPT:
{candidate}

Score strictly:

Relevance (0-10) → Does it match user intent?
Specificity (0-10) → Is it detailed and structured?
Clarity (0-10) → Is it clear and usable?
Intent Alignment (0-10) → Does it EXACTLY match use_case + audience + goal?

Return ONLY:
Relevance: X
Specificity: X
Clarity: X
Intent: X
"""

        response = llm.invoke(eval_instruction)
        text = response.content

        def extract(label):
            try:
                return int(text.split(label)[1].split("\n")[0].strip())
            except:
                return 0

        r = extract("Relevance:")
        s = extract("Specificity:")
        c = extract("Clarity:")
        intent = extract("Intent:")

        total = r + s + c + intent  # ✅ NEW scoring

        print(f"\n--- Candidate ---\n{candidate}")
        print(f"Score: {total}")

        if total > best_score:
            best_score = total
            best_prompt = candidate
            best_r, best_s, best_c, best_intent = r, s, c, intent

    print("\n🏆 Best Prompt Selected:")
    print(best_prompt)

    return {
        **state,
        "prompt": best_prompt,
        "best_prompt": best_prompt,
        "relevance": best_r,
        "specificity": best_s,
        "clarity": best_c,
        "intent_alignment": best_intent,
        "feedback": f"Best Score: {best_score}",
    }
