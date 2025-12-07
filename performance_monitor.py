#!/usr/bin/env python3
"""
Performance Monitor
Tracks and monitors application performance metrics.
Calculates FPS, latency, and resource usage.
"""

import time
from collections import deque
from typing import Dict, Optional
import threading


class PerformanceMonitor:
    """Monitor application performance metrics."""
    
    def __init__(self, window_size: int = 30):
        """Initialize performance monitor.
        
        Args:
            window_size: Number of frames for rolling average
        """
        self.window_size = window_size
        self.frame_times = deque(maxlen=window_size)
        self.gesture_times = deque(maxlen=window_size)
        self.volume_times = deque(maxlen=window_size)
        self.start_time = time.time()
        self.frame_count = 0
        self.lock = threading.Lock()
        
    def record_frame(self, duration: float) -> None:
        """Record frame processing time.
        
        Args:
            duration: Time taken for frame processing in seconds
        """
        with self.lock:
            self.frame_times.append(duration)
            self.frame_count += 1
    
    def record_gesture(self, duration: float) -> None:
        """Record gesture recognition time.
        
        Args:
            duration: Time taken for gesture recognition in seconds
        """
        with self.lock:
            self.gesture_times.append(duration)
    
    def record_volume_control(self, duration: float) -> None:
        """Record volume control time.
        
        Args:
            duration: Time taken for volume control in seconds
        """
        with self.lock:
            self.volume_times.append(duration)
    
    def get_fps(self) -> float:
        """Get current FPS.
        
        Returns:
            Average FPS over last window_size frames
        """
        with self.lock:
            if not self.frame_times:
                return 0.0
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
    
    def get_avg_frame_time(self) -> float:
        """Get average frame processing time."""
        with self.lock:
            if not self.frame_times:
                return 0.0
            return sum(self.frame_times) / len(self.frame_times)
    
    def get_avg_gesture_time(self) -> float:
        """Get average gesture recognition time."""
        with self.lock:
            if not self.gesture_times:
                return 0.0
            return sum(self.gesture_times) / len(self.gesture_times)
    
    def get_avg_volume_time(self) -> float:
        """Get average volume control time."""
        with self.lock:
            if not self.volume_times:
                return 0.0
            return sum(self.volume_times) / len(self.volume_times)
    
    def get_performance_summary(self) -> Dict[str, float]:
        """Get performance summary."""
        with self.lock:
            return {
                'fps': self.get_fps(),
                'frame_time_ms': self.get_avg_frame_time() * 1000,
                'gesture_time_ms': self.get_avg_gesture_time() * 1000,
                'volume_time_ms': self.get_avg_volume_time() * 1000,
                'total_frames': self.frame_count,
                'uptime_seconds': time.time() - self.start_time
            }
    
    def print_performance_stats(self) -> None:
        """Print performance statistics."""
        stats = self.get_performance_summary()
        print("\n" + "="*50)
        print("Performance Statistics")
        print("="*50)
        print(f"FPS: {stats['fps']:.1f}")
        print(f"Avg Frame Time: {stats['frame_time_ms']:.2f}ms")
        print(f"Avg Gesture Time: {stats['gesture_time_ms']:.2f}ms")
        print(f"Avg Volume Time: {stats['volume_time_ms']:.2f}ms")
        print(f"Total Frames: {stats['total_frames']}")
        print(f"Uptime: {stats['uptime_seconds']:.1f}s")
        print("="*50 + "\n")
