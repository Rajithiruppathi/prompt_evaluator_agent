from langgraph.graph import StateGraph
from typing import TypedDict
from langchain_openai import ChatOpenAI


# ✅ State
class State(TypedDict):
    prompt: str
    output: str
    user_input: str
    feedback: str
    attempt: int


# ✅ LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


# -------------------------
# 🔹 Node 1: Run Agent
# -------------------------
def run_node(state):
    print("\n🔹 Running Prompt...\n")

    response = llm.invoke(state["prompt"])
    output = response.content

    print("OUTPUT:\n")
    print(output)

    return {"output": output}


# -------------------------
# 🔹 Node 2: Ask User
# -------------------------
def ask_user_node(state):
    user_input = input("\nDo you like this output? (yes/no): ").strip().lower()

    feedback = ""

    if user_input == "no":
        feedback = input("What should be improved?: ")

    return {"user_input": user_input, "feedback": feedback}


# -------------------------
# 🔹 Node 3: Optimize
# -------------------------
def optimize_node(state):
    prompt = state["prompt"]
    feedback = state["feedback"]

    improve_prompt = f"""
You are an expert prompt engineer.

Original Prompt:
{prompt}

User Feedback:
{feedback}

Improve the prompt to generate better output.
"""

    response = llm.invoke(improve_prompt)

    return {"prompt": response.content, "attempt": state["attempt"] + 1}


# -------------------------
# 🔹 Decision Function
# -------------------------
def decide_next(state):

    # ✅ If user is happy → stop
    if state["user_input"] == "yes":
        return "end"

    # ✅ If max attempts reached → stop
    if state["attempt"] >= 3:
        print("\n⚠️ Max attempts reached. Stopping.")
        return "end"

    # ❌ Otherwise → improve
    return "optimize"


# -------------------------
# 🔹 Build Graph
# -------------------------
builder = StateGraph(State)

builder.add_node("run", run_node)
builder.add_node("ask_user", ask_user_node)
builder.add_node("optimize", optimize_node)

# Flow
builder.set_entry_point("run")

builder.add_edge("run", "ask_user")

builder.add_conditional_edges(
    "ask_user", decide_next, {"optimize": "optimize", "end": "__end__"}
)

builder.add_edge("optimize", "run")

graph = builder.compile()

# -------------------------
# 🚀 Run System
# -------------------------
result = graph.invoke({"prompt": "Explain about Pytorch in simple terms", "attempt": 0})

print("\n✅ Final State:\n", result)
