"""
Quick visualization script - View your QoS test history with charts
"""

from database import DatabaseManager
from visualizer import Visualizer

def main():
    print("QoS Tester - Quick Visualization Tool")
    print("=" * 50)
    
    db = DatabaseManager()
    viz = Visualizer()
    
    # Get all results
    results = db.get_all_results()
    
    if not results:
        print("\n❌ No test results found in database.")
        print("Run some tests first: python main.py test --server localhost")
        db.close()
        return
    
    print(f"\n✓ Found {len(results)} test result(s)")
    print("\nRecent tests:")
    print("-" * 50)
    
    for i, result in enumerate(results[:5], 1):
        print(f"{i}. {result['timestamp']} - {result['server_host']}:{result['server_port']}")
        print(f"   Bandwidth: {result.get('bandwidth_mbps', 0):.2f} Mbps, "
              f"Latency: {result.get('latency_ms', 0):.2f} ms")
    
    print("\n" + "=" * 50)
    print("Generating visualizations...")
    print("=" * 50)
    
    if len(results) == 1:
        print("\n📊 Showing single test result...")
        viz.display_single_result(results[0])
    else:
        print("\n📊 Showing comparison of all tests...")
        viz.plot_comparison(results)
    
    # Also show bandwidth history
    print("\n📈 Showing bandwidth trend...")
    viz.plot_history(results, metric='bandwidth_mbps')
    
    db.close()
    print("\n✓ Done! Close the chart windows when finished.")

if __name__ == '__main__':
    main()
