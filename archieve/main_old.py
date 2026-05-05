from langgraph.graph import StateGraph

from nodes.run_agent import run_agent
from nodes.evaluate import evaluate_prompt
from nodes.optimize import optimize_prompt
from nodes.check_quality import check_quality
import state

# Read prompt from file
with open("prompt.txt", "r", encoding="utf-8") as f:
    user_prompt = f.read()

# Define missing variables
use_case = "LinkedIn Post"
audience = "Developers"
tone = "Professional"
goal = "Awareness"

# Initial state
input_data = {
    "prompt": user_prompt,
    "improved_prompt": "",
    "use_case": use_case,
    "audience": audience,
    "tone": tone,
    "goal": goal,
    "relevance": 0,
    "specificity": 0,
    "clarity": 0,
    "feedback": "",
    "attempt": 0,
}

# Build graph


def process_state(state):
    if state["attempt"] >= 2:
        return "end"
    # Build graph

    builder = StateGraph(dict)

    builder.add_node("generate", optimize_prompt)
    builder.add_node("evaluate", evaluate_prompt)

    builder.set_entry_point("generate")

    builder.add_edge("generate", "evaluate")
    builder.add_edge("evaluate", "__end__")

    # builder.add_conditional_edges(
    #    "evaluate", check_quality, {"improve": "optimize", "end": "__end__"}
    # )

    # builder.add_edge("optimize", "improve")

    graph = builder.compile()

    # Run
    # result = graph.invoke(input_data)

    result = graph.invoke(input_data)

    # Final Output
    print("\n🎯 FINAL APPROVED PROMPT:\n")
    print(result["improved_prompt"])
