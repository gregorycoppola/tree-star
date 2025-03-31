import re
import sys

def evaluate_dependencies(log_file_path):
    pattern = r"Token: (.+?) \| Head: (\d+) \| Gold Label: (\S+) \| ChatGPT: (\S+)"
    total = 0
    correct = 0

    with open(log_file_path, 'r') as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                token, head, gold_label, pred_label = match.groups()
                total += 1
                if gold_label == pred_label:
                    correct += 1

    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"File: {log_file_path}")
    print(f"Total dependencies evaluated: {total}")
    print(f"Correct labels: {correct}")
    print(f"Accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python eval_deps.py <log_file_path>")
        sys.exit(1)

    log_file_path = sys.argv[1]
    evaluate_dependencies(log_file_path)

