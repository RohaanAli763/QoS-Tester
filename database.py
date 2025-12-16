"""
Database module for storing network performance test results.
Uses SQLite for data persistence.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional


class DatabaseManager:
    """Manages SQLite database operations for QoS test results."""
    
    def __init__(self, db_name: str = "qos_results.db"):
        """Initialize database connection and create tables if needed."""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                server_host TEXT NOT NULL,
                server_port INTEGER NOT NULL,
                test_duration INTEGER NOT NULL,
                bandwidth_mbps REAL,
                latency_ms REAL,
                jitter_ms REAL,
                packet_loss_percent REAL,
                bytes_sent INTEGER,
                bytes_received INTEGER,
                test_status TEXT
            )
        ''')
        self.conn.commit()
    
    def save_test_result(self, result: Dict) -> int:
        """
        Save a test result to the database.
        
        Args:
            result: Dictionary containing test results
            
        Returns:
            ID of the inserted record
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.cursor.execute('''
            INSERT INTO test_results (
                timestamp, server_host, server_port, test_duration,
                bandwidth_mbps, latency_ms, jitter_ms, packet_loss_percent,
                bytes_sent, bytes_received, test_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            result.get('server_host', 'unknown'),
            result.get('server_port', 5201),
            result.get('test_duration', 10),
            result.get('bandwidth_mbps'),
            result.get('latency_ms'),
            result.get('jitter_ms'),
            result.get('packet_loss_percent'),
            result.get('bytes_sent'),
            result.get('bytes_received'),
            result.get('test_status', 'unknown')
        ))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_results(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Retrieve all test results from the database.
        
        Args:
            limit: Optional limit on number of results to return
            
        Returns:
            List of dictionaries containing test results
        """
        query = 'SELECT * FROM test_results ORDER BY timestamp DESC'
        if limit:
            query += f' LIMIT {limit}'
        
        self.cursor.execute(query)
        columns = [desc[0] for desc in self.cursor.description]
        
        results = []
        for row in self.cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    
    def get_results_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Retrieve test results within a date range.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            
        Returns:
            List of dictionaries containing test results
        """
        self.cursor.execute('''
            SELECT * FROM test_results 
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        ''', (start_date, end_date))
        
        columns = [desc[0] for desc in self.cursor.description]
        results = []
        for row in self.cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    
    def clear_all_results(self):
        """Clear all test results from the database."""
        self.cursor.execute('DELETE FROM test_results')
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
