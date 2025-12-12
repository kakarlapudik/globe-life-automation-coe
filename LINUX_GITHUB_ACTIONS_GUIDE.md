# Linux GitHub Actions Compatibility Guide

## 🐧 **Linux vs Windows Command Compatibility**

### **✅ Commands That Work Identically:**

```bash
# Environment Variables (same syntax)
export USE_SELENIUM_GRID=true
export SELENIUM_HUB_URL=http://192.168.1.33:4444
export SELENIUM_BROWSER=chrome

# Python Commands (identical)
python run_complete_automation.py
pytest test_selenium_grid_uc001.py -v -s

# Pip Commands (identical)
pip install -r requirements.txt
pip install selenium==4.15.2
```

### **🔧 Linux-Specific Advantages:**

```bash
# Better package management
apt-get update && apt-get install -y curl jq

# Native curl support (built-in)
curl -f http://192.168.1.33:4444/wd/hub/status

# JSON processing with jq (pre-installed)
curl -s "$SELENIUM_HUB_URL/wd/hub/status" | jq -r '.value.message'

# Better parallel processing
pytest -n auto --dist worksteal  # More efficient on Linux
```

## 🌐 **Network Connectivity Solutions**

### **Problem: Private Network Access**
GitHub Actions hosted runners **cannot access** `192.168.1.33:4444` (private IP)

### **Solution 1: Self-Hosted Runner (Recommended)**

#### Setup Self-Hosted Runner:
```bash
# On your Linux machine with grid access
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# Configure runner
./config.sh --url https://github.com/kakarlapudik/globe-life-automation-coe --token YOUR_TOKEN

# Run as service
sudo ./svc.sh install
sudo ./svc.sh start
```

#### Workflow Configuration:
```yaml
jobs:
  selenium-grid-tests:
    runs-on: self-hosted  # Uses your Linux machine
    
    steps:
    - name: Test Grid Access
      run: |
        # This will work because runner is on same network
        curl -f http://192.168.1.33:4444/wd/hub/status
        
    - name: Run Tests
      run: |
        export USE_SELENIUM_GRID=true
        export SELENIUM_HUB_URL=http://192.168.1.33:4444
        python run_complete_automation.py
```

### **Solution 2: Public Grid Exposure**

#### Expose Grid Publicly:
```bash
# Option A: Port forwarding on router
# Forward external port 4444 to 192.168.1.33:4444

# Option B: Reverse proxy with nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://192.168.1.33:4444;
        proxy_set_header Host $host;
    }
}

# Option C: ngrok tunnel
ngrok http 192.168.1.33:4444
# Use the ngrok URL in workflows
```

#### Updated Workflow:
```yaml
env:
  SELENIUM_HUB_URL: http://your-public-ip:4444  # or ngrok URL
```

### **Solution 3: Conditional Testing**

```yaml
jobs:
  test-grid-connectivity:
    runs-on: ubuntu-latest
    outputs:
      grid-available: ${{ steps.check.outputs.available }}
    
    steps:
    - name: Check Grid Availability
      id: check
      run: |
        if curl -f --connect-timeout 5 http://192.168.1.33:4444/wd/hub/status; then
          echo "available=true" >> $GITHUB_OUTPUT
        else
          echo "available=false" >> $GITHUB_OUTPUT
        fi
  
  selenium-tests:
    needs: test-grid-connectivity
    if: needs.test-grid-connectivity.outputs.grid-available == 'true'
    runs-on: ubuntu-latest
    # ... rest of workflow
```

## 🔄 **Linux-Optimized Workflow**

### **Enhanced Linux Commands:**

```yaml
- name: Install System Dependencies (Linux)
  run: |
    sudo apt-get update
    sudo apt-get install -y curl jq xvfb
    
    # Virtual display for headless browsers
    export DISPLAY=:99
    Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &

- name: Advanced Grid Testing (Linux)
  run: |
    # Test grid with timeout and retry
    for i in {1..3}; do
      if curl -f --connect-timeout 10 --max-time 30 "$SELENIUM_HUB_URL/wd/hub/status"; then
        echo "✅ Grid accessible on attempt $i"
        break
      else
        echo "❌ Attempt $i failed, retrying..."
        sleep 5
      fi
    done
    
    # Get detailed grid info
    curl -s "$SELENIUM_HUB_URL/wd/hub/status" | jq '.' || echo "Grid status retrieved"

- name: Parallel Test Execution (Linux Optimized)
  run: |
    # Linux handles parallel execution better
    export USE_SELENIUM_GRID=true
    export SELENIUM_HUB_URL=http://192.168.1.33:4444
    
    # Use all available cores efficiently
    pytest test_selenium_grid_uc001.py \
      -v -s \
      --html=reports/linux_grid_report.html \
      --self-contained-html \
      -n auto \
      --dist worksteal \
      --maxfail=3 \
      --tb=short

- name: Process Results (Linux Tools)
  run: |
    # Use Linux tools for better processing
    if [ -f "reports/selenium_grid_uc001_links_report.json" ]; then
      # Extract metrics using jq
      TOTAL=$(jq -r '.total_links' reports/selenium_grid_uc001_links_report.json)
      VALID=$(jq -r '.valid_links_count' reports/selenium_grid_uc001_links_report.json)
      RATE=$(jq -r '.summary.success_rate' reports/selenium_grid_uc001_links_report.json)
      
      echo "📊 Test Results:"
      echo "   Total Links: $TOTAL"
      echo "   Valid Links: $VALID"
      echo "   Success Rate: $RATE"
      
      # Create summary file
      cat > test_summary.txt << EOF
Grid Hub: $SELENIUM_HUB_URL
Total Links: $TOTAL
Valid Links: $VALID
Success Rate: $RATE
Execution Time: $(date)
EOF
    fi
```

