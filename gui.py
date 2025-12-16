"""
QoS Tester GUI - Graphical User Interface using Tkinter
Provides an easy-to-use interface for network performance testing.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from network_tester_subprocess import NetworkTester
from database import DatabaseManager
from visualizer import Visualizer
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sys
from io import StringIO


class QoSTesterGUI:
    """Main GUI application for QoS Tester."""
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("QoS Tester - Network Performance Benchmarking Tool")
        self.root.geometry("1000x700")
        
        # Initialize components
        self.db = DatabaseManager()
        self.visualizer = Visualizer()
        self.tester = None
        self.test_running = False
        
        # Create GUI elements
        self.create_widgets()
        
        # Load initial history
        self.refresh_history()
    
    def create_widgets(self):
        """Create all GUI widgets."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        self.test_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)
        self.visualization_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.test_tab, text='Run Test')
        self.notebook.add(self.history_tab, text='History')
        self.notebook.add(self.visualization_tab, text='Visualizations')
        
        # Setup each tab
        self.setup_test_tab()
        self.setup_history_tab()
        self.setup_visualization_tab()
    
    def setup_test_tab(self):
        """Setup the test configuration and execution tab."""
        # Configuration Frame
        config_frame = ttk.LabelFrame(self.test_tab, text="Test Configuration", padding=10)
        config_frame.pack(fill='x', padx=10, pady=10)
        
        # Server Host
        ttk.Label(config_frame, text="Server Host:").grid(row=0, column=0, sticky='w', pady=5)
        self.host_entry = ttk.Entry(config_frame, width=30)
        self.host_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=5)
        self.host_entry.insert(0, "localhost")
        
        # Popular servers dropdown
        ttk.Label(config_frame, text="Quick Select:").grid(row=0, column=2, sticky='w', pady=5, padx=(10, 0))
        self.quick_servers = ttk.Combobox(config_frame, values=[
            "localhost",
            "iperf.he.net",
            "bouygues.iperf.fr",
            "ping.online.net"
        ], width=20, state='readonly')
        self.quick_servers.grid(row=0, column=3, sticky='ew', pady=5, padx=5)
        self.quick_servers.bind('<<ComboboxSelected>>', self.on_server_select)
        
        # Server Port
        ttk.Label(config_frame, text="Server Port:").grid(row=1, column=0, sticky='w', pady=5)
        self.port_entry = ttk.Entry(config_frame, width=30)
        self.port_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=5)
        self.port_entry.insert(0, "5201")
        
        # Test Duration
        ttk.Label(config_frame, text="Test Duration (sec):").grid(row=1, column=2, sticky='w', pady=5, padx=(10, 0))
        self.duration_entry = ttk.Entry(config_frame, width=20)
        self.duration_entry.grid(row=1, column=3, sticky='ew', pady=5, padx=5)
        self.duration_entry.insert(0, "10")
        
        config_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(3, weight=1)
        
        # Control Buttons
        button_frame = ttk.Frame(self.test_tab)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        self.run_button = ttk.Button(button_frame, text="▶ Run Test", command=self.run_test, style='Accent.TButton')
        self.run_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⬛ Stop", command=self.stop_test, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Clear Results", command=self.clear_results).pack(side='left', padx=5)
        
        # Progress Bar
        self.progress = ttk.Progressbar(self.test_tab, mode='indeterminate')
        self.progress.pack(fill='x', padx=10, pady=5)
        
        # Results Display
        results_frame = ttk.LabelFrame(self.test_tab, text="Test Results", padding=10)
        results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=20, wrap='word', font=('Consolas', 9))
        self.results_text.pack(fill='both', expand=True)
        
        # Configure text tags for colored output
        self.results_text.tag_config('success', foreground='green')
        self.results_text.tag_config('error', foreground='red')
        self.results_text.tag_config('info', foreground='blue')
        self.results_text.tag_config('header', foreground='purple', font=('Consolas', 9, 'bold'))
    
    def setup_history_tab(self):
        """Setup the history viewing tab."""
        # Control Frame
        control_frame = ttk.Frame(self.history_tab)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(control_frame, text="🔄 Refresh", command=self.refresh_history).pack(side='left', padx=5)
        
        ttk.Label(control_frame, text="Show:").pack(side='left', padx=(20, 5))
        self.history_limit = ttk.Combobox(control_frame, values=['10', '20', '50', '100', 'All'], width=10, state='readonly')
        self.history_limit.set('10')
        self.history_limit.pack(side='left', padx=5)
        self.history_limit.bind('<<ComboboxSelected>>', lambda e: self.refresh_history())
        
        ttk.Button(control_frame, text="🗑️ Clear All History", command=self.clear_all_history).pack(side='right', padx=5)
        
        # Treeview for history
        tree_frame = ttk.Frame(self.history_tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        columns = ('ID', 'Timestamp', 'Server', 'Bandwidth', 'Latency', 'Jitter', 'Loss', 'Status')
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', 
                                         yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.config(command=self.history_tree.yview)
        hsb.config(command=self.history_tree.xview)
        
        # Configure columns
        self.history_tree.heading('ID', text='ID')
        self.history_tree.heading('Timestamp', text='Timestamp')
        self.history_tree.heading('Server', text='Server')
        self.history_tree.heading('Bandwidth', text='Bandwidth (Mbps)')
        self.history_tree.heading('Latency', text='Latency (ms)')
        self.history_tree.heading('Jitter', text='Jitter (ms)')
        self.history_tree.heading('Loss', text='Packet Loss (%)')
        self.history_tree.heading('Status', text='Status')
        
        self.history_tree.column('ID', width=40)
        self.history_tree.column('Timestamp', width=150)
        self.history_tree.column('Server', width=150)
        self.history_tree.column('Bandwidth', width=120)
        self.history_tree.column('Latency', width=100)
        self.history_tree.column('Jitter', width=100)
        self.history_tree.column('Loss', width=100)
        self.history_tree.column('Status', width=80)
        
        # Grid layout
        self.history_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
    
    def setup_visualization_tab(self):
        """Setup the visualization tab."""
        # Control Frame
        control_frame = ttk.Frame(self.visualization_tab)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(control_frame, text="Chart Type:").pack(side='left', padx=5)
        
        self.chart_type = ttk.Combobox(control_frame, values=[
            'Bandwidth History',
            'Latency History',
            'Jitter History',
            'Packet Loss History',
            'All Metrics Comparison'
        ], width=25, state='readonly')
        self.chart_type.set('Bandwidth History')
        self.chart_type.pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="📊 Generate Chart", command=self.generate_chart).pack(side='left', padx=10)
        
        ttk.Label(control_frame, text="Results:").pack(side='left', padx=(20, 5))
        self.chart_limit = ttk.Combobox(control_frame, values=['5', '10', '20', '50'], width=10, state='readonly')
        self.chart_limit.set('10')
        self.chart_limit.pack(side='left', padx=5)
        
        # Canvas Frame for matplotlib
        self.canvas_frame = ttk.Frame(self.visualization_tab)
        self.canvas_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Initial empty chart
        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def on_server_select(self, event):
        """Handle server selection from dropdown."""
        server = self.quick_servers.get()
        self.host_entry.delete(0, tk.END)
        self.host_entry.insert(0, server)
        
        # Set appropriate port for known servers
        if 'bouygues' in server or 'ping.online' in server:
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, "5200")
        else:
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, "5201")
    
    def run_test(self):
        """Run the network performance test."""
        if self.test_running:
            return
        
        # Get configuration
        host = self.host_entry.get().strip()
        port_str = self.port_entry.get().strip()
        duration_str = self.duration_entry.get().strip()
        
        # Validate inputs
        if not host:
            messagebox.showerror("Error", "Please enter a server host.")
            return
        
        try:
            port = int(port_str)
            duration = int(duration_str)
        except ValueError:
            messagebox.showerror("Error", "Port and duration must be integers.")
            return
        
        # Clear previous results
        self.results_text.delete('1.0', tk.END)
        
        # Update UI
        self.test_running = True
        self.run_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress.start()
        
        # Run test in separate thread
        thread = threading.Thread(target=self._run_test_thread, args=(host, port, duration))
        thread.daemon = True
        thread.start()
    
    def _run_test_thread(self, host, port, duration):
        """Run test in a separate thread."""
        try:
            # Redirect stdout to capture print statements
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            # Create tester and run
            self.tester = NetworkTester(host, port)
            result = self.tester.run_full_test(duration=duration)
            
            # Get captured output
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            # Display results in GUI
            self.root.after(0, self._display_results, result, output)
            
            # Save to database in main thread
            if result.get('test_status') in ['success', 'partial']:
                self.root.after(0, self._save_result, result)
            
        except Exception as e:
            sys.stdout = old_stdout
            self.root.after(0, self._display_error, str(e))
        finally:
            self.root.after(0, self._test_complete)
    
    def _display_results(self, result, output):
        """Display test results in the GUI."""
        self.results_text.insert(tk.END, output)
        
        # Generate report
        self.results_text.insert(tk.END, "\n" + "="*60 + "\n", 'header')
        self.results_text.insert(tk.END, "NETWORK PERFORMANCE TEST REPORT\n", 'header')
        self.results_text.insert(tk.END, "="*60 + "\n\n", 'header')
        
        self.results_text.insert(tk.END, f"Server: {result.get('server_host')}:{result.get('server_port')}\n")
        self.results_text.insert(tk.END, f"Test Duration: {result.get('test_duration')} seconds\n")
        
        status = result.get('test_status', 'unknown').upper()
        status_tag = 'success' if status == 'SUCCESS' else 'error'
        self.results_text.insert(tk.END, f"Status: {status}\n", status_tag)
        
        if 'errors' in result and result['errors']:
            self.results_text.insert(tk.END, "\nERRORS:\n", 'error')
            for error in result['errors']:
                self.results_text.insert(tk.END, f"  • {error}\n", 'error')
        
        self.results_text.insert(tk.END, "\n" + "-"*60 + "\n")
        self.results_text.insert(tk.END, "RESULTS:\n", 'info')
        self.results_text.insert(tk.END, "-"*60 + "\n")
        
        if result.get('test_status') in ['success', 'partial']:
            self.results_text.insert(tk.END, f"  Bandwidth:    {result.get('bandwidth_mbps', 0):.2f} Mbps\n")
            self.results_text.insert(tk.END, f"  Latency:      {result.get('latency_ms', 0):.2f} ms\n")
            self.results_text.insert(tk.END, f"  Jitter:       {result.get('jitter_ms', 0):.2f} ms\n")
            self.results_text.insert(tk.END, f"  Packet Loss:  {result.get('packet_loss_percent', 0):.2f}%\n")
            
            self.results_text.insert(tk.END, "\n" + "-"*60 + "\n")
            self.results_text.insert(tk.END, "QUALITY ASSESSMENT:\n", 'info')
            self.results_text.insert(tk.END, "-"*60 + "\n")
            
            bandwidth = result.get('bandwidth_mbps', 0)
            latency = result.get('latency_ms', 0)
            jitter = result.get('jitter_ms', 0)
            packet_loss = result.get('packet_loss_percent', 0)
            
            bw_status = "✓ Excellent" if bandwidth > 50 else ("○ Good" if bandwidth > 10 else "✗ Poor")
            lat_status = "✓ Excellent" if latency < 20 else ("○ Good" if latency < 50 else "✗ High")
            jit_status = "✓ Excellent" if jitter < 5 else ("○ Acceptable" if jitter < 20 else "✗ High")
            loss_status = "✓ Excellent" if packet_loss < 0.5 else ("○ Acceptable" if packet_loss < 2 else "✗ High")
            
            self.results_text.insert(tk.END, f"  Bandwidth:    {bw_status}\n", 'success' if '✓' in bw_status else 'error')
            self.results_text.insert(tk.END, f"  Latency:      {lat_status}\n", 'success' if '✓' in lat_status else 'error')
            self.results_text.insert(tk.END, f"  Jitter:       {jit_status}\n", 'success' if '✓' in jit_status else 'error')
            self.results_text.insert(tk.END, f"  Packet Loss:  {loss_status}\n", 'success' if '✓' in loss_status else 'error')
        
        self.results_text.insert(tk.END, "="*60 + "\n", 'header')
        self.results_text.see(tk.END)
    
    def _display_error(self, error):
        """Display error message."""
        self.results_text.insert(tk.END, f"\n❌ Error: {error}\n", 'error')
    
    def _save_result(self, result):
        """Save test result to database (must run in main thread)."""
        try:
            test_id = self.db.save_test_result(result)
            self.results_text.insert(tk.END, f"\n✓ Results saved to database (ID: {test_id})\n", 'success')
            self.refresh_history()
        except Exception as e:
            self.results_text.insert(tk.END, f"\n❌ Failed to save results: {str(e)}\n", 'error')
    
    def _test_complete(self):
        """Clean up after test completion."""
        self.test_running = False
        self.run_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress.stop()
    
    def stop_test(self):
        """Stop the running test."""
        # Note: This is a placeholder. Actual implementation would need
        # to handle thread termination properly
        messagebox.showinfo("Info", "Test will stop after current operation completes.")
        self.test_running = False
    
    def clear_results(self):
        """Clear the results display."""
        self.results_text.delete('1.0', tk.END)
    
    def refresh_history(self):
        """Refresh the history table."""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Get limit
        limit_str = self.history_limit.get()
        limit = None if limit_str == 'All' else int(limit_str)
        
        # Fetch results
        results = self.db.get_all_results(limit=limit)
        
        # Populate tree
        for result in results:
            values = (
                result['id'],
                result['timestamp'],
                f"{result['server_host']}:{result['server_port']}",
                f"{result.get('bandwidth_mbps', 0):.2f}" if result.get('bandwidth_mbps') else 'N/A',
                f"{result.get('latency_ms', 0):.2f}" if result.get('latency_ms') else 'N/A',
                f"{result.get('jitter_ms', 0):.2f}" if result.get('jitter_ms') else 'N/A',
                f"{result.get('packet_loss_percent', 0):.2f}" if result.get('packet_loss_percent') else 'N/A',
                result.get('test_status', 'unknown')
            )
            self.history_tree.insert('', 'end', values=values)
    
    def clear_all_history(self):
        """Clear all history from database."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all test history?"):
            self.db.clear_all_results()
            self.refresh_history()
            messagebox.showinfo("Success", "All test history cleared.")
    
    def generate_chart(self):
        """Generate visualization chart."""
        chart_type = self.chart_type.get()
        limit = int(self.chart_limit.get())
        
        results = self.db.get_all_results(limit=limit)
        
        if not results:
            messagebox.showwarning("No Data", "No test results available to visualize.")
            return
        
        # Clear previous figure
        self.figure.clear()
        
        if chart_type == 'All Metrics Comparison':
            self._plot_comparison(results)
        else:
            self._plot_single_metric(results, chart_type)
        
        self.canvas.draw()
    
    def _plot_single_metric(self, results, chart_type):
        """Plot a single metric over time."""
        metric_map = {
            'Bandwidth History': ('bandwidth_mbps', 'Bandwidth (Mbps)', '#2ecc71'),
            'Latency History': ('latency_ms', 'Latency (ms)', '#3498db'),
            'Jitter History': ('jitter_ms', 'Jitter (ms)', '#9b59b6'),
            'Packet Loss History': ('packet_loss_percent', 'Packet Loss (%)', '#e74c3c')
        }
        
        metric, ylabel, color = metric_map[chart_type]
        
        # Extract data
        values = []
        labels = []
        for i, result in enumerate(reversed(results)):
            if result.get(metric) is not None:
                values.append(result[metric])
                labels.append(f"Test {result['id']}")
        
        if not values:
            messagebox.showwarning("No Data", f"No data available for {chart_type}.")
            return
        
        # Create plot
        ax = self.figure.add_subplot(111)
        ax.plot(range(len(values)), values, marker='o', color=color, linewidth=2, markersize=8)
        ax.set_title(chart_type, fontsize=14, fontweight='bold')
        ax.set_xlabel('Test Number', fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # Add average line
        import numpy as np
        avg = np.mean(values)
        ax.axhline(y=avg, color='r', linestyle='--', label=f'Average: {avg:.2f}')
        ax.legend()
        
        self.figure.tight_layout()
    
    def _plot_comparison(self, results):
        """Plot all metrics comparison."""
        # Prepare data
        bandwidth = []
        latency = []
        jitter = []
        packet_loss = []
        
        for result in reversed(results):
            bandwidth.append(result.get('bandwidth_mbps', 0))
            latency.append(result.get('latency_ms', 0))
            jitter.append(result.get('jitter_ms', 0))
            packet_loss.append(result.get('packet_loss_percent', 0))
        
        # Create subplots
        axes = self.figure.subplots(2, 2)
        self.figure.suptitle('Network Performance Comparison', fontsize=14, fontweight='bold')
        
        x = range(len(bandwidth))
        
        # Bandwidth
        axes[0, 0].plot(x, bandwidth, marker='o', color='#2ecc71', linewidth=2)
        axes[0, 0].set_title('Bandwidth')
        axes[0, 0].set_ylabel('Mbps')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Latency
        axes[0, 1].plot(x, latency, marker='o', color='#3498db', linewidth=2)
        axes[0, 1].set_title('Latency')
        axes[0, 1].set_ylabel('ms')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Jitter
        axes[1, 0].plot(x, jitter, marker='o', color='#9b59b6', linewidth=2)
        axes[1, 0].set_title('Jitter')
        axes[1, 0].set_ylabel('ms')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Packet Loss
        axes[1, 1].plot(x, packet_loss, marker='o', color='#e74c3c', linewidth=2)
        axes[1, 1].set_title('Packet Loss')
        axes[1, 1].set_ylabel('%')
        axes[1, 1].grid(True, alpha=0.3)
        
        self.figure.tight_layout()
    
    def on_closing(self):
        """Handle window closing."""
        self.db.close()
        self.root.destroy()


def main():
    """Main entry point for GUI application."""
    root = tk.Tk()
    
    # Set style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Create application
    app = QoSTesterGUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Run
    root.mainloop()


if __name__ == '__main__':
    main()
