import streamlit as st
from typing import Any, cast
from typing import TypedDict
from app_graph import graph  # your existing graph
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

st.title("Prompt Optimizer 🚀")

# Input box
user_input = st.text_area("Enter your prompt:")

# Prompt optimization parameters

use_case = st.selectbox(
    "Select Use Case", ["LinkedIn Post", "Cold Email", "Blog Writing", "Ad Copy"]
)

audience = st.text_input("Target Audience", "Developers / Founders / Students")

tone = st.selectbox("Tone", ["Professional", "Casual", "Persuasive", "Educational"])

goal = st.text_input("Goal", "Engagement / Leads / Awareness")

if st.button("Optimize Prompt"):
    if user_input.strip() == "":
        st.warning("Please enter a prompt")
    else:
        with st.spinner("Optimizing..."):
            input_data = {
                "prompt": user_input,
                "use_case": use_case,
                "audience": audience,
                "tone": tone,
                "goal": goal,
                "relevance": 0,
                "specificity": 0,
                "clarity": 0,
                "feedback": "",
                "candidate_prompts": [],
                "best_prompt": "",
                "improved_prompt": "",
                "human_decision": "",
                "approved_prompt": "",
                "prompt_history": [],
                "attempt": 0,
            }

            result = graph.invoke(input_data)

            st.success("Done!")

            st.subheader("Evaluation Scores:")
            st.write(f"Relevance: {result['relevance']}")
            st.write(f"Specificity: {result['specificity']}")
            st.write(f"Clarity: {result['clarity']}")

            st.subheader("Feedback:")
            st.write(result["feedback"])

            avg_score = (
                result["relevance"] + result["specificity"] + result["clarity"]
            ) / 3

            if avg_score < 6:
                st.warning("The prompt needs improvement.")

            st.write(f"🔁 Iterations used: {result.get('attempt', 0) + 1}")
            st.subheader("🚀 Final Optimized Prompt:")
            st.code(result["prompt"], language="text")

            final_response = llm.invoke(result["prompt"])
            st.subheader("Final Output (Generated using Optimised Prompt)")
            st.write(final_response.content)
