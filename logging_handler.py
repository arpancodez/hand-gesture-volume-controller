#!/usr/bin/env python3
"""
Logging Handler
Provides comprehensive logging and debug capabilities.
Supports file logging, console output, and performance tracking.
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
import json


class LoggingHandler:
    """Centralized logging manager."""
    
    LOG_DIR = Path.home() / ".hand_gesture_controller" / "logs"
    
    def __init__(self, debug_mode: bool = False, log_to_file: bool = True):
        """Initialize logging handler.
        
        Args:
            debug_mode: Enable debug logging
            log_to_file: Save logs to file
        """
        self.debug_mode = debug_mode
        self.log_to_file = log_to_file
        self.logger = self._setup_logger()
        self.performance_data = {}
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logger with console and file handlers."""
        logger = logging.getLogger('HandGestureController')
        logger.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        if self.log_to_file:
            self.LOG_DIR.mkdir(parents=True, exist_ok=True)
            log_file = self.LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str, exception: Optional[Exception] = None) -> None:
        """Log error message."""
        if exception:
            self.logger.error(message, exc_info=True)
        else:
            self.logger.error(message)
    
    def log_gesture(self, gesture_type: str, confidence: float) -> None:
        """Log detected gesture."""
        self.info(f"Gesture detected: {gesture_type} (confidence: {confidence:.2f})")
    
    def log_volume_change(self, old_volume: float, new_volume: float) -> None:
        """Log volume changes."""
        if self.debug_mode:
            self.debug(f"Volume changed: {old_volume:.1f}% -> {new_volume:.1f}%")
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "") -> None:
        """Log performance metric."""
        if metric_name not in self.performance_data:
            self.performance_data[metric_name] = []
        self.performance_data[metric_name].append(value)
        
        if self.debug_mode:
            self.debug(f"{metric_name}: {value:.2f}{unit}")
    
    def get_performance_summary(self) -> dict:
        """Get performance summary."""
        summary = {}
        for metric, values in self.performance_data.items():
            if values:
                summary[metric] = {
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'latest': values[-1]
                }
        return summary
    
    def save_session_report(self) -> None:
        """Save session report to file."""
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        report_file = self.LOG_DIR / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'performance': self.get_performance_summary()
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            self.info(f"Session report saved to {report_file}")
        except Exception as e:
            self.error("Failed to save session report", e)
    
    def clear_old_logs(self, days_to_keep: int = 7) -> None:
        """Delete logs older than specified days."""
        from time import time
        cutoff = time() - (days_to_keep * 86400)
        
        for log_file in self.LOG_DIR.glob("*.log"):
            if os.stat(log_file).st_mtime < cutoff:
                try:
                    os.remove(log_file)
                    self.info(f"Deleted old log: {log_file}")
                except Exception as e:
                    self.error(f"Failed to delete log {log_file}", e)
