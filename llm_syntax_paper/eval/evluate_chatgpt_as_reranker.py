import json

def main():
    input_file = "results.jsonl"  # Change if needed

    with open(input_file) as f:
        results = [json.loads(line) for line in f]

    for result in results:
        print("=" * 80)
        print(f"Example {result['index']}")
        print(f"Sentence: {result['sentence']}")
        print(f"Ambiguous Phrase: {result['ambiguous_phrase']}")
        print(f"Expected Head: {result['expected_head']}")
        print(f"Predicted Head: {result['predicted_head']}")

        correct = result["correct"]
        correctness = "✅ Correct" if correct else "❌ Incorrect"
        print(f"Attachment Match: {correctness}")

        response = result["chatgpt_response"]
        print(f"ChatGPT Response: {response}")
        print()

if __name__ == "__main__":
    main()

