#!/usr/bin/env python3
"""
Configuration Manager
Handles application configuration, settings, and preferences.
Supports loading/saving configurations from files.
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from pathlib import Path


@dataclass
class VolumeConfig:
    """Volume control configuration."""
    min_distance: float = 0.02
    max_distance: float = 0.3
    smoothing_window: int = 5
    sensitivity: float = 1.0
    min_change_threshold: float = 2.0


@dataclass
class GestureConfig:
    """Gesture recognition configuration."""
    enabled_gestures: list = field(default_factory=lambda: [
        "pinch", "peace", "thumbs_up", "rock", "pointing", "swipe"
    ])
    confidence_threshold: float = 0.7
    history_length: int = 5
    swipe_threshold: float = 0.1


@dataclass
class DisplayConfig:
    """Display and UI configuration."""
    show_fps: bool = True
    show_volume: bool = True
    show_gesture_info: bool = True
    show_hand_landmarks: bool = True
    font_size: int = 14
    overlay_opacity: float = 0.8
    debug_mode: bool = False


@dataclass
class CameraConfig:
    """Camera configuration."""
    camera_id: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30
    flip_horizontal: bool = True


@dataclass
class ApplicationConfig:
    """Main application configuration."""
    volume: VolumeConfig = field(default_factory=VolumeConfig)
    gesture: GestureConfig = field(default_factory=GestureConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    
    # Feature flags
    enable_multi_gesture: bool = True
    enable_gesture_recording: bool = False
    enable_brightness_control: bool = False
    enable_mute_gesture: bool = True
    enable_statistics: bool = True


class ConfigManager:
    """Manage application configuration."""
    
    DEFAULT_CONFIG_PATH = Path.home() / ".hand_gesture_controller" / "config.json"
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config: ApplicationConfig = ApplicationConfig()
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_dict = json.load(f)
                    self._update_config_from_dict(config_dict)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}. Using defaults.")
    
    def _update_config_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        if 'volume' in config_dict:
            self.config.volume = VolumeConfig(**config_dict['volume'])
        if 'gesture' in config_dict:
            self.config.gesture = GestureConfig(**config_dict['gesture'])
        if 'display' in config_dict:
            self.config.display = DisplayConfig(**config_dict['display'])
        if 'camera' in config_dict:
            self.config.camera = CameraConfig(**config_dict['camera'])
        if 'enable_multi_gesture' in config_dict:
            self.config.enable_multi_gesture = config_dict['enable_multi_gesture']
        if 'enable_gesture_recording' in config_dict:
            self.config.enable_gesture_recording = config_dict['enable_gesture_recording']
        if 'enable_brightness_control' in config_dict:
            self.config.enable_brightness_control = config_dict['enable_brightness_control']
        if 'enable_mute_gesture' in config_dict:
            self.config.enable_mute_gesture = config_dict['enable_mute_gesture']
        if 'enable_statistics' in config_dict:
            self.config.enable_statistics = config_dict['enable_statistics']
    
    def save_config(self) -> None:
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            config_dict = {
                'volume': asdict(self.config.volume),
                'gesture': asdict(self.config.gesture),
                'display': asdict(self.config.display),
                'camera': asdict(self.config.camera),
                'enable_multi_gesture': self.config.enable_multi_gesture,
                'enable_gesture_recording': self.config.enable_gesture_recording,
                'enable_brightness_control': self.config.enable_brightness_control,
                'enable_mute_gesture': self.config.enable_mute_gesture,
                'enable_statistics': self.config.enable_statistics,
            }
            with open(self.config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
        except IOError as e:
            print(f"Error: Could not save config file: {e}")
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self.config = ApplicationConfig()
        self.save_config()
    
    def get_volume_config(self) -> VolumeConfig:
        """Get volume configuration."""
        return self.config.volume
    
    def get_gesture_config(self) -> GestureConfig:
        """Get gesture configuration."""
        return self.config.gesture
    
    def get_display_config(self) -> DisplayConfig:
        """Get display configuration."""
        return self.config.display
    
    def get_camera_config(self) -> CameraConfig:
        """Get camera configuration."""
        return self.config.camera
    
    def update_volume_sensitivity(self, sensitivity: float) -> None:
        """Update volume sensitivity."""
        self.config.volume.sensitivity = max(0.1, min(2.0, sensitivity))
    
    def update_gesture_confidence(self, threshold: float) -> None:
        """Update gesture confidence threshold."""
        self.config.gesture.confidence_threshold = max(0.0, min(1.0, threshold))
    
    def toggle_feature(self, feature_name: str) -> bool:
        """Toggle feature flag.
        
        Args:
            feature_name: Name of feature to toggle
            
        Returns:
            New state of feature
        """
        if hasattr(self.config, feature_name):
            current_state = getattr(self.config, feature_name)
            setattr(self.config, feature_name, not current_state)
            self.save_config()
            return not current_state
        return False
    
    def print_config_summary(self) -> None:
        """Print configuration summary."""
        print("\n" + "="*50)
        print("Configuration Summary")
        print("="*50)
        print(f"Volume Range: {self.config.volume.min_distance} - {self.config.volume.max_distance}")
        print(f"Smoothing Window: {self.config.volume.smoothing_window}")
        print(f"Camera: {self.config.camera.camera_id} ({self.config.camera.width}x{self.config.camera.height})")
        print(f"Debug Mode: {self.config.display.debug_mode}")
        print("="*50 + "\n")
