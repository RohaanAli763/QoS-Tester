# QoS Tester: Network Performance Benchmarking Tool

A comprehensive network performance testing tool that measures bandwidth, latency, jitter, and packet loss using iperf3 APIs with data visualization and SQLite storage.

## Features

- **Bandwidth Testing**: Measure TCP/UDP throughput
- **Latency Measurement**: RTT estimation
- **Jitter Analysis**: UDP jitter measurement
- **Packet Loss Detection**: Track packet loss percentage
- **Data Persistence**: SQLite database for storing test results
- **Rich Visualizations**: Matplotlib charts and graphs
- **Historical Analysis**: Compare and track performance over time
- **Command-Line Interface**: Easy-to-use CLI with multiple commands

## Technologies

- **Python**: Core programming language
- **iperf3**: Network performance testing (subprocess-based)
- **Matplotlib**: Data visualization
- **SQLite**: Result storage and history tracking

## Prerequisites

1. **Python 3.7+** installed on your system
2. **iperf3** installed on both client and server machines

### Installing iperf3

**Windows:**

```powershell
# Using Chocolatey
choco install iperf3

# Or download from: https://iperf.fr/iperf-download.php
```

**Linux:**

```bash
sudo apt-get install iperf3  # Debian/Ubuntu
sudo yum install iperf3      # RHEL/CentOS
```

**macOS:**

```bash
brew install iperf3
```

## Installation

1. Clone or download this project:

```powershell
cd d:\HP\Projects\Cn-Project
```

2. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

## Usage

### Option 1: GUI Mode (Recommended)

Launch the graphical user interface:

```powershell
python gui.py
```

The GUI provides:

- **Easy test configuration** with dropdown server selection
- **Real-time results** display with color-coded output
- **History viewer** with sortable table
- **Built-in visualizations** with multiple chart types
- **One-click operations** for all features

### Option 2: Command-Line Mode

#### Starting an iperf3 Server

Before running tests, you need an iperf3 server running:

```powershell
# Start server on default port (5201)
iperf3 -s

# Start server on custom port
iperf3 -s -p 5202
```

#### Basic Test

```powershell
python main.py test --server localhost
```

#### Test with Custom Parameters

```powershell
# Custom port and duration
python main.py test --server 192.168.1.100 --port 5201 --duration 30

# Test without saving to database
python main.py test --server iperf.example.com --no-save

# Test without visualization
python main.py test --server 10.0.0.1 --no-visualize
```

### Viewing History

#### View Recent Tests

```powershell
# Show last 10 tests
python main.py history

# Show last 20 tests
python main.py history --limit 20
```

#### Plot Specific Metrics

```powershell
# Plot bandwidth over time
python main.py history --metric bandwidth_mbps

# Plot latency over time
python main.py history --metric latency_ms

# Plot jitter over time
python main.py history --metric jitter_ms

# Plot packet loss over time
python main.py history --metric packet_loss_percent
```

### Comparing Tests

```powershell
# Compare last 10 tests
python main.py compare

# Compare last 20 tests
python main.py compare --limit 20
```

### Clearing History

```powershell
python main.py clear
```

## Command Reference

### test

Run a network performance test.

**Arguments:**

- `--server, -s`: iperf3 server hostname or IP (required)
- `--port, -p`: Server port (default: 5201)
- `--duration, -d`: Test duration in seconds (default: 10)
- `--no-save`: Don't save results to database
- `--no-visualize`: Don't show visualizations

### history

View test history.

**Arguments:**

- `--limit, -l`: Number of results to show (default: 10)
- `--metric, -m`: Plot specific metric (bandwidth_mbps, latency_ms, jitter_ms, packet_loss_percent)

### compare

Compare multiple test results with visualization.

**Arguments:**

- `--limit, -l`: Number of results to compare (default: 10)

### clear

Clear all test history from database.

## Metrics Explained

### Bandwidth

- **Unit**: Mbps (Megabits per second)
- **Description**: Data transfer rate
- **Good**: > 50 Mbps
- **Acceptable**: > 10 Mbps

### Latency

- **Unit**: ms (milliseconds)
- **Description**: Round-trip time (RTT)
- **Excellent**: < 20 ms
- **Good**: < 50 ms

### Jitter

- **Unit**: ms (milliseconds)
- **Description**: Variation in packet delay
- **Excellent**: < 5 ms
- **Acceptable**: < 20 ms

### Packet Loss

- **Unit**: % (percentage)
- **Description**: Percentage of packets lost
- **Excellent**: < 0.5%
- **Acceptable**: < 2%

## Project Structure

```
Cn-Project/
├── gui.py                          # GUI application (Tkinter)
├── main.py                         # CLI application entry point
├── network_tester_subprocess.py    # Network testing module (iperf3)
├── database.py                     # SQLite database management
├── visualizer.py                   # Matplotlib visualization
├── requirements.txt                # Python dependencies
├── launch_gui.bat                  # Windows GUI launcher
├── README.md                       # Documentation
└── qos_results.db                  # SQLite database (created on first run)
```

## GUI Features

### Run Test Tab

- Configure server hostname/IP
- Quick select from popular iperf3 servers
- Set custom port and test duration
- Real-time progress indicator
- Color-coded results display
- Quality assessment indicators

### History Tab

- View all past test results
- Sortable columns (ID, Timestamp, Server, Metrics)
- Filter by number of results
- One-click refresh and clear history

### Visualizations Tab

- Multiple chart types:
  - Bandwidth History
  - Latency History
  - Jitter History
  - Packet Loss History
  - All Metrics Comparison (4-panel view)
- Configurable number of results to display
- Interactive matplotlib charts

## Example Output

```
============================================================
Starting Comprehensive Network Performance Test
============================================================

Running TCP bandwidth test to 192.168.1.100:5201...
Running UDP test to measure jitter and packet loss...
Measuring latency to 192.168.1.100:5201...

============================================================
Test Complete
============================================================

============================================================
NETWORK PERFORMANCE TEST REPORT
============================================================

Server: 192.168.1.100:5201
Test Duration: 10 seconds
Status: SUCCESS

------------------------------------------------------------
RESULTS:
------------------------------------------------------------
  Bandwidth:    95.34 Mbps
  Latency:      12.45 ms
  Jitter:       2.31 ms
  Packet Loss:  0.15%

  Bytes Sent:     119,175,168
  Bytes Received: 119,157,248

------------------------------------------------------------
QUALITY ASSESSMENT:
------------------------------------------------------------
  Bandwidth: ✓ Excellent
  Latency:   ✓ Excellent
  Jitter:    ✓ Excellent
  Packet Loss: ✓ Excellent
============================================================

✓ Results saved to database (ID: 1)
```

## Troubleshooting

### "Connection refused" error

- Ensure iperf3 server is running on the target host
- Check firewall settings allow connections on the specified port
- Verify the server hostname/IP is correct

### "Module not found" error

- Install dependencies: `pip install -r requirements.txt`
- Ensure you're using Python 3.7 or higher

### Visualization not showing

- Ensure matplotlib is properly installed
- On some systems, you may need to install tkinter:
  - Windows: Usually included with Python
  - Linux: `sudo apt-get install python3-tk`

## License

This project is created for educational purposes as part of a Computer Networks course project.

## Author

Created as part of the CN-Project coursework.