## 🚀 **Performance Optimizations for Linux**

### **Resource Management:**
```yaml
- name: Optimize for Linux Performance
  run: |
    # Set optimal Python settings
    export PYTHONUNBUFFERED=1
    export PYTHONDONTWRITEBYTECODE=1
    
    # Optimize pytest for Linux
    export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
    
    # Use faster JSON library if available
    pip install orjson || echo "Using standard json"
    
    # Set optimal parallel workers based on CPU
    WORKERS=$(nproc)
    echo "Using $WORKERS parallel workers"
    
    pytest -n $WORKERS --dist worksteal
```

### **Caching Strategy:**
```yaml
- name: Cache Python Dependencies
  uses: actions/cache@v3
  with:
    path: |
      ~/.cache/pip
      ~/.cache/pytest_cache
    key: ${{ runner.os }}-python-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-python-

- name: Cache Selenium Drivers
  uses: actions/cache@v3
  with:
    path: ~/.cache/selenium
    key: ${{ runner.os }}-selenium-drivers
```

## 🔍 **Debugging on Linux**

### **Network Debugging:**
```bash
# Test connectivity
ping -c 3 192.168.1.33
telnet 192.168.1.33 4444
nmap -p 4444 192.168.1.33

# Check routing
traceroute 192.168.1.33
ip route show

# Test from different networks
curl -v http://192.168.1.33:4444/wd/hub/status
```

### **Process Debugging:**
```bash
# Monitor test execution
ps aux | grep pytest
htop

# Check network connections
netstat -tulpn | grep 4444
ss -tulpn | grep 4444

# Monitor logs
tail -f /var/log/selenium-grid.log
journalctl -f -u selenium-grid
```

## 📋 **Complete Linux Workflow Example**

```yaml
name: Linux Selenium Grid Tests

on:
  workflow_dispatch:
    inputs:
      grid_type:
        description: 'Grid Access Type'
        required: true
        default: 'self-hosted'
        type: choice
        options:
        - self-hosted
        - public
        - local-tunnel

jobs:
  linux-selenium-tests:
    runs-on: ${{ github.event.inputs.grid_type == 'self-hosted' && 'self-hosted' || 'ubuntu-latest' }}
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Linux Environment
      run: |
        echo "🐧 Running on Linux: $(uname -a)"
        echo "🔧 Available CPU cores: $(nproc)"
        echo "💾 Available memory: $(free -h)"
        
        # Install system dependencies
        if [ "${{ runner.os }}" == "Linux" ]; then
          sudo apt-get update
          sudo apt-get install -y curl jq
        fi
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Configure Grid Access
      run: |
        case "${{ github.event.inputs.grid_type }}" in
          "self-hosted")
            export SELENIUM_HUB_URL=http://192.168.1.33:4444
            ;;
          "public")
            export SELENIUM_HUB_URL=http://your-public-ip:4444
            ;;
          "local-tunnel")
            export SELENIUM_HUB_URL=https://your-ngrok-url.ngrok.io
            ;;
        esac
        
        echo "SELENIUM_HUB_URL=$SELENIUM_HUB_URL" >> $GITHUB_ENV
    
    - name: Test Grid Connectivity
      run: |
        echo "🔍 Testing grid at: $SELENIUM_HUB_URL"
        
        if curl -f --connect-timeout 10 "$SELENIUM_HUB_URL/wd/hub/status"; then
          echo "✅ Grid is accessible from Linux runner"
          curl -s "$SELENIUM_HUB_URL/wd/hub/status" | jq -r '.value.message'
        else
          echo "❌ Grid is not accessible"
          exit 1
        fi
    
    - name: Run Tests on Linux
      run: |
        export USE_SELENIUM_GRID=true
        export SELENIUM_BROWSER=chrome
        export PYTHONHTTPSVERIFY=0
        
        # Run with Linux optimizations
        python run_complete_automation.py
    
    - name: Upload Linux Results
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: linux-test-results
        path: |
          reports/
          screenshots/
```

## 🎯 **Summary**

**✅ Your commands will work perfectly on Linux GitHub Actions runners**

**🔧 Key considerations:**
1. **Network Access**: Use self-hosted runner or expose grid publicly
2. **Linux Tools**: Leverage curl, jq, and better parallel processing
3. **Performance**: Linux runners are often faster and more efficient
4. **Debugging**: Better tooling available for troubleshooting

**🚀 Recommended approach:**
- Use **self-hosted runner** for private grid access
- Optimize workflows for Linux performance
- Leverage Linux-native tools for better processing