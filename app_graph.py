"""
from langgraph.graph import StateGraph, END
from state import AgentState

from nodes.run_agent import run_agent
from nodes.evaluate import evaluate
from nodes.optimize import optimize
from nodes.human_review import human_review


def human_decision_router(state):
    if state["human_decision"] == "accept":
        return "end"

    if state.get("attempt", 0) >= 3:
        print("\n⚠️ Max attempts reached. Ending.")
        return "end"

    return "run"


"""


def decide(state):
    total_score = state["relevance"] + state["specificity"] + state["clarity"]
    attempt = state["attempt"]
    print(f"\n⭐ Total Score: {total_score}")

    if total_score >= 24:
        print("\n✅ Good output. Stopping.")
        return END

    if state["attempt"] >= 2:
        print("\n⚠️ Max attempts reached.")
        return END

    return "optimize"


"""

builder = StateGraph(AgentState)

builder.add_node("run", run_agent)
builder.add_node("evaluate", evaluate)
builder.add_node("optimize", optimize)
builder.add_node("human_review", human_review)


def update_prompt(state):
    state["prompt"] = state["approved_prompt"]  # 🔥 THIS LINE
    return state


builder.add_node("update_prompt", update_prompt)

builder.set_entry_point("run")

builder.add_edge("run", "evaluate")
builder.add_edge("evaluate", "optimize")
builder.add_edge("optimize", "human_review")
builder.add_conditional_edges(
    "human_review", human_decision_router, {"run": "run", "end": END}
)

graph = builder.compile()

"""

from langgraph.graph import StateGraph

builder = StateGraph(dict)

builder.add_node("improve", run_agent)
builder.add_node("evaluate", evaluate_prompt)
builder.add_node("optimize", optimize)

builder.set_entry_point("improve")

builder.add_edge("improve", "evaluate")

builder.add_conditional_edges(
    "evaluate", check_quality, {"improve": "optimize", "end": "__end__"}
)

builder.add_edge("optimize", "improve")

graph = builder.compile()
