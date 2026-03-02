Preparations:

 - Check with nvidia-smi if everything is alright with the NVIDIA GPU
 - Install nvidia-container-toolkit to support --gpus on podman
    sudo pacman -S nvidia-container-toolkit
 - Onetime only manual model pull (if needed): podman exec -it ollama-deepseek ollama pull deepseek-r1:1.5b

Use:
 - ollama pull <modelname>
 - ollama list
 - Choose a model name (often with a billion of parameters number, ex :3b)
 - ollama run <modelname>
 - Chat with the model. 
 - /bye to exit
 - Note: Try with a very light one like tinyllama (only 1.1B params) just to test


Install via CLI:

Run podman to download images, build and start the ollama container
# Run detached
podman run -d \
# Container name
  --name ollama \
# Tell ollama to use the Nvidia GPU instead of the CPU (way slower)
  --gpus=all \
# Host path : Container path
  -v ~/path/to/ollama:/root/.ollama \
# Host port : Container port
  -p 9191:11434 \
# Optional: only 1 model loaded into VRAM simultaneously
-e OLLAMA_MAX_LOADED_MODELS=1 \
# Optional: only 1 parallel inference threads per model
-e OLLAMA_NUM_PARALLEL=1 \
#  Image of opensource ollama
  ollama/ollama



Post Install:
- An ssh key will be created for internal use, public key will be exposed in the container logs (multi user, run via remote, multiple containers, etc)
- Check for something like this:
time=2026-02-24T11:23:50.528Z ... msg="inference compute" ... library=CUDA compute=8.9 name=CUDA0 description="NVIDIA GeForce RTX 4090" total="24.0 GiB" available="20.7 GiB"
to check if GPU was detected succesfully

