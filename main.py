from generator import generate_content


def run():
    print("🚀 AI Content Engine\n")

    prompt = input("Enter your prompt: ").strip()
    use_case = input("Use Case (LinkedIn Post / Cold Email / Blog): ").strip()
    audience = input("Target Audience: ").strip()
    tone = input("Tone: ").strip()
    goal = input("Goal: ").strip()

    print("\n⏳ Generating...\n")

    try:
        result = generate_content(prompt, use_case, audience, tone, goal)

        print("\n🎯 FINAL OUTPUT:\n")
        print(result)

    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    run()
