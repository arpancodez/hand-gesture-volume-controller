#!/usr/bin/env python3
"""
Hand Gesture Volume Controller
Real-time hand gesture recognition for system volume control.
Uses OpenCV and MediaPipe for hand detection.

Author: Arpan
License: MIT
"""

import cv2
import mediapipe as mp
import math
import os
import platform
from collections import deque
import numpy as np


class HandGestureVolumeController:
    """Control system volume using hand gestures."""

    def __init__(self, smoothing_window=5):
        """
        Initialize the Hand Gesture Volume Controller.

        Args:
            smoothing_window: Number of frames for smoothing volume changes
        """
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.distance_history = deque(maxlen=smoothing_window)
        self.fingers_history = deque(maxlen=smoothing_window)
        self.os_type = platform.system()
        self.setup_audio_control()

    def setup_audio_control(self):
        """Setup OS-specific audio control methods."""
        if self.os_type == "Darwin":  # macOS
            self.set_volume = self._set_volume_mac
        elif self.os_type == "Windows":
            self.set_volume = self._set_volume_windows
        else:  # Linux
            self.set_volume = self._set_volume_linux

    @staticmethod
    def _set_volume_mac(volume):
        """Set volume on macOS (0-100)."""
        volume = max(0, min(100, volume))
        os.system(f"osascript -e 'set volume output volume {volume}'")

    @staticmethod
    def _set_volume_windows(volume):
        """Set volume on Windows (0-100)."""
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from ctypes import cast, POINTER

            volume = max(0, min(100, volume)) / 100.0
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, None, None
            )
            volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            volume_interface.SetMasterVolumeLevelScalar(volume, None)
        except ImportError:
            print(
                "Warning: Install pycaw for volume control: "
                "pip install pycaw"
            )

    @staticmethod
    def _set_volume_linux(volume):
        """Set volume on Linux (0-100)."""
        volume = max(0, min(100, volume))
        os.system(f"amixer -D pulse sset Master {volume}%")

    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points."""
        return math.sqrt(
            (point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2
        )

    def count_fingers(self, hand_landmarks, handedness):
        """Count raised fingers.

        Args:
            hand_landmarks: MediaPipe hand landmarks
            handedness: 'Right' or 'Left'

        Returns:
            Number of raised fingers (0-5)
        """
        fingers_raised = 0
        fingers_tips = [4, 8, 12, 16, 20]
        fingers_pip = [3, 6, 10, 14, 18]

        # Thumb
        if handedness == "Right":
            if hand_landmarks[fingers_tips[0]].x < hand_landmarks[
                fingers_pip[0]
            ].x:
                fingers_raised += 1
        else:
            if hand_landmarks[fingers_tips[0]].x > hand_landmarks[
                fingers_pip[0]
            ].x:
                fingers_raised += 1

        # Other fingers
        for i in range(1, 5):
            if (
                hand_landmarks[fingers_tips[i]].y
                < hand_landmarks[fingers_pip[i]].y
            ):
                fingers_raised += 1

        return fingers_raised

    def process_frame(self, frame):
        """Process a single frame for hand detection and gesture recognition.

        Args:
            frame: Input video frame

        Returns:
            Processed frame with annotations, volume level
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        volume_level = None
        frame_height, frame_width, _ = frame.shape

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness_info in zip(
                results.multi_hand_landmarks, results.multi_handedness
            ):
                # Draw hand landmarks
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                )

                # Get thumb and index finger positions (for distance)
                thumb_tip = hand_landmarks[4]  # Thumb tip
                index_tip = hand_landmarks[8]  # Index finger tip

                distance = self.calculate_distance(thumb_tip, index_tip)
                self.distance_history.append(distance)
                smoothed_distance = (
                    sum(self.distance_history) / len(self.distance_history)
                )

                # Count fingers
                handedness_label = handedness_info.classification[0].label
                fingers_count = self.count_fingers(
                    hand_landmarks, handedness_label
                )
                self.fingers_history.append(fingers_count)

                # Map distance to volume (0-100)
                # Distance range: 0.02 (pinch) to 0.3 (open hand)
                volume_level = max(
                    0,
                    min(
                        100,
                        (smoothed_distance - 0.02) / (0.3 - 0.02) * 100,
                    ),
                )

                # Draw circle on thumb-index distance
                thumb_pos = (
                    int(thumb_tip.x * frame_width),
                    int(thumb_tip.y * frame_height),
                )
                index_pos = (
                    int(index_tip.x * frame_width),
                    int(index_tip.y * frame_height),
                )

                cv2.line(frame, thumb_pos, index_pos, (0, 255, 0), 2)
                cv2.circle(frame, thumb_pos, 8, (255, 0, 0), -1)
                cv2.circle(frame, index_pos, 8, (0, 255, 0), -1)

                # Display info
                info_text = (
                    f"Volume: {int(volume_level)}% | "
                    f"Fingers: {fingers_count}"
                )
                cv2.putText(
                    frame,
                    info_text,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )

                if volume_level is not None:
                    try:
                        self.set_volume(volume_level)
                    except Exception as e:
                        print(f"Error setting volume: {e}")

        return frame, volume_level

    def run(self, camera_id=0):
        """Run the hand gesture volume controller.

        Args:
            camera_id: Camera device ID (default: 0)
        """
        cap = cv2.VideoCapture(camera_id)

        if not cap.isOpened():
            print("Error: Could not open camera.")
            return

        print("\n" + "=" * 50)
        print("Hand Gesture Volume Controller")
        print("=" * 50)
        print("Controls:")
        print("  - Pinch thumb & index to minimum distance for low volume")
        print("  - Move them farther apart for higher volume")
        print("  - Raise different fingers to see gesture recognition")
        print("  - Press 'q' to quit")
        print("=" * 50 + "\n")

        fps_counter = deque(maxlen=30)
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to read frame.")
                break

            frame = cv2.flip(frame, 1)
            frame, volume_level = self.process_frame(frame)

            # Calculate and display FPS
            frame_count += 1
            if frame_count % 30 == 0:
                fps_counter.append(30)
            fps = sum(fps_counter) / len(fps_counter) if fps_counter else 0

            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (frame.shape[1] - 150, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            cv2.imshow("Hand Gesture Volume Controller", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                print("\nClosing application...")
                break

        cap.release()
        cv2.destroyAllWindows()
        self.hands.close()
        print("Application closed successfully.")


if __name__ == "__main__":
    controller = HandGestureVolumeController()
    controller.run()
