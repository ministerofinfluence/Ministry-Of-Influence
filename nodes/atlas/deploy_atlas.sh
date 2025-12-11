#!/bin/bash
# Atlas Deployment Script
# Target: 10.0.0.100 (Atlas Node)
# User: fabio

TARGET_IP="10.0.0.100"
USER="fabio"
REMOTE_DIR="~/ministry/atlas"
LOCAL_DIR="./nodes/atlas"

echo "=== Deploying Atlas Infrastructure to $TARGET_IP ==="

# Helper for SSH commands
run_remote() {
    ssh -o StrictHostKeyChecking=no $USER@$TARGET_IP "$1"
}

# 1. Check Connectivity
echo "[1/5] Checking connection..."
ping -c 1 $TARGET_IP > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Cannot ping $TARGET_IP. Check VPN/Network."
    exit 1
fi

# 2. Upload Files (Rsync)
echo "[2/5] Uploading configuration..."
# Create remote dir if not exists
run_remote "mkdir -p $REMOTE_DIR/volumes/db/data $REMOTE_DIR/volumes/api"
# Clean Rsync
rsync -avz -e "ssh -o StrictHostKeyChecking=no" --exclude 'volumes/db/data' $LOCAL_DIR/ $USER@$TARGET_IP:$REMOTE_DIR/

# 3. Install Docker (Remote Execution)
echo "[3/5] Verifying Docker installation..."
run_remote "
    if ! command -v docker &> /dev/null; then
        echo 'Docker not found. Installing...'
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker \$USER
        echo 'Docker installed.'
    else
        echo 'Docker is already installed.'
    fi
"

# 4. Launch Stack
echo "[4/5] Launching Supabase Stack..."
run_remote "
    cd $REMOTE_DIR
    # Ensure Permissions for Postgres
    mkdir -p volumes/db/data
    chmod 700 volumes/db/data
    
    # Launch
    docker compose up -d
"

echo "=== Deployment Complete ==="
echo "Supabase Studio: http://$TARGET_IP:3000"
echo "API Gateway:     http://$TARGET_IP:8000"
echo "Check logs with: ssh $USER@$TARGET_IP 'cd $REMOTE_DIR && docker compose logs -f'"
