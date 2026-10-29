# Palm Vanish

A small Windows webcam effect: hold an open palm in view or bring both hands together in the Namaste/prayer pose 🙏🏻, and the app fades you into the empty background. Repeat either gesture to return.

The webcam frames are processed locally. The app does not record or upload video.

## Requirements

- Windows 10 or 11
- Python 3.10 or 3.11
- A webcam

## Install and run

1. Install Python and make sure the Python launcher (`py`) is available.
2. Open PowerShell in this folder.
3. Install the dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

4. Double-click `Run Palm Vanish.bat`, or run:

   ```powershell
   py palm_vanish.py
   ```

5. Step out of view for four seconds while the app captures the background.
6. Return to frame and hold either an open palm toward the camera or both hands upright together in the **Namaste/prayer pose** 🙏🏻 (palms pressed together, fingers pointing up) for at least half a second. The progress ring fills, then the app animates the vanish. Lower your hand or separate your hands, then repeat either gesture to reappear.

## Controls

- **Q** or **Esc**: quit
- **B**: capture the background again (step out of view during capture)

If the default webcam does not open, try another camera index, such as `py palm_vanish.py --camera 1`.

## How it works

OpenCV reads the webcam and displays the result. MediaPipe Hands checks for an open palm or two upright hands close together in the Namaste/prayer pose. After either gesture is held for half a second, the app cross-fades between the live camera frame and a background captured at startup.

For a clean disappearance, keep the camera still and capture the background with nobody in frame. Moving objects, changing light, or camera movement can make the replacement noticeable. The effect replaces the full frame; it does not cut a person out of a moving background.


