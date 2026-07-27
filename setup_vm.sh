#!/bin/bash
set -e

echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing Docker and Docker Compose V2..."
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

echo "Installing NVIDIA Container Toolkit..."
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker

echo "Installing Ollama (native) and configuring to listen on all interfaces..."
curl -fsSL https://ollama.com/install.sh | sh

sudo mkdir -p /etc/systemd/system/ollama.service.d
echo -e "[Service]\nEnvironment=\"OLLAMA_HOST=0.0.0.0\"" | sudo tee /etc/systemd/system/ollama.service.d/override.conf
sudo systemctl daemon-reload
sudo systemctl restart ollama

echo "Pulling DeepSeek model..."
ollama pull deepseek-r1:32b

echo "Installing Node.js (v20)..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

echo "Installing Python pip..."
sudo apt install -y python3-pip

echo "Configuring Docker for Artifact Registry..."
gcloud auth configure-docker asia-south1-docker.pkg.dev --quiet

echo "Enabling OS Login..."
sudo gcloud compute instances add-metadata $(hostname) --metadata enable-oslogin=TRUE

echo "Setup complete. Rebooting to apply changes..."
sudo reboot
