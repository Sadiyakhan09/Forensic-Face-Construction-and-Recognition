import time
import psutil
import threading
from typing import Dict, List, Any
import logging
from collections import deque
import json
import os

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Performance thresholds
        self.thresholds = {
            'cpu_usage': 80.0,  # 80%
            'memory_usage': 85.0,  # 85%
            'response_time': 5.0,  # 5 seconds
            'error_rate': 10.0  # 10%
        }
        
        # Current metrics
        self.current_metrics = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'active_connections': 0,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'uptime': 0.0
        }
        
        self.start_time = time.time()
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start the performance monitoring thread"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop the performance monitoring thread"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Performance monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # Update current metrics
                self.current_metrics.update({
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory_percent,
                    'uptime': time.time() - self.start_time,
                    'timestamp': time.time()
                })
                
                # Calculate derived metrics
                if self.current_metrics['total_requests'] > 0:
                    success_rate = (self.current_metrics['successful_requests'] / 
                                  self.current_metrics['total_requests']) * 100
                    error_rate = (self.current_metrics['failed_requests'] / 
                                self.current_metrics['total_requests']) * 100
                    
                    self.current_metrics.update({
                        'success_rate': success_rate,
                        'error_rate': error_rate
                    })
                
                # Store metrics history
                self.metrics_history.append(self.current_metrics.copy())
                
                # Check for alerts
                self._check_alerts()
                
                time.sleep(2)  # Monitor every 2 seconds
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                time.sleep(5)
    
    def _check_alerts(self):
        """Check for performance alerts"""
        alerts = []
        
        if self.current_metrics['cpu_usage'] > self.thresholds['cpu_usage']:
            alerts.append({
                'type': 'cpu_high',
                'message': f"High CPU usage: {self.current_metrics['cpu_usage']:.1f}%",
                'severity': 'warning'
            })
        
        if self.current_metrics['memory_usage'] > self.thresholds['memory_usage']:
            alerts.append({
                'type': 'memory_high',
                'message': f"High memory usage: {self.current_metrics['memory_usage']:.1f}%",
                'severity': 'warning'
            })
        
        if self.current_metrics.get('error_rate', 0) > self.thresholds['error_rate']:
            alerts.append({
                'type': 'error_rate_high',
                'message': f"High error rate: {self.current_metrics.get('error_rate', 0):.1f}%",
                'severity': 'critical'
            })
        
        if self.current_metrics['average_response_time'] > self.thresholds['response_time']:
            alerts.append({
                'type': 'response_time_high',
                'message': f"High response time: {self.current_metrics['average_response_time']:.2f}s",
                'severity': 'warning'
            })
        
        # Store alerts
        if alerts:
            self.current_metrics['alerts'] = alerts
        else:
            self.current_metrics.pop('alerts', None)
    
    def record_request(self, response_time: float, success: bool):
        """Record a request for performance tracking"""
        self.current_metrics['total_requests'] += 1
        
        if success:
            self.current_metrics['successful_requests'] += 1
        else:
            self.current_metrics['failed_requests'] += 1
        
        # Update average response time
        total_requests = self.current_metrics['total_requests']
        current_avg = self.current_metrics['average_response_time']
        new_avg = ((current_avg * (total_requests - 1)) + response_time) / total_requests
        self.current_metrics['average_response_time'] = new_avg
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return self.current_metrics.copy()
    
    def get_metrics_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get performance metrics history"""
        return list(self.metrics_history)[-limit:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a performance summary"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 measurements
        
        # Calculate trends
        cpu_trend = self._calculate_trend([m['cpu_usage'] for m in recent_metrics])
        memory_trend = self._calculate_trend([m['memory_usage'] for m in recent_metrics])
        response_time_trend = self._calculate_trend([m['average_response_time'] for m in recent_metrics])
        
        return {
            'current': self.current_metrics,
            'trends': {
                'cpu_trend': cpu_trend,
                'memory_trend': memory_trend,
                'response_time_trend': response_time_trend
            },
            'health_status': self._get_health_status(),
            'recommendations': self._get_recommendations()
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'stable'
        
        recent_avg = sum(values[-3:]) / min(3, len(values))
        older_avg = sum(values[:-3]) / max(1, len(values) - 3)
        
        if recent_avg > older_avg * 1.1:
            return 'increasing'
        elif recent_avg < older_avg * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def _get_health_status(self) -> str:
        """Get overall health status"""
        alerts = self.current_metrics.get('alerts', [])
        critical_alerts = [a for a in alerts if a['severity'] == 'critical']
        warning_alerts = [a for a in alerts if a['severity'] == 'warning']
        
        if critical_alerts:
            return 'critical'
        elif warning_alerts:
            return 'warning'
        else:
            return 'healthy'
    
    def _get_recommendations(self) -> List[str]:
        """Get performance recommendations"""
        recommendations = []
        
        if self.current_metrics['cpu_usage'] > 70:
            recommendations.append("Consider scaling up CPU resources or optimizing algorithms")
        
        if self.current_metrics['memory_usage'] > 80:
            recommendations.append("Consider increasing memory allocation or optimizing memory usage")
        
        if self.current_metrics['average_response_time'] > 3:
            recommendations.append("Consider optimizing database queries or using caching")
        
        if self.current_metrics.get('error_rate', 0) > 5:
            recommendations.append("Investigate and fix error sources to improve reliability")
        
        if not recommendations:
            recommendations.append("System performance is optimal")
        
        return recommendations
    
    def export_metrics(self, format: str = 'json') -> str:
        """Export performance metrics"""
        if format == 'json':
            return json.dumps({
                'current_metrics': self.current_metrics,
                'metrics_history': list(self.metrics_history),
                'thresholds': self.thresholds
            }, indent=2)
        elif format == 'csv':
            # Convert to CSV format
            if not self.metrics_history:
                return "timestamp,cpu_usage,memory_usage,response_time,success_rate\n"
            
            csv_data = "timestamp,cpu_usage,memory_usage,response_time,success_rate\n"
            for metric in self.metrics_history:
                csv_data += f"{metric['timestamp']},{metric['cpu_usage']},{metric['memory_usage']},{metric['average_response_time']},{metric.get('success_rate', 0)}\n"
            return csv_data
        else:
            raise ValueError(f"Unsupported format: {format}")



