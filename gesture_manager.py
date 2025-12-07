#!/usr/bin/env python3
"""
Advanced Gesture Manager
Provides advanced gesture recognition beyond basic finger counting.
Detects swipe, peace sign, thumbs up, rock gesture, palm open, etc.
"""

import math
import numpy as np
from collections import deque
from enum import Enum


class GestureType(Enum):
    """Enumeration of recognized gestures."""
    PINCH = "pinch"
    OPEN_HAND = "open_hand"
    PEACE = "peace"
    THUMBS_UP = "thumbs_up"
    ROCK = "rock"
    OK_SIGN = "ok_sign"
    PALM = "palm"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    POINT = "point"
    FIST = "fist"
    UNKNOWN = "unknown"


class GestureManager:
    """Manage and recognize advanced hand gestures."""
    
    def __init__(self, history_length=5):
        """Initialize gesture manager.
        
        Args:
            history_length: Number of frames to track for gesture history
        """
        self.history_length = history_length
        self.hand_positions = deque(maxlen=history_length)
        self.gesture_confidence = {}
        self.swipe_threshold = 0.1
        self.min_gesture_frames = 3
        
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points."""
        return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)
    
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points (vertex at point2)."""
        a = self.calculate_distance(point1, point2)
        b = self.calculate_distance(point2, point3)
        c = self.calculate_distance(point1, point3)
        
        if a == 0 or b == 0:
            return 0
        
        cos_angle = (a**2 + b**2 - c**2) / (2 * a * b)
        cos_angle = max(-1, min(1, cos_angle))
        return math.degrees(math.acos(cos_angle))
    
    def is_finger_raised(self, finger_tip, finger_pip):
        """Check if a finger is raised."""
        return finger_tip.y < finger_pip.y
    
    def count_raised_fingers(self, landmarks, handedness):
        """Count number of raised fingers.
        
        Args:
            landmarks: MediaPipe hand landmarks
            handedness: 'Right' or 'Left'
            
        Returns:
            Count of raised fingers (0-5)
        """
        raised = 0
        finger_tips = [4, 8, 12, 16, 20]
        finger_pips = [3, 6, 10, 14, 18]
        
        for i in range(5):
            if self.is_finger_raised(landmarks[finger_tips[i]], landmarks[finger_pips[i]]):
                raised += 1
        
        return raised
    
    def detect_peace_sign(self, landmarks, handedness):
        """Detect peace/victory sign (index and middle fingers up)."""
        is_peace = (
            self.is_finger_raised(landmarks[8], landmarks[6]) and
            self.is_finger_raised(landmarks[12], landmarks[10]) and
            not self.is_finger_raised(landmarks[16], landmarks[14]) and
            not self.is_finger_raised(landmarks[20], landmarks[18])
        )
        return is_peace
    
    def detect_thumbs_up(self, landmarks):
        """Detect thumbs up gesture."""
        thumb_tip = landmarks[4]
        thumb_pip = landmarks[3]
        middle_finger_mcp = landmarks[9]
        
        # Thumb should be pointing up and above other fingers
        is_thumbs_up = (
            thumb_tip.y < thumb_pip.y and
            thumb_tip.y < middle_finger_mcp.y and
            self.calculate_distance(thumb_tip, thumb_pip) > 0.05
        )
        return is_thumbs_up
    
    def detect_rock_gesture(self, landmarks):
        """Detect rock/devil horns gesture (index and pinky up)."""
        is_rock = (
            self.is_finger_raised(landmarks[8], landmarks[6]) and
            self.is_finger_raised(landmarks[20], landmarks[18]) and
            not self.is_finger_raised(landmarks[12], landmarks[10]) and
            not self.is_finger_raised(landmarks[16], landmarks[14])
        )
        return is_rock
    
    def detect_ok_sign(self, landmarks):
        """Detect OK sign (thumb and index finger pinched)."""
        thumb_index_distance = self.calculate_distance(landmarks[4], landmarks[8])
        other_fingers_up = sum([
            self.is_finger_raised(landmarks[12], landmarks[10]),
            self.is_finger_raised(landmarks[16], landmarks[14]),
            self.is_finger_raised(landmarks[20], landmarks[18])
        ]) >= 2
        
        return thumb_index_distance < 0.05 and other_fingers_up
    
    def detect_pointing(self, landmarks):
        """Detect pointing gesture (only index finger extended)."""
        is_pointing = (
            self.is_finger_raised(landmarks[8], landmarks[6]) and
            not self.is_finger_raised(landmarks[12], landmarks[10]) and
            not self.is_finger_raised(landmarks[16], landmarks[14]) and
            not self.is_finger_raised(landmarks[20], landmarks[18])
        )
        return is_pointing
    
    def detect_palm_open(self, landmarks):
        """Detect open palm (all fingers raised)."""
        raised_count = sum([
            self.is_finger_raised(landmarks[8], landmarks[6]),
            self.is_finger_raised(landmarks[12], landmarks[10]),
            self.is_finger_raised(landmarks[16], landmarks[14]),
            self.is_finger_raised(landmarks[20], landmarks[18]),
            landmarks[4].y < landmarks[3].y
        ])
        return raised_count >= 4
    
    def detect_fist(self, landmarks):
        """Detect closed fist (no fingers raised)."""
        raised_count = sum([
            self.is_finger_raised(landmarks[8], landmarks[6]),
            self.is_finger_raised(landmarks[12], landmarks[10]),
            self.is_finger_raised(landmarks[16], landmarks[14]),
            self.is_finger_raised(landmarks[20], landmarks[18])
        ])
        return raised_count == 0
    
    def detect_swipe(self, current_position, history_positions, frame_width):
        """Detect swipe gestures based on hand movement.
        
        Args:
            current_position: Current hand position (x, y)
            history_positions: List of previous positions
            frame_width: Width of video frame
            
        Returns:
            Gesture type if swipe detected, None otherwise
        """
        if len(history_positions) < self.min_gesture_frames:
            return None
        
        # Get oldest position
        oldest_position = history_positions[0]
        displacement_x = current_position[0] - oldest_position[0]
        displacement_y = current_position[1] - oldest_position[1]
        
        # Normalize by frame width
        displacement_x = displacement_x / frame_width
        displacement_y = displacement_y / frame_width
        
        # Detect horizontal swipes
        if abs(displacement_x) > self.swipe_threshold and abs(displacement_x) > abs(displacement_y):
            return GestureType.SWIPE_RIGHT if displacement_x > 0 else GestureType.SWIPE_LEFT
        
        # Detect vertical swipes
        if abs(displacement_y) > self.swipe_threshold and abs(displacement_y) > abs(displacement_x):
            return GestureType.SWIPE_UP if displacement_y < 0 else GestureType.SWIPE_DOWN
        
        return None
    
    def recognize_gesture(self, landmarks, handedness, hand_center, history_positions, frame_width):
        """Recognize gesture from hand landmarks.
        
        Args:
            landmarks: MediaPipe hand landmarks
            handedness: 'Right' or 'Left'
            hand_center: Center position of hand
            history_positions: List of previous hand centers
            frame_width: Video frame width
            
        Returns:
            GestureType: Recognized gesture
        """
        # Check advanced gestures first
        if self.detect_thumbs_up(landmarks):
            return GestureType.THUMBS_UP
        if self.detect_peace_sign(landmarks, handedness):
            return GestureType.PEACE
        if self.detect_rock_gesture(landmarks):
            return GestureType.ROCK
        if self.detect_ok_sign(landmarks):
            return GestureType.OK_SIGN
        if self.detect_pointing(landmarks):
            return GestureType.POINT
        if self.detect_palm_open(landmarks):
            return GestureType.PALM
        if self.detect_fist(landmarks):
            return GestureType.FIST
        
        # Check swipe gestures
        swipe = self.detect_swipe(hand_center, history_positions, frame_width)
        if swipe:
            return swipe
        
        # Check basic pinch/open hand
        thumb_index_dist = self.calculate_distance(landmarks[4], landmarks[8])
        if thumb_index_dist < 0.05:
            return GestureType.PINCH
        elif thumb_index_dist > 0.15:
            return GestureType.OPEN_HAND
        
        return GestureType.UNKNOWN
