#!/bin/bash
# This makes the script exit immediately if any command fails
set -e

# Base models to ensure they exist
base_models=(
  "qwen3:4b"
  "deepseek-r1:14b"
  "qwen3-coder:30b"
)

echo "Pulling base models..."
for base in "${base_models[@]}"; do
  if ! ollama list | grep -q "$(echo $base | cut -d':' -f1)"; then
    echo "Pulling $base..."
    ollama pull "$base"
  else
    echo "$base already exists, skipping pull."
  fi
done

# Custom models to create
custom_models=(
  "qwen3-4b-balanced"
  "qwen3-4b-drunk"
  "qwen3-4b-serious"
  "qwencoder-30b-safe"
)

echo "Creating custom models..."
for model in "${custom_models[@]}"; do
  Modelfile.md="/modelfiles/Modelfile-$model"
  ollama create "$model" -f "/modelfiles/Modelfile-$model"
done



echo "All models processed."
