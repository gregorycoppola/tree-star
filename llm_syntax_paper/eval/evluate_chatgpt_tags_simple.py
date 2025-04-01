import re
import sys

def evaluate_tagging(log_file_path):
    pattern = r"Token: (.+?) \| Gold UPOS: (\w+) \| ChatGPT: (\w+)"
    total = 0
    correct = 0

    with open(log_file_path, 'r') as f:
        for line in f:
            # print(line)
            match = re.search(pattern, line)
            if match:

                token, gold, pred = match.groups()
                print(token)
                if gold not in {"VERB", "NOUN"}:
                    continue  # Skip if not VERB or NOUN

                total += 1
                if gold == pred:
                    correct += 1
                else:
                    print (token, "gold", gold, "pred", pred)
                
    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"File: {log_file_path}")
    print(f"Evaluated only NOUN/VERB tokens.")
    print(f"Total NOUN/VERB tokens: {total}")
    print(f"Correct tags: {correct}")
    print(f"Accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python eval_tags.py <log_file_path>")
        sys.exit(1)

    log_file_path = sys.argv[1]
    evaluate_tagging(log_file_path)
