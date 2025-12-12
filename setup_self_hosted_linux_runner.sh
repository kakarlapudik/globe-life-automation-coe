#!/bin/bash
# Setup Self-Hosted Linux Runner for Selenium Grid Testing

echo "🐧 Setting up Self-Hosted Linux Runner for Selenium Grid"
echo "========================================================"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
  echo "❌ Please don't run this script as root"
  exit 1
fi

# Create runner directory
RUNNER_DIR="$HOME/actions-runner"
mkdir -p $RUNNER_DIR
cd $RUNNER_DIR

echo "📥 Downloading GitHub Actions Runner..."

# Download latest runner
RUNNER_VERSION="2.311.0"
curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -L \
  https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Verify download
echo "🔍 Verifying download..."
echo "29fc8cf2dab4c195bb147384e7e2c94cfd4d4022c793b346a6175435265aa278  actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz" | shasum -a 256 -c

# Extract runner
echo "📦 Extracting runner..."
tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Install dependencies
echo "🔧 Installing dependencies..."
sudo ./bin/installdependencies.sh

echo "⚙️  Configuration Instructions:"
echo "========================================================"
echo "1. Go to your GitHub repository:"
echo "   https://github.com/kakarlapudik/globe-life-automation-coe/settings/actions/runners"
echo ""
echo "2. Click 'New self-hosted runner'"
echo "3. Select 'Linux' and copy the token"
echo "4. Run the configuration command:"
echo "   ./config.sh --url https://github.com/kakarlapudik/globe-life-automation-coe --token YOUR_TOKEN"
echo ""
echo "5. Configure runner settings:"
echo "   - Runner name: selenium-grid-runner"
echo "   - Runner group: Default"
echo "   - Labels: self-hosted,linux,selenium-grid"
echo ""
echo "6. Start the runner:"
echo "   ./run.sh"
echo ""
echo "7. (Optional) Install as service:"
echo "   sudo ./svc.sh install"
echo "   sudo ./svc.sh start"

# Test Selenium Grid connectivity
echo ""
echo "🔍 Testing Selenium Grid connectivity..."
if curl -f --connect-timeout 5 http://192.168.1.33:4444/wd/hub/status; then
  echo "✅ Selenium Grid is accessible from this machine"
  echo "✅ Self-hosted runner will be able to run grid tests"
else
  echo "❌ Selenium Grid is not accessible from this machine"
  echo "❌ Please ensure:"
  echo "   - Selenium Grid is running at 192.168.1.33:4444"
  echo "   - This machine can access the grid network"
  echo "   - Firewall allows access to port 4444"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Complete the runner configuration above"
echo "2. Update your workflows to use 'runs-on: self-hosted'"
echo "3. Tests will run with full access to your Selenium Grid!"

echo ""
echo "📋 Test the setup with:"
echo "   export USE_SELENIUM_GRID=true"
echo "   export SELENIUM_HUB_URL=http://192.168.1.33:4444"
echo "   python test_selenium_grid_connectivity.py"