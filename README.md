# Prompt Evaluator & Optimizer Agent 🚀

## 📌 Overview

This project is an AI-powered **Prompt Optimization Pipeline** built using Python and LangChain.

It is designed to:

* Improve raw prompts
* Evaluate their quality
* Iteratively refine them
* Produce a final, high-quality prompt

Instead of manually rewriting prompts, this system automates the process using structured AI workflows.

---

## 🎯 Problem Statement

Writing prompts is easy.
But writing **high-quality prompts** that are:

* Clear
* Specific
* Structured
* Effective

is difficult and inconsistent.

Most developers:

* Rewrite prompts manually
* Don’t evaluate quality
* Lack a feedback loop

---

## 💡 Solution

This project introduces a **multi-node pipeline** that:

1. Improves prompts using an LLM
2. Evaluates them using scoring metrics
3. Decides whether to iterate or stop
4. Outputs a refined version

---

## ⚙️ How the System Works

### 🔁 Pipeline Flow

User Input / prompt.txt
↓
run_agent.py (LLM improves prompt)
↓
evaluate.py (scores prompt)
↓
check_quality.py (decides if good enough)
↓
optimize.py (retries if needed)
↓
human_review.py (optional approval)
↓
FINAL OUTPUT

---

## 🧩 Project Structure

```
v2_ai_evaluator/
│
├── main.py                # Entry point
├── app_graph.py           # LangGraph pipeline definition
├── state.py               # Shared state across nodes
│
├── prompt.txt             # Input prompt
├── requirements.txt       # Dependencies
├── README.md              # Documentation
│
├── nodes/
│   ├── run_agent.py       # Prompt improvement (LLM call)
│   ├── evaluate.py        # Scoring logic
│   ├── check_quality.py   # Quality threshold decision
│   ├── optimize.py        # Iteration logic
│   ├── human_review.py    # Manual approval (optional)
│   ├── ask_user.py        # User input handling (optional)
```

---

## 🧠 Node-Level Explanation

### 1. run_agent.py

**Role:** Improves the input prompt using an LLM.

* Takes: `state["prompt"]`
* Sends to model (GPT)
* Returns: improved prompt

👉 This is the **core generation step**

---

### 2. evaluate.py

**Role:** Scores the improved prompt.

Evaluates based on:

* Relevance
* Specificity
* Clarity

Returns:

* Scores
* Feedback

👉 This is the **quality measurement layer**

---

### 3. check_quality.py

**Role:** Decides whether the prompt is good enough.

* Calculates average score
* Compares with threshold (e.g., ≥ 8)

If:

* ✅ Good → Stop pipeline
* ❌ Not good → Send for optimization

👉 This is the **decision engine**

---

### 4. optimize.py

**Role:** Controls iteration.

* Tracks number of attempts
* Decides whether to retry
* Prevents infinite loops

👉 This is the **loop controller**

---

### 5. human_review.py (Optional)

**Role:** Manual validation step.

* Allows user to approve/reject
* Adds human-in-the-loop control

👉 Useful for production systems

---

### 6. ask_user.py (Optional)

**Role:** Handles user input dynamically.

* Accepts prompt input from user
* Can replace static `prompt.txt`

---

### 7. app_graph.py

**Role:** Defines the pipeline flow using LangGraph.

* Connects all nodes
* Controls execution order

👉 This is the **brain of the system**

---

### 8. state.py

**Role:** Maintains shared data across nodes.

Stores:

* Prompt
* Improved prompt
* Scores
* Feedback
* Attempt count

👉 This is the **memory layer**

---

## 📊 Evaluation Metrics

Each prompt is scored based on:

| Metric      | Description                   |
| ----------- | ----------------------------- |
| Relevance   | How well it matches the task  |
| Specificity | Level of detail and precision |
| Clarity     | Ease of understanding         |

---

## ▶️ How to Run

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Add API Key

Create `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

### 3. Run the project

```
python main.py
```

---

## 📌 Example Workflow

Input:

```
Improve the prompt
```

System:

* Generates improved version
* Evaluates it
* Iterates if needed

Output:

```
A structured, detailed prompt with rules, constraints, and format
```

---

## 🚀 Future Improvements

* Multi-prompt generation (best selection)
* UI using Streamlit
* Prompt history tracking
* Scoring visualization dashboard
* Integration with real applications

---

## 👤 Author

Raji
AI Engineer (Learning & Building Phase)

---

## ⭐ Key Learning

This project demonstrates:

* Prompt engineering is iterative
* Evaluation is critical in AI systems
* Small pipeline issues can break output
* Structured workflows improve reliability

---
