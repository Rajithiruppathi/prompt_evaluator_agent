from langgraph.graph import StateGraph, END
from state import AgentState

# ✅ Import all nodes correctly
from nodes.run_agent import run_agent
from nodes.evaluate import evaluate_prompt as evaluate
from nodes.optimize import optimize_prompt as optimize
from nodes.check_quality import check_quality


# ----------------------------------------
# Decision Function
# ----------------------------------------
def decide(state):
    total_score = state["relevance"] + state["specificity"] + state["clarity"]
    attempt = state.get("attempt", 0)

    print(f"\n⭐ Total Score: {total_score}")

    # ✅ If good score → stop
    if total_score >= 27:
        print("\n✅ Good output. Stopping.")
        return END

    # ✅ If max attempts reached → stop
    # if attempt >= 2:
    if attempt >= 3:
        print("\n⚠️ Max attempts reached.")
        return END

    # Otherwise → optimize again
    return "optimize"


# ----------------------------------------
# Build Graph
# ----------------------------------------
builder = StateGraph(AgentState)

# ✅ Add nodes
builder.add_node("run", run_agent)
builder.add_node("evaluate", evaluate)
builder.add_node("optimize", optimize)

# ✅ Entry point
builder.set_entry_point("run")

# ✅ Flow
builder.add_edge("run", "evaluate")

builder.add_conditional_edges("evaluate", decide, {"optimize": "optimize", END: END})

builder.add_edge("optimize", "run")

# ✅ Compile graph
graph = builder.compile()
