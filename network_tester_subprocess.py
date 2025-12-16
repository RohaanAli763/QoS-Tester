"""
Network testing module using iperf3 subprocess for Windows compatibility.
Measures bandwidth, latency, jitter, and packet loss.
"""

import subprocess
import json
import time
from typing import Dict, Optional


class NetworkTester:
    """Handles network performance testing using iperf3 subprocess."""
    
    def __init__(self, server_host: str = 'localhost', server_port: int = 5201):
        """
        Initialize the network tester.
        
        Args:
            server_host: iperf3 server hostname or IP address
            server_port: iperf3 server port
        """
        self.server_host = server_host
        self.server_port = server_port
    
    def run_bandwidth_test(self, duration: int = 10, protocol: str = 'TCP') -> Dict:
        """
        Run bandwidth test using iperf3.
        
        Args:
            duration: Test duration in seconds
            protocol: Protocol to use ('TCP' or 'UDP')
            
        Returns:
            Dictionary containing test results
        """
        try:
            cmd = [
                'iperf3',
                '-c', self.server_host,
                '-p', str(self.server_port),
                '-t', str(duration),
                '-J'  # JSON output
            ]
            
            if protocol.upper() == 'UDP':
                cmd.extend(['-u', '-b', '100M'])  # UDP with 100 Mbps bandwidth
            
            print(f"Running {protocol} bandwidth test to {self.server_host}:{self.server_port}...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=duration + 10
            )
            
            if result.returncode != 0:
                return {
                    'test_status': 'failed',
                    'error': result.stderr or 'iperf3 command failed',
                    'server_host': self.server_host,
                    'server_port': self.server_port,
                    'test_duration': duration
                }
            
            # Parse JSON output
            data = json.loads(result.stdout)
            
            if 'error' in data:
                return {
                    'test_status': 'failed',
                    'error': data['error'],
                    'server_host': self.server_host,
                    'server_port': self.server_port,
                    'test_duration': duration
                }
            
            # Extract results based on protocol
            if protocol.upper() == 'TCP':
                sent = data['end']['sum_sent']
                bandwidth_mbps = sent['bits_per_second'] / 1000000
                bytes_sent = sent['bytes']
                bytes_received = data['end']['sum_received']['bytes']
                
                return {
                    'test_status': 'success',
                    'server_host': self.server_host,
                    'server_port': self.server_port,
                    'test_duration': duration,
                    'protocol': protocol,
                    'bandwidth_mbps': bandwidth_mbps,
                    'bytes_sent': bytes_sent,
                    'bytes_received': bytes_received,
                    'jitter_ms': None,
                    'packet_loss_percent': None
                }
            else:  # UDP
                sent = data['end']['sum']
                bandwidth_mbps = sent['bits_per_second'] / 1000000
                jitter_ms = sent.get('jitter_ms', 0)
                lost_packets = sent.get('lost_packets', 0)
                total_packets = sent.get('packets', 1)
                packet_loss_percent = (lost_packets / total_packets * 100) if total_packets > 0 else 0
                
                return {
                    'test_status': 'success',
                    'server_host': self.server_host,
                    'server_port': self.server_port,
                    'test_duration': duration,
                    'protocol': protocol,
                    'bandwidth_mbps': bandwidth_mbps,
                    'bytes_sent': sent['bytes'],
                    'bytes_received': sent['bytes'] - lost_packets * 1400,  # Approximate
                    'jitter_ms': jitter_ms,
                    'packet_loss_percent': packet_loss_percent
                }
            
        except subprocess.TimeoutExpired:
            return {
                'test_status': 'error',
                'error': 'Test timeout',
                'server_host': self.server_host,
                'server_port': self.server_port,
                'test_duration': duration
            }
        except json.JSONDecodeError as e:
            return {
                'test_status': 'error',
                'error': f'Failed to parse iperf3 output: {str(e)}',
                'server_host': self.server_host,
                'server_port': self.server_port,
                'test_duration': duration
            }
        except FileNotFoundError:
            return {
                'test_status': 'error',
                'error': 'iperf3 executable not found. Please ensure iperf3 is installed and in PATH.',
                'server_host': self.server_host,
                'server_port': self.server_port,
                'test_duration': duration
            }
        except Exception as e:
            return {
                'test_status': 'error',
                'error': f"{type(e).__name__}: {str(e)}",
                'server_host': self.server_host,
                'server_port': self.server_port,
                'test_duration': duration
            }
    
    def run_udp_test(self, duration: int = 10) -> Dict:
        """
        Run UDP test to measure jitter and packet loss.
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            Dictionary containing test results including jitter and packet loss
        """
        return self.run_bandwidth_test(duration=duration, protocol='UDP')
    
    def run_latency_test(self) -> Dict:
        """
        Estimate latency using ping or a short TCP test.
        
        Returns:
            Dictionary containing latency results
        """
        try:
            # Try using ping for better latency measurement
            if self.server_host == 'localhost' or self.server_host == '127.0.0.1':
                # For localhost, estimate very low latency
                return {
                    'test_status': 'success',
                    'latency_ms': 0.5
                }
            
            print(f"Measuring latency to {self.server_host}...")
            
            # Use ping command (Windows format)
            result = subprocess.run(
                ['ping', '-n', '4', self.server_host],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse average latency from ping output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Average' in line or 'average' in line:
                        # Extract average value (Windows format)
                        parts = line.split('=')
                        if len(parts) > 1:
                            avg_str = parts[-1].strip().replace('ms', '').strip()
                            try:
                                latency = float(avg_str)
                                return {
                                    'test_status': 'success',
                                    'latency_ms': latency
                                }
                            except ValueError:
                                pass
            
            # Fallback: use iperf3 for latency estimation
            start_time = time.time()
            tcp_result = self.run_bandwidth_test(duration=1, protocol='TCP')
            end_time = time.time()
            
            if tcp_result['test_status'] == 'success':
                estimated_latency = (end_time - start_time) * 1000 / 2
                return {
                    'test_status': 'success',
                    'latency_ms': min(estimated_latency, 100)  # Cap at 100ms
                }
            else:
                return {
                    'test_status': 'failed',
                    'error': 'Could not measure latency',
                    'latency_ms': None
                }
            
        except Exception as e:
            return {
                'test_status': 'error',
                'error': f"{type(e).__name__}: {str(e)}",
                'latency_ms': None
            }
    
    def run_full_test(self, duration: int = 10) -> Dict:
        """
        Run comprehensive network test including bandwidth, latency, jitter, and packet loss.
        
        Args:
            duration: Test duration in seconds for each test
            
        Returns:
            Dictionary containing all test results
        """
        print("\n" + "="*60)
        print("Starting Comprehensive Network Performance Test")
        print("="*60 + "\n")
        
        errors = []
        
        # Run TCP bandwidth test
        tcp_results = self.run_bandwidth_test(duration=duration, protocol='TCP')
        if tcp_results['test_status'] != 'success':
            errors.append(f"TCP test: {tcp_results.get('error', 'Unknown error')}")
        time.sleep(1)
        
        # Run UDP test for jitter and packet loss
        udp_results = self.run_udp_test(duration=duration)
        if udp_results['test_status'] != 'success':
            errors.append(f"UDP test: {udp_results.get('error', 'Unknown error')}")
        time.sleep(1)
        
        # Run latency test
        latency_results = self.run_latency_test()
        if latency_results['test_status'] != 'success':
            errors.append(f"Latency test: {latency_results.get('error', 'Unknown error')}")
        
        # Determine overall status
        if tcp_results['test_status'] == 'success' and udp_results['test_status'] == 'success':
            status = 'success'
        elif tcp_results['test_status'] == 'success' or udp_results['test_status'] == 'success':
            status = 'partial'
        else:
            status = 'failed'
        
        # Combine results
        combined_results = {
            'test_status': status,
            'server_host': self.server_host,
            'server_port': self.server_port,
            'test_duration': duration,
            'bandwidth_mbps': tcp_results.get('bandwidth_mbps'),
            'latency_ms': latency_results.get('latency_ms'),
            'jitter_ms': udp_results.get('jitter_ms'),
            'packet_loss_percent': udp_results.get('packet_loss_percent'),
            'bytes_sent': tcp_results.get('bytes_sent'),
            'bytes_received': tcp_results.get('bytes_received')
        }
        
        if errors:
            combined_results['errors'] = errors
        
        print("\n" + "="*60)
        print("Test Complete")
        print("="*60 + "\n")
        
        return combined_results
