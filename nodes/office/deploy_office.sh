#!/bin/bash
# Office Deployment Script
# Target: 10.0.0.105 (Ministry HQ)
# User: fabio

TARGET_IP="10.0.0.105"
USER="fabio"
REMOTE_DIR="~/ministry/office"
LOCAL_DIR="./nodes/office"

echo "=== Deploying Office Infrastructure to $TARGET_IP ==="

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
run_remote "mkdir -p $REMOTE_DIR"
# Clean Rsync
# Note: We exclude 'sysop/logs' so we don't overwrite remote logs with empty local ones
rsync -avz -e "ssh -o StrictHostKeyChecking=no" --exclude 'sysop/logs' $LOCAL_DIR/ $USER@$TARGET_IP:$REMOTE_DIR/

# 3. Install Docker (Remote Execution)
echo "[3/5] Verifying Docker installation..."
# We inject the password for sudo operations
PASS="Grrrtrude"
ssh -o StrictHostKeyChecking=no $USER@$TARGET_IP "
    if ! command -v docker &> /dev/null; then
        echo 'Docker not found. Installing...'
        echo '$PASS' | sudo -S curl -fsSL https://get.docker.com -o get-docker.sh
        echo '$PASS' | sudo -S sh get-docker.sh
        echo '$PASS' | sudo -S usermod -aG docker \$USER
        echo 'Docker installed.'
    else
        echo 'Docker is already installed.'
    fi
"

# 4. Launch Stack
echo "[4/5] Launching Office Stack..."
run_remote "
    cd $REMOTE_DIR
    echo 'Building Office Stack...'
    docker compose build
    echo 'Starting Services...'
    docker compose up -d
"

echo "=== Deployment Complete ==="
echo "SysOp Agent:  http://$TARGET_IP:9090"
echo "n8n Workflow: http://$TARGET_IP:5678"
echo "WordPress:    http://$TARGET_IP:8080"
echo "Check logs: ssh $USER@$TARGET_IP 'cd $REMOTE_DIR && docker compose logs -f'"
