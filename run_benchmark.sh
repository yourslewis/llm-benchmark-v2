#!/bin/bash

# Read models from config file
models=$(jq -r '.models[]' benchmark/config/models.json)

# Iterate over each task
for task_dir in benchmark/tasks/*; do
  task_name=$(basename "$task_dir")
  
  # Create results directory for the task
  mkdir -p "benchmark/results/$task_name"
  
  # Read task and input
  task=$(cat "$task_dir/task.txt")
  input=$(cat "$task_dir/input.txt")
  
  # Combine task and input into a single prompt
  prompt="$task

$input"
  
  # Iterate over each model
  for model in $models; do
    echo "Running $task_name with $model"
    
    # Generate a safe filename for the model
    model_filename=$(echo "$model" | tr '/' '_')
    
    # Run the inference and save the output
    openclaw completion --model "$model" --system-prompt "$prompt" > "benchmark/results/$task_name/$model_filename.txt"
    
    echo "Finished running $task_name with $model"
  done
done

echo "Benchmark run complete."
