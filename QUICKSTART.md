# QoS Tester - Quick Start Guide

## Launching the Application

### GUI Mode (Easiest)

**Option 1: Double-click**

- Simply double-click `launch_gui.bat`

**Option 2: Command line**

```powershell
python gui.py
```

### CLI Mode

```powershell
python main.py test --server localhost
```

## Quick WiFi Testing Guide

### 1. Setup iperf3 Server

**On another device on your WiFi:**

```powershell
iperf3 -s
```

**Find that device's IP address:**

```powershell
ipconfig
```

Look for "IPv4 Address" (e.g., 192.168.1.100)

### 2. Run Test from GUI

1. Launch GUI: `python gui.py`
2. In "Run Test" tab:
   - Enter server IP in "Server Host" field
   - Click "▶ Run Test"
3. View results in the same tab
4. Check "History" tab to see all tests
5. Use "Visualizations" tab for charts

### 3. Interpreting Results

**Good WiFi Performance:**

- 5GHz: 200-500 Mbps bandwidth
- 2.4GHz: 50-150 Mbps bandwidth
- Latency: < 10 ms
- Jitter: < 5 ms
- Packet Loss: < 1%

**Poor WiFi Performance:**

- Bandwidth: < 10 Mbps
- Latency: > 50 ms
- Jitter: > 20 ms
- Packet Loss: > 2%

## Testing Public Servers

Try these public iperf3 servers in the GUI dropdown:

- `iperf.he.net` (port 5201)
- `bouygues.iperf.fr` (port 5200)
- `ping.online.net` (port 5200)

## Common Issues

**"Connection refused"**

- Make sure iperf3 server is running: `iperf3 -s`
- Check firewall settings
- Verify IP address is correct

**"No module named 'tkinter'"**

- Tkinter usually comes with Python
- On Linux: `sudo apt-get install python3-tk`

**"iperf3 not found"**

- Install iperf3: `choco install iperf3` (Windows)
- Add to PATH if needed

## GUI Tips

1. **Quick Server Selection**: Use the dropdown to quickly select common servers
2. **Real-time Updates**: Results appear as tests run
3. **Color Coding**:
   - Green = Success/Excellent
   - Red = Error/Poor
   - Blue = Info
4. **History Filtering**: Choose how many results to display (10/20/50/All)
5. **Chart Types**: Switch between different metrics or view all at once

## Keyboard Shortcuts

- **Alt+Tab**: Switch between tabs
- **Ctrl+C**: Copy selected text from results

## Support

For issues or questions:

1. Check that iperf3 is installed: `iperf3 --version`
2. Verify Python version: `python --version` (3.7+)
3. Ensure all dependencies are installed: `pip install -r requirements.txt`
