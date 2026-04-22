from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def evaluate_prompt(state):
    prompt = state["prompt"]

    print("\n📊 Evaluating Prompt...\n")

    eval_instruction = f"""
Evaluate this prompt on:
1. Relevance (0-10)
2. Specificity (0-10)
3. Clarity (0-10)

Also give short feedback.

IMPORTANT:
This is a PROMPT TEMPLATE, not final output.

PROMPT:
{prompt}

Return in this format:
Relevance: X
Specificity: X
Clarity: X
Feedback: ...
"""

    response = llm.invoke(eval_instruction)
    text = response.content

    # Simple parsing (safe enough)
    def extract(label):
        try:
            return int(text.split(label)[1].split("\n")[0].strip())
        except:
            return 5

    relevance = extract("Relevance:")
    specificity = extract("Specificity:")
    clarity = extract("Clarity:")

    print(text)

    return {
        **state,
        "relevance": relevance,
        "specificity": specificity,
        "clarity": clarity,
        "feedback": text,
    }
