# 🚀 AI Content Engine (Prompt Optimizer Agent)

An intelligent AI system that transforms a simple idea into high-quality content tailored for different use cases like LinkedIn posts, blogs, and cold emails.

---

## 💡 Problem

Most users give vague prompts like:

> "Write about APIs"

This leads to:
- Generic outputs
- No audience targeting
- No structure
- Poor engagement

---

## ✅ Solution

This AI Content Engine:
- Understands **use case**
- Adapts to **audience**
- Aligns with **tone**
- Optimizes for **goal**

👉 Converts one simple input into **high-quality, structured content**

---

## 🧠 How It Works

### Flow:


User Input → Prompt Optimization → Evaluation → Final Output


---

## 📂 Project Structure

### 1. `main.py`
- Entry point of the application
- Takes user input:
  - Prompt
  - Use Case
  - Audience
  - Tone
  - Goal
- Runs the full pipeline

---

### 2. `generator.py`
- Core AI generation logic
- Converts structured prompt into final content
- Handles:
  - LinkedIn Post
  - Blog
  - Cold Email

---

### 3. `templates.py`
- Contains dynamic templates for each use case
- Ensures:
  - Correct format
  - Structured output
  - Use-case specific behavior

---

### 4. `evaluate.py`
- Scores prompt quality based on:
  - Relevance
  - Specificity
  - Clarity
- Selects best version of prompt

---

### 5. `check_quality.py`
- Decides whether output is good enough
- Stops unnecessary iterations
- Improves performance

---

## ⚙️ Features

✅ Dynamic Use Case Handling  
✅ Audience-Aware Content  
✅ Tone Control  
✅ Goal-Oriented Output  
✅ Fast Execution (< 5 seconds)  
✅ Clean Modular Architecture  

---

## 🚀 Example

### Input:

Prompt: Write about APIs
Use Case: LinkedIn Post
Audience: AI Engineers
Tone: Professional
Goal: Engagement


### Output:
👉 Structured, engaging LinkedIn post with hook, insights, CTA

---

## 🛠️ Tech Stack

- Python
- OpenAI (GPT models)
- LangChain

---

## ⚡ Future Improvements

- Streamlit Web App UI
- API Deployment (FastAPI)
- Multi-language support
- Prompt memory system
- User history tracking

---

## 🎯 Key Learning

- Prompt engineering alone is not enough  
- Context (use case, audience, tone) is critical  
- Evaluation loops improve output quality  

---

## 📌 Status

✅ Working Prototype  
⚡ Ready for Portfolio  
🚧 Moving towards Production  

---

## 🤝 Connect

If you're building in AI / GenAI, let's connect!
