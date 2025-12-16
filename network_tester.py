"""
Network testing module using iperf3 for QoS measurements.
Measures bandwidth, latency, jitter, and packet loss.
"""

import iperf3
import time
from typing import Dict, Optional


class NetworkTester:
    """Handles network performance testing using iperf3."""
    
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
        client = None
        try:
            client = iperf3.Client()
            client.server_hostname = self.server_host
            client.port = self.server_port
            client.duration = duration
            
            if protocol.upper() == 'UDP':
                client.protocol = 'udp'
                client.bandwidth = 100000000  # 100 Mbps for UDP
            else:
                client.protocol = 'tcp'
            
            print(f"Running {protocol} bandwidth test to {self.server_host}:{self.server_port}...")
            result = client.run()
            
            if result is None:
                return {
                    'test_status': 'failed',
                    'error': 'No result received from iperf3. Check if server is running.',
                    'server_host': self.server_host,
                    'server_port': self.server_port,
                    'test_duration': duration
                }
            
            if result.error:
                return {
                    'test_status': 'failed',
                    'error': result.error,
                    'server_host': self.server_host,
                    'server_port': self.server_port,
                    'test_duration': duration
                }
            
            # Extract results
            bandwidth_mbps = result.sent_Mbps if protocol.upper() == 'TCP' else result.Mbps
            
            results = {
                'test_status': 'success',
                'server_host': self.server_host,
                'server_port': self.server_port,
                'test_duration': duration,
                'protocol': protocol,
                'bandwidth_mbps': bandwidth_mbps,
                'bytes_sent': result.sent_bytes,
                'bytes_received': result.received_bytes,
                'jitter_ms': result.jitter_ms if hasattr(result, 'jitter_ms') else None,
                'packet_loss_percent': result.lost_percent if hasattr(result, 'lost_percent') else None
            }
            
            return results
            
        except Exception as e:
            return {
                'test_status': 'error',
                'error': f"{type(e).__name__}: {str(e)}",
                'server_host': self.server_host,
                'server_port': self.server_port,
                'test_duration': duration
            }
        finally:
            # Cleanup to prevent AttributeError on Windows
            if client:
                try:
                    del client
                except:
                    pass
    
    def run_udp_test(self, duration: int = 10) -> Dict:
        """
        Run UDP test to measure jitter and packet loss.
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            Dictionary containing test results including jitter and packet loss
        """
        client = None
        try:
            client = iperf3.Client()
            client.server_hostname = self.server_host
            client.port = self.server_port
            client.duration = duration
            client.protocol = 'udp'
            client.bandwidth = 50000000  # 50 Mbps
            
            print(f"Running UDP test to measure jitter and packet loss...")
            result = client.run()
            
            if result is None:
                return {
                    'test_status': 'failed',
                    'error': 'No result received from iperf3. Check if server is running.',
                    'server_host': self.server_host,
                    'server_port': self.server_port,
                    'test_duration': duration
                }
            
            if result.error:
                return {
                    'test_status': 'failed',
                    'error': result.error,
                    'server_host': self.server_host,
                    'server_port': self.server_port,
                    'test_duration': duration
                }
            
            results = {
                'test_status': 'success',
                'server_host': self.server_host,
                'server_port': self.server_port,
                'test_duration': duration,
                'protocol': 'UDP',
                'bandwidth_mbps': result.Mbps,
                'jitter_ms': result.jitter_ms,
                'packet_loss_percent': result.lost_percent,
                'bytes_sent': result.sent_bytes,
                'bytes_received': result.received_bytes
            }
            
            return results
            
        except Exception as e:
            return {
                'test_status': 'error',
                'error': f"{type(e).__name__}: {str(e)}",
                'server_host': self.server_host,
                'server_port': self.server_port,
                'test_duration': duration
            }
        finally:
            # Cleanup to prevent AttributeError on Windows
            if client:
                try:
                    del client
                except:
                    pass
    
    def run_latency_test(self) -> Dict:
        """
        Estimate latency using a short TCP test.
        Note: This provides an approximate RTT measurement.
        
        Returns:
            Dictionary containing latency results
        """
        client = None
        try:
            client = iperf3.Client()
            client.server_hostname = self.server_host
            client.port = self.server_port
            client.duration = 1
            client.protocol = 'tcp'
            
            print(f"Measuring latency to {self.server_host}:{self.server_port}...")
            
            # Perform quick connection test
            start_time = time.time()
            result = client.run()
            end_time = time.time()
            
            if result is None:
                return {
                    'test_status': 'failed',
                    'error': 'No result received from iperf3.',
                    'latency_ms': None
                }
            
            if result.error:
                return {
                    'test_status': 'failed',
                    'error': result.error,
                    'latency_ms': None
                }
            
            # Estimate RTT based on connection time
            estimated_latency = (end_time - start_time) * 1000 / 2  # Convert to ms and divide by 2
            
            return {
                'test_status': 'success',
                'latency_ms': estimated_latency
            }
            
        except Exception as e:
            return {
                'test_status': 'error',
                'error': f"{type(e).__name__}: {str(e)}",
                'latency_ms': None
            }
        finally:
            # Cleanup to prevent AttributeError on Windows
            if client:
                try:
                    del client
                except:
                    pass
    
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
