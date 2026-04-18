from langgraph.graph import StateGraph

from nodes.run_agent import run_agent
from nodes.evaluate import evaluate_prompt
from nodes.optimize import optimize
from nodes.check_quality import check_quality

# Read prompt from file
with open("prompt.txt", "r", encoding="utf-8") as f:
    user_prompt = f.read()

# Initial state
input_data = {
    "prompt": user_prompt,
    "improved_prompt": "",
    "relevance": 0,
    "specificity": 0,
    "clarity": 0,
    "feedback": "",
    "attempt": 0,
}

# Build graph
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

# Run
result = graph.invoke(input_data)

# Final Output
print("\n🎯 FINAL APPROVED PROMPT:\n")
print(result["improved_prompt"])
