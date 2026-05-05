from langchain_openai import ChatOpenAI
from templates import TEMPLATES

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5, max_tokens=500)


def generate_content(prompt, use_case, audience, tone, goal):
    template = TEMPLATES.get(use_case)

    if not template:
        raise ValueError(f"Invalid use case: {use_case}")

    final_prompt = template.format(
        prompt=prompt, audience=audience, tone=tone, goal=goal
    )

    response = llm.invoke(final_prompt)

    # ✅ CORRECT way
    return response.content.strip()
