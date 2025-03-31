import json
import argparse

def is_chatgpt_right(correct: bool, chatgpt_response: str) -> bool:
    response = chatgpt_response.strip().lower()
    if correct:
        return response == "no"
    else:
        return response != "no"

def main():
    parser = argparse.ArgumentParser(description="Evaluate ChatGPT's judgments on syntactic attachment.")
    parser.add_argument("input_file", help="Path to the results JSONL file.")
    args = parser.parse_args()

    with open(args.input_file) as f:
        results = [json.loads(line) for line in f]

    total = len(results)
    correct_preds = 0
    correct_when_parser_correct = 0
    correct_when_parser_incorrect = 0
    parser_correct_total = 0
    parser_incorrect_total = 0

    for result in results:
        print("=" * 80)
        print(f"Example {result['index']}")
        print(f"Sentence: {result['sentence']}")
        print(f"Ambiguous Phrase: {result['ambiguous_phrase']}")
        print(f"Expected Head: {result['expected_head']}")
        print(f"Predicted Head: {result['predicted_head']}")

        parser_correct = result["correct"]
        chatgpt_response = result["chatgpt_response"]
        chatgpt_correct = is_chatgpt_right(parser_correct, chatgpt_response)

        if parser_correct:
            parser_correct_total += 1
            if chatgpt_correct:
                correct_when_parser_correct += 1
        else:
            parser_incorrect_total += 1
            if chatgpt_correct:
                correct_when_parser_incorrect += 1

        if chatgpt_correct:
            correct_preds += 1

        parser_status = "✅ Correct" if parser_correct else "❌ Incorrect"
        chatgpt_status = "✅ ChatGPT Right" if chatgpt_correct else "❌ ChatGPT Wrong"
        print(f"Attachment Match: {parser_status}")
        print(f"ChatGPT Response: {chatgpt_response}")
        print(f"{chatgpt_status}\n")

    # Summary statistics
    print("=" * 80)
    print("Evaluation Summary:")
    print(f"Total Examples: {total}")
    print(f"Parser Correct: {parser_correct_total}")
    print(f"Parser Incorrect: {parser_incorrect_total}")
    print()
    if parser_correct_total > 0:
        print(f"ChatGPT Accuracy when Parser Correct: {correct_when_parser_correct}/{parser_correct_total} = {correct_when_parser_correct / parser_correct_total:.2%}")
    if parser_incorrect_total > 0:
        print(f"ChatGPT Accuracy when Parser Incorrect: {correct_when_parser_incorrect}/{parser_incorrect_total} = {correct_when_parser_incorrect / parser_incorrect_total:.2%}")
    print(f"Overall ChatGPT Accuracy: {correct_preds}/{total} = {correct_preds / total:.2%}")

if __name__ == "__main__":
    main()

