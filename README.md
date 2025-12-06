# Hand Gesture Volume Controller

A real-time hand gesture recognition application that allows you to control your system volume using hand gestures captured through a webcam. Built with OpenCV and MediaPipe for robust hand detection and tracking.

## Features

- **Real-time Hand Detection**: Uses MediaPipe for accurate hand pose estimation
- **Volume Control**: Control system volume by:
  - **Pinching**: Moving thumb and index finger closer together for lower volume
  - **Opening hand**: Moving fingers farther apart for higher volume
  - **Finger counting**: Visual feedback showing number of raised fingers
- **Cross-platform Support**: Works on Windows, macOS, and Linux
- **Live FPS Display**: Monitor performance with real-time frame rate display
- **Smooth Volume Changes**: Temporal smoothing to reduce jitter and provide smooth transitions
- **Hand Tracking**: Visualizes hand landmarks and keypoints for debugging

## Installation

### Prerequisites

- Python 3.7 or higher
- Webcam or camera input device

### Step 1: Clone the Repository

```bash
git clone https://github.com/arpancodez/hand-gesture-volume-controller.git
cd hand-gesture-volume-controller
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note for Windows Users**: If you encounter issues with `pycaw`, install the Microsoft Visual C++ Build Tools first.

## Usage

### Basic Usage

```bash
python volume_controller.py
```

A window will appear showing your webcam feed with hand landmarks.

### Controls

- **Volume Control**:
  - Move thumb and index finger **closer** → **Lower volume**
  - Move thumb and index finger **farther** → **Higher volume**
  - **Pinch gesture** (minimum distance) → Minimum volume (0%)
  - **Open hand** (maximum distance) → Maximum volume (100%)

- **Exit**: Press **'q'** to quit the application

## How It Works

### Hand Detection

The application uses **MediaPipe Hands** to detect 21 hand landmarks in real-time:
- 4 landmarks per finger (tip, pip, mcp, cmc)
- Real-time multi-hand support (currently configured for 1 hand)

### Volume Mapping

1. **Distance Calculation**: Euclidean distance between thumb tip and index finger tip is calculated
2. **Smoothing**: Distance values are smoothed over 5 frames to reduce noise
3. **Normalization**: Distance (0.02 to 0.3) is mapped to volume (0-100%)
4. **OS-specific Control**:
   - **macOS**: Uses AppleScript
   - **Windows**: Uses pycaw library
   - **Linux**: Uses ALSA amixer

### Finger Counting

Raises 5 fingers:
- **Thumb**: Checked based on x-coordinate (handedness-aware)
- **Other fingers**: Checked by comparing tip position above pip joint

## File Structure

```
hand-gesture-volume-controller/
├── volume_controller.py    # Main application (282 lines)
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── .gitignore            # Git ignore rules
```

## System Requirements

| OS | Requirement | Notes |
|---|---|---|
| **Windows** | Python 3.7+ | Requires pycaw library for volume control |
| **macOS** | Python 3.7+ | Uses osascript (built-in) |
| **Linux** | Python 3.7+ | Requires ALSA tools (amixer) |

## Example Code Usage

```python
from volume_controller import HandGestureVolumeController

# Create controller instance
controller = HandGestureVolumeController(smoothing_window=5)

# Run with default camera (device 0)
controller.run(camera_id=0)

# Or process individual frames
frame, volume_level = controller.process_frame(frame)
```

## Troubleshooting

### Camera Not Working
- Check if your camera is accessible: `cv2.VideoCapture(0)`
- Try different camera IDs (0, 1, 2, etc.)
- Verify camera permissions

### Volume Not Changing (Windows)
```bash
pip install --upgrade pycaw
```

### Volume Not Changing (Linux)
```bash
sudo apt-get install alsa-utils
```

### Poor Hand Detection
- Ensure good lighting conditions
- Keep hand in front of camera
- Adjust `min_detection_confidence` in `volume_controller.py`

## Performance

- **FPS**: 25-30 FPS on modern hardware (depends on CPU)
- **Latency**: ~50-100ms from gesture to volume change
- **Memory**: ~200-300 MB during execution

## Future Enhancements

- [ ] Screen brightness control
- [ ] Multi-gesture support (brightness, playback control)
- [ ] Gesture recording and playback
- [ ] GUI with settings panel
- [ ] Hand detection confidence display
- [ ] Gesture history and statistics
- [ ] Custom gesture mapping

## License

MIT License - feel free to use this in your projects!

## Author

**Arpan** - [@arpancodez](https://github.com/arpancodez)

## Acknowledgments

- [MediaPipe](https://mediapipe.dev/) - Hand pose detection
- [OpenCV](https://opencv.org/) - Computer vision library
- [pycaw](https://github.com/AndreMiras/pycaw) - Windows audio control

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

**Built with ❤️ for the Python community**
