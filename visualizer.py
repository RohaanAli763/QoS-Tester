"""
Visualization module for displaying network performance test results.
Uses Matplotlib for creating charts and graphs.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from typing import List, Dict
import numpy as np


class Visualizer:
    """Handles visualization of network performance test results."""
    
    def __init__(self):
        """Initialize the visualizer."""
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def display_single_result(self, result: Dict):
        """
        Display results from a single test in a bar chart.
        
        Args:
            result: Dictionary containing test results
        """
        if result.get('test_status') != 'success':
            print(f"Cannot visualize failed test: {result.get('error', 'Unknown error')}")
            return
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f'Network Performance Test Results\n{result.get("server_host")}:{result.get("server_port")}', 
                     fontsize=14, fontweight='bold')
        
        # Bandwidth
        ax1 = axes[0, 0]
        bandwidth = result.get('bandwidth_mbps', 0)
        ax1.bar(['Bandwidth'], [bandwidth], color='#2ecc71', width=0.5)
        ax1.set_ylabel('Mbps')
        ax1.set_title('Bandwidth')
        ax1.set_ylim(0, max(bandwidth * 1.2, 10))
        ax1.text(0, bandwidth, f'{bandwidth:.2f} Mbps', ha='center', va='bottom', fontweight='bold')
        
        # Latency
        ax2 = axes[0, 1]
        latency = result.get('latency_ms', 0)
        color = '#3498db' if latency < 50 else '#e74c3c'
        ax2.bar(['Latency'], [latency], color=color, width=0.5)
        ax2.set_ylabel('ms')
        ax2.set_title('Latency')
        ax2.set_ylim(0, max(latency * 1.2, 10))
        ax2.text(0, latency, f'{latency:.2f} ms', ha='center', va='bottom', fontweight='bold')
        
        # Jitter
        ax3 = axes[1, 0]
        jitter = result.get('jitter_ms', 0)
        color = '#9b59b6' if jitter < 5 else '#e67e22'
        ax3.bar(['Jitter'], [jitter], color=color, width=0.5)
        ax3.set_ylabel('ms')
        ax3.set_title('Jitter')
        ax3.set_ylim(0, max(jitter * 1.2, 5))
        ax3.text(0, jitter, f'{jitter:.2f} ms', ha='center', va='bottom', fontweight='bold')
        
        # Packet Loss
        ax4 = axes[1, 1]
        packet_loss = result.get('packet_loss_percent', 0)
        color = '#27ae60' if packet_loss < 1 else '#c0392b'
        ax4.bar(['Packet Loss'], [packet_loss], color=color, width=0.5)
        ax4.set_ylabel('%')
        ax4.set_title('Packet Loss')
        ax4.set_ylim(0, max(packet_loss * 1.5, 5))
        ax4.text(0, packet_loss, f'{packet_loss:.2f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def plot_history(self, results: List[Dict], metric: str = 'bandwidth_mbps'):
        """
        Plot historical results for a specific metric.
        
        Args:
            results: List of test results dictionaries
            metric: Metric to plot ('bandwidth_mbps', 'latency_ms', 'jitter_ms', 'packet_loss_percent')
        """
        if not results:
            print("No results to visualize")
            return
        
        # Extract timestamps and values
        timestamps = []
        values = []
        
        for result in results:
            if result.get(metric) is not None:
                try:
                    timestamp = datetime.strptime(result['timestamp'], '%Y-%m-%d %H:%M:%S')
                    timestamps.append(timestamp)
                    values.append(result[metric])
                except (ValueError, KeyError):
                    continue
        
        if not timestamps:
            print(f"No valid data for metric: {metric}")
            return
        
        # Create plot
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, values, marker='o', linestyle='-', linewidth=2, markersize=6)
        
        # Format based on metric
        metric_info = {
            'bandwidth_mbps': ('Bandwidth Over Time', 'Bandwidth (Mbps)', '#2ecc71'),
            'latency_ms': ('Latency Over Time', 'Latency (ms)', '#3498db'),
            'jitter_ms': ('Jitter Over Time', 'Jitter (ms)', '#9b59b6'),
            'packet_loss_percent': ('Packet Loss Over Time', 'Packet Loss (%)', '#e74c3c')
        }
        
        title, ylabel, color = metric_info.get(metric, ('Metric Over Time', 'Value', '#34495e'))
        
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('Time', fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Format x-axis
        plt.gcf().autofmt_xdate()
        
        # Add average line
        avg_value = np.mean(values)
        plt.axhline(y=avg_value, color='r', linestyle='--', label=f'Average: {avg_value:.2f}')
        plt.legend()
        
        plt.tight_layout()
        plt.show()
    
    def plot_comparison(self, results: List[Dict]):
        """
        Create a comprehensive comparison chart for multiple test results.
        
        Args:
            results: List of test results dictionaries
        """
        if not results:
            print("No results to visualize")
            return
        
        # Prepare data
        timestamps = []
        bandwidth = []
        latency = []
        jitter = []
        packet_loss = []
        
        for result in results:
            try:
                timestamp = datetime.strptime(result['timestamp'], '%Y-%m-%d %H:%M:%S')
                timestamps.append(timestamp)
                bandwidth.append(result.get('bandwidth_mbps', 0))
                latency.append(result.get('latency_ms', 0))
                jitter.append(result.get('jitter_ms', 0))
                packet_loss.append(result.get('packet_loss_percent', 0))
            except (ValueError, KeyError):
                continue
        
        if not timestamps:
            print("No valid data to visualize")
            return
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Network Performance Comparison', fontsize=16, fontweight='bold')
        
        # Bandwidth
        axes[0, 0].plot(timestamps, bandwidth, marker='o', color='#2ecc71', linewidth=2)
        axes[0, 0].set_title('Bandwidth')
        axes[0, 0].set_ylabel('Mbps')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Latency
        axes[0, 1].plot(timestamps, latency, marker='o', color='#3498db', linewidth=2)
        axes[0, 1].set_title('Latency')
        axes[0, 1].set_ylabel('ms')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Jitter
        axes[1, 0].plot(timestamps, jitter, marker='o', color='#9b59b6', linewidth=2)
        axes[1, 0].set_title('Jitter')
        axes[1, 0].set_ylabel('ms')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Packet Loss
        axes[1, 1].plot(timestamps, packet_loss, marker='o', color='#e74c3c', linewidth=2)
        axes[1, 1].set_title('Packet Loss')
        axes[1, 1].set_ylabel('%')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        # Format x-axis for all subplots
        for ax in axes.flat:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        
        plt.tight_layout()
        plt.show()
    
    def generate_report(self, result: Dict):
        """
        Generate and print a text report of test results.
        
        Args:
            result: Dictionary containing test results
        """
        print("\n" + "="*60)
        print("NETWORK PERFORMANCE TEST REPORT")
        print("="*60)
        print(f"\nServer: {result.get('server_host')}:{result.get('server_port')}")
        print(f"Test Duration: {result.get('test_duration')} seconds")
        print(f"Status: {result.get('test_status').upper()}")
        
        # Show errors if any
        if 'errors' in result and result['errors']:
            print("\n" + "-"*60)
            print("ERRORS ENCOUNTERED:")
            print("-"*60)
            for error in result['errors']:
                print(f"  • {error}")
        
        print("\n" + "-"*60)
        print("RESULTS:")
        print("-"*60)
        
        if result.get('test_status') in ['success', 'partial']:
            bandwidth = result.get('bandwidth_mbps') or 0
            latency = result.get('latency_ms') or 0
            jitter = result.get('jitter_ms') or 0
            packet_loss = result.get('packet_loss_percent') or 0
            
            print(f"  Bandwidth:    {bandwidth:.2f} Mbps")
            print(f"  Latency:      {latency:.2f} ms")
            print(f"  Jitter:       {jitter:.2f} ms" if jitter else "  Jitter:       N/A")
            print(f"  Packet Loss:  {packet_loss:.2f}%" if packet_loss is not None else "  Packet Loss:  N/A")
            print(f"\n  Bytes Sent:     {result.get('bytes_sent', 0):,}")
            print(f"  Bytes Received: {result.get('bytes_received', 0):,}")
            
            # Quality assessment
            print("\n" + "-"*60)
            print("QUALITY ASSESSMENT:")
            print("-"*60)
            
            if bandwidth > 50:
                print("  Bandwidth: ✓ Excellent")
            elif bandwidth > 10:
                print("  Bandwidth: ○ Good")
            else:
                print("  Bandwidth: ✗ Poor")
            
            if latency < 20:
                print("  Latency:   ✓ Excellent")
            elif latency < 50:
                print("  Latency:   ○ Good")
            else:
                print("  Latency:   ✗ High")
            
            if jitter < 5:
                print("  Jitter:    ✓ Excellent")
            elif jitter < 20:
                print("  Jitter:    ○ Acceptable")
            else:
                print("  Jitter:    ✗ High")
            
            if packet_loss < 0.5:
                print("  Packet Loss: ✓ Excellent")
            elif packet_loss < 2:
                print("  Packet Loss: ○ Acceptable")
            else:
                print("  Packet Loss: ✗ High")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")
        
        print("="*60 + "\n")
