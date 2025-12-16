"""
QoS Tester: Network Performance Benchmarking Tool
Main application interface for running network tests and visualizing results.
"""

import argparse
import sys
from network_tester_subprocess import NetworkTester
from database import DatabaseManager
from visualizer import Visualizer


class QoSTester:
    """Main application class for the QoS Tester."""
    
    def __init__(self):
        """Initialize the QoS Tester."""
        self.db = DatabaseManager()
        self.visualizer = Visualizer()
        self.tester = None
    
    def run_test(self, server_host: str, server_port: int = 5201, duration: int = 10, 
                 save: bool = True, visualize: bool = True):
        """
        Run a complete network performance test.
        
        Args:
            server_host: iperf3 server hostname or IP
            server_port: iperf3 server port
            duration: Test duration in seconds
            save: Whether to save results to database
            visualize: Whether to display visualization
        """
        self.tester = NetworkTester(server_host, server_port)
        
        # Run comprehensive test
        result = self.tester.run_full_test(duration=duration)
        
        # Display report
        self.visualizer.generate_report(result)
        
        # Save to database
        if save and result.get('test_status') == 'success':
            test_id = self.db.save_test_result(result)
            print(f"✓ Results saved to database (ID: {test_id})")
        
        # Visualize results
        if visualize and result.get('test_status') == 'success':
            print("\nGenerating visualizations...")
            self.visualizer.display_single_result(result)
        
        return result
    
    def view_history(self, limit: int = 10, metric: str = None):
        """
        View historical test results.
        
        Args:
            limit: Number of recent results to show
            metric: Specific metric to plot (optional)
        """
        results = self.db.get_all_results(limit=limit)
        
        if not results:
            print("No test results found in database.")
            return
        
        print(f"\nShowing last {len(results)} test results:\n")
        print("-" * 100)
        print(f"{'ID':<5} {'Timestamp':<20} {'Server':<20} {'Bandwidth':<12} {'Latency':<10} {'Jitter':<10} {'Loss':<8}")
        print("-" * 100)
        
        for result in results:
            print(f"{result['id']:<5} "
                  f"{result['timestamp']:<20} "
                  f"{result['server_host']}:{result['server_port']:<15} "
                  f"{result['bandwidth_mbps']:.2f} Mbps   "
                  f"{result['latency_ms']:.2f} ms   "
                  f"{result['jitter_ms']:.2f} ms   "
                  f"{result['packet_loss_percent']:.2f}%")
        
        print("-" * 100 + "\n")
        
        # Plot specific metric if requested
        if metric:
            if metric in ['bandwidth_mbps', 'latency_ms', 'jitter_ms', 'packet_loss_percent']:
                self.visualizer.plot_history(results, metric=metric)
            else:
                print(f"Invalid metric: {metric}")
                print("Valid metrics: bandwidth_mbps, latency_ms, jitter_ms, packet_loss_percent")
    
    def compare_tests(self, limit: int = 10):
        """
        Compare multiple test results with visualization.
        
        Args:
            limit: Number of recent results to compare
        """
        results = self.db.get_all_results(limit=limit)
        
        if not results:
            print("No test results found in database.")
            return
        
        if len(results) < 2:
            print("Need at least 2 test results for comparison.")
            return
        
        print(f"\nComparing {len(results)} test results...")
        self.visualizer.plot_comparison(results)
    
    def clear_history(self):
        """Clear all test results from the database."""
        confirm = input("Are you sure you want to clear all test results? (yes/no): ")
        if confirm.lower() == 'yes':
            self.db.clear_all_results()
            print("✓ All test results cleared.")
        else:
            print("Operation cancelled.")
    
    def close(self):
        """Clean up resources."""
        self.db.close()


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description='QoS Tester: Network Performance Benchmarking Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run test against iperf3 server
  python main.py test --server 192.168.1.100
  
  # Run test with custom duration and port
  python main.py test --server iperf.example.com --port 5201 --duration 30
  
  # View test history
  python main.py history --limit 20
  
  # Plot specific metric
  python main.py history --metric bandwidth_mbps
  
  # Compare multiple tests
  python main.py compare --limit 10
  
  # Clear all history
  python main.py clear

Note: Requires iperf3 server to be running on the target host.
      To start an iperf3 server: iperf3 -s
        """)
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run network performance test')
    test_parser.add_argument('--server', '-s', required=True, help='iperf3 server hostname or IP')
    test_parser.add_argument('--port', '-p', type=int, default=5201, help='Server port (default: 5201)')
    test_parser.add_argument('--duration', '-d', type=int, default=10, help='Test duration in seconds (default: 10)')
    test_parser.add_argument('--no-save', action='store_true', help='Do not save results to database')
    test_parser.add_argument('--no-visualize', action='store_true', help='Do not show visualizations')
    
    # History command
    history_parser = subparsers.add_parser('history', help='View test history')
    history_parser.add_argument('--limit', '-l', type=int, default=10, help='Number of results to show (default: 10)')
    history_parser.add_argument('--metric', '-m', choices=['bandwidth_mbps', 'latency_ms', 'jitter_ms', 'packet_loss_percent'],
                               help='Plot specific metric over time')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare multiple test results')
    compare_parser.add_argument('--limit', '-l', type=int, default=10, help='Number of results to compare (default: 10)')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear all test history')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize QoS Tester
    qos_tester = QoSTester()
    
    try:
        if args.command == 'test':
            qos_tester.run_test(
                server_host=args.server,
                server_port=args.port,
                duration=args.duration,
                save=not args.no_save,
                visualize=not args.no_visualize
            )
        
        elif args.command == 'history':
            qos_tester.view_history(limit=args.limit, metric=args.metric)
        
        elif args.command == 'compare':
            qos_tester.compare_tests(limit=args.limit)
        
        elif args.command == 'clear':
            qos_tester.clear_history()
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
    finally:
        qos_tester.close()


if __name__ == '__main__':
    main()
