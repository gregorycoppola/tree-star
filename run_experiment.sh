#!/bin/bash

if [ $# -lt 2 ]; then
  echo "Usage: $0 \"experiment_name\" \"command to run\""
  echo "Example: $0 my_exp \"python train.py --lr 0.01\""
  exit 1
fi

experiment_name="$1"
shift
cmd="$*"

timestamp=$(date +%Y%m%d-%H%M%S)
dir="experiments/${experiment_name}_${timestamp}"

mkdir -p "$dir"

echo "$cmd" > "$dir/command.sh"
bash -c "$cmd" > "$dir/output.log" 2>&1

echo "Experiment saved in $dir"

