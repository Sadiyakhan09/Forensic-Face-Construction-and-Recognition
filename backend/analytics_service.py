import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import os

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, data_file: str = None):
        if not data_file:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_file = os.path.join(base_dir, "analytics_data.json")
        self.data_file = data_file
        self.analytics_data = self.load_analytics_data()
        
        # Real-time metrics (in-memory)
        self.search_history = deque(maxlen=1000)  # Keep last 1000 searches
        self.performance_metrics = {
            'total_searches': 0,
            'successful_searches': 0,
            'failed_searches': 0,
            'average_response_time': 0,
            'gender_filter_usage': defaultdict(int),
            'similarity_scores': [],
            'search_times': []
        }
    
    def load_analytics_data(self) -> Dict[str, Any]:
        """Load analytics data from file"""
        try:
            if os.path.exists(self.data_file):
                # Handle empty or partially written files gracefully
                if os.path.getsize(self.data_file) == 0:
                    raise ValueError("Analytics file is empty")
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("Analytics file has invalid structure")
                # Ensure required top-level keys exist
                data.setdefault('daily_stats', {})
                data.setdefault('weekly_stats', {})
                data.setdefault('monthly_stats', {})
                data.setdefault('user_patterns', {})
                data.setdefault('system_performance', {})
                return data
            else:
                return {
                    'daily_stats': {},
                    'weekly_stats': {},
                    'monthly_stats': {},
                    'user_patterns': {},
                    'system_performance': {}
                }
        except Exception as e:
            logger.error(f"Error loading analytics data: {e}")
            return {
                'daily_stats': {},
                'weekly_stats': {},
                'monthly_stats': {},
                'user_patterns': {},
                'system_performance': {}
            }
    
    def _to_json_safe(self, obj: Any) -> Any:
        """Recursively convert objects to JSON-serializable types."""
        try:
            import numpy as np
        except Exception:
            np = None  # type: ignore

        if isinstance(obj, dict):
            return {k: self._to_json_safe(v) for k, v in obj.items()}
        if isinstance(obj, defaultdict):
            return {k: self._to_json_safe(v) for k, v in obj.items()}
        if isinstance(obj, deque):
            return [self._to_json_safe(v) for v in obj]
        if isinstance(obj, list):
            return [self._to_json_safe(v) for v in obj]
        if np is not None and isinstance(obj, (np.integer,)):
            return int(obj)
        if np is not None and isinstance(obj, (np.floating,)):
            return float(obj)
        if np is not None and isinstance(obj, (np.bool_,)):
            return bool(obj)
        return obj

    def save_analytics_data(self):
        """Save analytics data to file"""
        try:
            safe_data = self._to_json_safe(self.analytics_data)
            with open(self.data_file, 'w') as f:
                json.dump(safe_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving analytics data: {e}")
    
    def record_search(self, search_data: Dict[str, Any]):
        """Record a search operation"""
        try:
            timestamp = datetime.now()
            search_record = {
                'timestamp': timestamp.isoformat(),
                'search_id': f"search_{int(time.time())}",
                'gender_filter': search_data.get('gender_filter', 'all'),
                'similarity_scores': search_data.get('similarity_scores', []),
                'response_time': search_data.get('response_time', 0),
                'success': search_data.get('success', True),
                'face_detected': search_data.get('face_detected', True),
                'matches_found': search_data.get('matches_found', 0)
            }
            
            # Add to search history
            self.search_history.append(search_record)
            
            # Update performance metrics
            self.performance_metrics['total_searches'] += 1
            if search_record['success']:
                self.performance_metrics['successful_searches'] += 1
            else:
                self.performance_metrics['failed_searches'] += 1
            
            # Update gender filter usage
            self.performance_metrics['gender_filter_usage'][search_record['gender_filter']] += 1
            
            # Update similarity scores
            if search_record['similarity_scores']:
                self.performance_metrics['similarity_scores'].extend(search_record['similarity_scores'])
                # Keep only last 1000 scores
                if len(self.performance_metrics['similarity_scores']) > 1000:
                    self.performance_metrics['similarity_scores'] = self.performance_metrics['similarity_scores'][-1000:]
            
            # Update response times
            self.performance_metrics['search_times'].append(search_record['response_time'])
            if len(self.performance_metrics['search_times']) > 1000:
                self.performance_metrics['search_times'] = self.performance_metrics['search_times'][-1000:]
            
            # Calculate average response time
            if self.performance_metrics['search_times']:
                self.performance_metrics['average_response_time'] = sum(self.performance_metrics['search_times']) / len(self.performance_metrics['search_times'])
            
            # Update daily stats
            self._update_daily_stats(timestamp, search_record)
            
            # Save data on every search to ensure JSON updates immediately
            self.save_analytics_data()
                
        except Exception as e:
            logger.error(f"Error recording search: {e}")
    
    def _update_daily_stats(self, timestamp: datetime, search_record: Dict[str, Any]):
        """Update daily statistics"""
        try:
            date_key = timestamp.strftime('%Y-%m-%d')
            # Ensure container exists
            if 'daily_stats' not in self.analytics_data or not isinstance(self.analytics_data['daily_stats'], dict):
                self.analytics_data['daily_stats'] = {}

            if date_key not in self.analytics_data['daily_stats']:
                self.analytics_data['daily_stats'][date_key] = {
                    'total_searches': 0,
                    'successful_searches': 0,
                    'failed_searches': 0,
                    'gender_filter_usage': defaultdict(int),
                    'average_similarity': 0,
                    'response_times': []
                }
            
            daily_stats = self.analytics_data['daily_stats'][date_key]
            # Normalize gender_filter_usage to defaultdict(int) if it was loaded as a plain dict
            if not isinstance(daily_stats.get('gender_filter_usage'), defaultdict):
                daily_stats['gender_filter_usage'] = defaultdict(int, daily_stats.get('gender_filter_usage', {}))
            daily_stats['total_searches'] += 1
            
            if search_record['success']:
                daily_stats['successful_searches'] += 1
            else:
                daily_stats['failed_searches'] += 1
            
            daily_stats['gender_filter_usage'][search_record['gender_filter']] += 1
            
            if search_record['similarity_scores']:
                daily_stats['response_times'].append(search_record['response_time'])
                # Calculate average similarity for the day
                all_scores = daily_stats.get('similarity_scores', [])
                all_scores.extend(search_record['similarity_scores'])
                daily_stats['average_similarity'] = sum(all_scores) / len(all_scores) if all_scores else 0
                daily_stats['similarity_scores'] = all_scores[-1000:]  # Keep last 1000
                
        except Exception as e:
            logger.error(f"Error updating daily stats: {e}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for analytics dashboard"""
        try:
            # Calculate recent trends (last 7 days)
            recent_searches = [s for s in self.search_history 
                             if datetime.fromisoformat(s['timestamp']) > datetime.now() - timedelta(days=7)]
            
            # Calculate accuracy metrics
            total_recent = len(recent_searches)
            successful_recent = len([s for s in recent_searches if s['success']])
            accuracy = (successful_recent / total_recent * 100) if total_recent > 0 else 0
            
            # Calculate average similarity
            all_scores = self.performance_metrics['similarity_scores']
            avg_similarity = sum(all_scores) / len(all_scores) if all_scores else 0
            
            # Calculate gender distribution
            gender_distribution = dict(self.performance_metrics['gender_filter_usage'])
            
            # Calculate hourly usage pattern
            hourly_usage = defaultdict(int)
            for search in recent_searches:
                hour = datetime.fromisoformat(search['timestamp']).hour
                hourly_usage[hour] += 1
            
            return {
                'overview': {
                    'total_searches': self.performance_metrics['total_searches'],
                    'successful_searches': self.performance_metrics['successful_searches'],
                    'failed_searches': self.performance_metrics['failed_searches'],
                    'accuracy_percentage': round(accuracy, 2),
                    'average_response_time': round(self.performance_metrics['average_response_time'], 3),
                    'average_similarity': round(avg_similarity, 3)
                },
                'gender_distribution': gender_distribution,
                'hourly_usage': dict(hourly_usage),
                'recent_searches': recent_searches[-10:],  # Last 10 searches
                'similarity_distribution': self._get_similarity_distribution(all_scores),
                'performance_trends': self._get_performance_trends()
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}
    
    def _get_similarity_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Get distribution of similarity scores"""
        if not scores:
            return {}
        
        distribution = {
            'excellent (80-100%)': 0,
            'good (60-79%)': 0,
            'fair (40-59%)': 0,
            'poor (20-39%)': 0,
            'very_poor (0-19%)': 0
        }
        
        for score in scores:
            if score >= 0.8:
                distribution['excellent (80-100%)'] += 1
            elif score >= 0.6:
                distribution['good (60-79%)'] += 1
            elif score >= 0.4:
                distribution['fair (40-59%)'] += 1
            elif score >= 0.2:
                distribution['poor (20-39%)'] += 1
            else:
                distribution['very_poor (0-19%)'] += 1
        
        return distribution
    
    def _get_performance_trends(self) -> Dict[str, List[float]]:
        """Get performance trends over time"""
        try:
            # Get last 7 days of data
            trends = {
                'daily_searches': [],
                'daily_accuracy': [],
                'daily_avg_similarity': []
            }
            
            for i in range(7):
                date = datetime.now() - timedelta(days=i)
                date_key = date.strftime('%Y-%m-%d')
                
                if date_key in self.analytics_data['daily_stats']:
                    daily_stats = self.analytics_data['daily_stats'][date_key]
                    trends['daily_searches'].append(daily_stats['total_searches'])
                    
                    total = daily_stats['total_searches']
                    successful = daily_stats['successful_searches']
                    accuracy = (successful / total * 100) if total > 0 else 0
                    trends['daily_accuracy'].append(accuracy)
                    
                    trends['daily_avg_similarity'].append(daily_stats['average_similarity'])
                else:
                    trends['daily_searches'].append(0)
                    trends['daily_accuracy'].append(0)
                    trends['daily_avg_similarity'].append(0)
            
            # Reverse to get chronological order
            for key in trends:
                trends[key] = trends[key][::-1]
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting performance trends: {e}")
            return {}
    
    def export_analytics(self, format: str = 'json') -> str:
        """Export analytics data"""
        try:
            if format == 'json':
                return json.dumps(self.analytics_data, indent=2)
            elif format == 'csv':
                # Convert to CSV format
                csv_data = "timestamp,search_id,gender_filter,similarity_scores,response_time,success\n"
                for search in self.search_history:
                    csv_data += f"{search['timestamp']},{search['search_id']},{search['gender_filter']},{search['similarity_scores']},{search['response_time']},{search['success']}\n"
                return csv_data
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting analytics: {e}")
            return ""
