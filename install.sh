#!/bin/bash

# HomeSpend Installation Script
# This script helps set up HomeSpend on a fresh VPS

set -e  # Exit on any error

echo "🚀 HomeSpend Installation Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "This script should not be run as root"
   exit 1
fi

# Update system
log_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
log_info "Installing required packages..."
sudo apt install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Install Docker
if ! command -v docker &> /dev/null; then
    log_info "Installing Docker..."
    
    # Add Docker's official GPG key
    sudo mkdir -m 0755 -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    log_success "Docker installed successfully"
else
    log_info "Docker is already installed"
fi

# Install Docker Compose (standalone)
if ! command -v docker-compose &> /dev/null; then
    log_info "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    log_success "Docker Compose installed successfully"
else
    log_info "Docker Compose is already installed"
fi

# Install Nginx
if ! command -v nginx &> /dev/null; then
    log_info "Installing Nginx..."
    sudo apt install -y nginx
    
    # Enable and start Nginx
    sudo systemctl enable nginx
    sudo systemctl start nginx
    
    log_success "Nginx installed and started"
else
    log_info "Nginx is already installed"
fi

# Install Certbot for SSL
if ! command -v certbot &> /dev/null; then
    log_info "Installing Certbot for SSL certificates..."
    sudo apt install -y certbot python3-certbot-nginx
    log_success "Certbot installed successfully"
else
    log_info "Certbot is already installed"
fi

# Copy environment file
if [[ ! -f ".env" ]]; then
    log_info "Creating environment file..."
    cp env.example .env
    log_warning "Please edit .env with your configuration"
    log_warning "You need to set up Microsoft App credentials"
else
    log_info "Environment file already exists"
fi

# Set up firewall
log_info "Configuring firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 22/tcp comment 'SSH'
    sudo ufw allow 80/tcp comment 'HTTP'
    sudo ufw allow 443/tcp comment 'HTTPS'
    
    # Ask before enabling UFW
    read -p "Enable UFW firewall? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo ufw --force enable
        log_success "Firewall configured and enabled"
    else
        log_info "Firewall configured but not enabled"
    fi
else
    log_warning "UFW not found, please configure firewall manually"
fi

# Final instructions
echo ""
log_success "Installation completed!"
echo ""
log_info "Next steps:"
log_info "1. Configure your Microsoft App in Azure Portal"
log_info "2. Update .env file with your credentials"
log_info "3. Run: docker-compose build && docker-compose up -d"
log_info "4. Set up SSL certificate with certbot"
echo ""
log_success "HomeSpend installation script completed!"
