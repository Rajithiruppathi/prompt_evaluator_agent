def ask_user(state):
    print(f"\nAI Score: {state['score']}")
    print(f"AI Feedback: {state['feedback']}\n")

    user_input = input("Approve output? Type 'yes', 'no', or press Enter to skip: ").strip().lower()
    user_feedback = ""

    if user_input == "no":
        user_feedback = input("Please provide your feedback: ").strip()

    return {
        "user_input": user_input,
        "user_feedback": user_feedback,
    }
