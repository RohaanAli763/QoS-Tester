"""
Simple web interface for QoS Network Tester
A lightweight Flask application to access the network testing tool via web browser.
"""

from flask import Flask, render_template, request, jsonify, g
from network_tester_subprocess import NetworkTester
from database import DatabaseManager
import json

app = Flask(__name__)


def get_db():
    """Get a database connection for the current request thread."""
    if 'db' not in g:
        g.db = DatabaseManager()
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Close database connection at the end of request."""
    db = g.pop('db', None)
    if db is not None and hasattr(db, 'close'):
        db.close()


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')


@app.route('/run-test', methods=['POST'])
def run_test():
    """Run a network test."""
    try:
        data = request.get_json()
        server_host = data.get('server_host')
        server_port = int(data.get('server_port', 5201))
        duration = int(data.get('duration', 10))
        
        if not server_host:
            return jsonify({'error': 'Server host is required'}), 400
        
        tester = NetworkTester(server_host, server_port)
        result = tester.run_full_test(duration=duration)
        
        # Save to database if successful
        if result.get('test_status') == 'success':
            db = get_db()
            test_id = db.save_test_result(result)
            result['test_id'] = test_id
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/history')
def get_history():
    """Get test history from database."""
    try:
        db = get_db()
        results = db.get_all_results()
        # Convert to JSON-serializable format
        history = []
        for row in results:
            history.append({
                'id': row[0],
                'timestamp': row[1],
                'server': row[2],
                'port': row[3],
                'bandwidth_mbps': row[4],
                'latency_ms': row[5],
                'jitter_ms': row[6],
                'packet_loss_percent': row[7]
            })
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting QoS Tester Web Interface...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
