#!/bin/bash
set -e

echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing Docker and Docker Compose..."
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

echo "Installing NVIDIA Container Toolkit..."
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

echo "Pulling DeepSeek model (this will take time)..."
ollama pull deepseek-r1:32b

echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

echo "Installing Python pip and required packages..."
sudo apt install -y python3-pip

echo "Configuring Docker for Artifact Registry..."
gcloud auth configure-docker asia-south1-docker.pkg.dev --quiet

echo "Enabling OS Login..."
sudo gcloud compute instances add-metadata $(hostname) --metadata enable-oslogin=TRUE

echo "Setup complete. Rebooting to apply changes..."
sudo reboot
