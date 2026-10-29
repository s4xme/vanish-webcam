# Palm Vanish

Make yourself disappear from your webcam with a hand gesture. Hold up an open palm or bring both hands together in a **Namaste/prayer pose** and Palm Vanish smoothly fades you into the empty background. Repeat either gesture to reappear.

The camera feed is processed on your computer. The app does not record or upload video.

## Features

- Open-palm and Namaste/prayer-pose gesture controls
- A half-second hold with an on-screen progress ring
- Smooth fade animation for disappearing and reappearing
- Background recapture with the **B** key
- Simple Python API and command-line launcher

## Requirements

- Windows 10 or 11
- Python 3.10, 3.11, or 3.12
- A webcam

## Install from GitHub

Until the first PyPI release is available, install the package from this repository:

```powershell
git clone https://github.com/s4xme/vanish-webcam.git
cd vanish-webcam
py -m pip install .
```

## Use it in Python

```python
from palm_vanish import start

start()
```

`start()` opens the webcam window and runs until you press **Q** or **Esc**. You can choose a camera and resolution with `start(camera=1, width=1280, height=720)`.

After the package is published on PyPI, install it with:

```powershell
py -m pip install palm-vanish
```

The distribution name is `palm-vanish`; the Python import name is `palm_vanish`.

## Run the app

After installing from the repository, start the command-line app with:

```powershell
palm-vanish
```

Or double-click `Run Palm Vanish.bat`. To select a different camera, run `palm-vanish --camera 1`.

Step out of view for four seconds when the app starts so it can capture the empty background. Then return to frame and hold either:

- **Open palm:** raise one hand toward the camera with your fingers extended.
- **Namaste/prayer pose:** hold both hands upright together, palms touching and fingers pointing up.

Keep the gesture visible for at least half a second. Lower your hand or separate your hands before repeating the gesture to switch back.

## Controls

- **Q** or **Esc**: quit
- **B**: capture the background again; step out of view while it captures

## How it works

OpenCV reads and displays the webcam video. MediaPipe Hands recognizes the gestures. When a gesture is held long enough, Palm Vanish cross-fades the live frame with a background captured at startup.

The effect works best with a stationary camera and steady lighting. It replaces the full image with the captured background; movement in the room or camera can make the effect visible.

## License

This repository does not have a license file yet. A license must be added to clearly grant permission for others to reuse or redistribute the code.
