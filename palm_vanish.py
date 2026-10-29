"""Hide and reveal yourself with an open-palm gesture."""

from __future__ import annotations

import argparse
import time

import cv2
import mediapipe as mp
import numpy as np


WINDOW = "Palm Vanish"
CAPTURE_SECONDS = 4.0
PALM_HOLD_SECONDS = 0.5
TRANSITION_SECONDS = 0.7


def open_palm(hand_landmarks) -> bool:
    """Return true when the four fingers (not the thumb) are extended."""
    points = hand_landmarks.landmark
    # Tip and PIP landmark indices for index, middle, ring and little fingers.
    return sum(points[tip].y < points[pip].y for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18))) >= 4


def namaste_pose(hands) -> bool:
    """Recognize two upright, extended hands held together in prayer pose."""
    if len(hands) < 2 or not all(open_palm(hand) for hand in hands[:2]):
        return False
    centers = []
    for hand in hands[:2]:
        points = hand.landmark
        centers.append((
            (points[0].x + points[5].x + points[17].x) / 3.0,
            (points[0].y + points[5].y + points[17].y) / 3.0,
        ))
    dx = centers[0][0] - centers[1][0]
    dy = centers[0][1] - centers[1][1]
    return dx * dx + dy * dy < 0.22 * 0.22


def capture_background(camera: cv2.VideoCapture, width: int, height: int) -> np.ndarray:
    print("Step out of view. Capturing the empty background for four seconds...")
    frames: list[np.ndarray] = []
    start = time.monotonic()
    while time.monotonic() - start < CAPTURE_SECONDS:
        ok, frame = camera.read()
        if not ok:
            continue
        frame = cv2.flip(cv2.resize(frame, (width, height)), 1)
        frames.append(frame)
        left = max(0, int(CAPTURE_SECONDS - (time.monotonic() - start)))
        preview = frame.copy()
        cv2.putText(preview, f"Capturing empty background: {left + 1}", (20, 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (60, 230, 255), 2, cv2.LINE_AA)
        cv2.imshow(WINDOW, preview)
        if cv2.waitKey(1) & 0xFF in (27, ord("q")):
            raise KeyboardInterrupt
    if not frames:
        raise RuntimeError("No camera frames received while capturing the background.")
    return np.median(np.stack(frames[-30:]), axis=0).astype(np.uint8)


def run(camera_index: int, width: int, height: int) -> int:
    camera = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW if hasattr(cv2, "CAP_DSHOW") else cv2.CAP_ANY)
    if not camera.isOpened():
        raise RuntimeError(f"Could not open camera {camera_index}. Try --camera 1.")
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
    background = capture_background(camera, width, height)

    hands_api = mp.solutions.hands
    hidden = False
    palm_latched = False
    palm_started: float | None = None
    transition_started: float | None = None
    transition_from_hidden = False
    transition_to_hidden = False
    print("Ready: hold an open palm or Namaste/prayer pose for half a second to vanish.")
    print("Lower your hands, then repeat either gesture to return.")
    print("Press Q or Esc to quit. Press B to recapture the empty background.")
    try:
        with hands_api.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=0,
            min_detection_confidence=0.65,
            min_tracking_confidence=0.6,
        ) as tracker:
            while True:
                ok, frame = camera.read()
                if not ok:
                    print("Camera frame unavailable; retrying...")
                    continue
                frame = cv2.flip(cv2.resize(frame, (width, height)), 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = tracker.process(rgb)
                detected_hands = result.multi_hand_landmarks or []
                palm_now = any(open_palm(hand) for hand in detected_hands)
                gesture_now = palm_now or namaste_pose(detected_hands)

                now = time.monotonic()
                if not gesture_now:
                    palm_latched = False
                    palm_started = None
                elif palm_started is None and not palm_latched:
                    palm_started = now

                if (gesture_now and palm_started is not None and not palm_latched
                        and transition_started is None
                        and now - palm_started >= PALM_HOLD_SECONDS):
                    transition_from_hidden = hidden
                    transition_to_hidden = not hidden
                    transition_started = now
                    palm_latched = True
                    print("Starting vanish animation." if transition_to_hidden else "Starting return animation.")

                if transition_started is not None:
                    progress = min(1.0, (now - transition_started) / TRANSITION_SECONDS)
                    eased = progress * progress * (3.0 - 2.0 * progress)
                    start_frame = background if transition_from_hidden else frame
                    end_frame = background if transition_to_hidden else frame
                    output = cv2.addWeighted(start_frame, 1.0 - eased, end_frame, eased, 0)
                    if progress >= 1.0:
                        hidden = transition_to_hidden
                        transition_started = None
                        print("Vanished." if hidden else "Visible again.")
                else:
                    output = background.copy() if hidden else frame.copy()

                label = ("INVISIBLE - lower hands, then repeat gesture to return" if hidden
                         else "Hold open palm or Namaste pose for 0.5s")
                color = (70, 220, 140) if hidden else (255, 230, 90)
                cv2.putText(output, label, (18, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                            color, 2, cv2.LINE_AA)
                if gesture_now and palm_started is not None and transition_started is None:
                    hold_progress = min(1.0, (now - palm_started) / PALM_HOLD_SECONDS)
                    center = (width - 35, 30)
                    cv2.circle(output, center, 15, (90, 90, 90), 3, cv2.LINE_AA)
                    cv2.ellipse(output, center, (15, 15), -90, 0, int(360 * hold_progress),
                                (50, 230, 150), 3, cv2.LINE_AA)
                cv2.imshow(WINDOW, output)
                key = cv2.waitKey(1) & 0xFF
                if key in (27, ord("q")):
                    break
                if key == ord("b"):
                    hidden = False
                    background = capture_background(camera, width, height)
    finally:
        camera.release()
        cv2.destroyAllWindows()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Vanish from your webcam with an open-palm gesture.")
    parser.add_argument("--camera", type=int, default=0, help="Camera index (default: 0)")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    args = parser.parse_args()
    try:
        return run(args.camera, args.width, args.height)
    except KeyboardInterrupt:
        return 0
    except RuntimeError as error:
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
