import cv2
import time
from PIL import Image
import numpy as np
import os
import pyautogui

# Folder
folder = "frames"

# Create the frames folder if it doesn't exist
frames_dir = os.path.join(os.getcwd(), folder)
os.makedirs(frames_dir, exist_ok=True)


def screenshot():
    start = time.time()
    # Take a screenshot using PyAutoGUI
    screenshot = pyautogui.screenshot()

    # Convert the screenshot to a numpy array
    frame = np.array(screenshot)

    # Convert RGB to BGR format for OpenCV
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Resize the image
    max_size = 3000
    ratio = max_size / max(frame.shape[1], frame.shape[0])
    new_size = tuple([int(x * ratio) for x in frame.shape[1::-1]])
    resized_img = cv2.resize(frame, new_size, interpolation=cv2.INTER_LANCZOS4)

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    path = f"{frames_dir}/screenshot_{timestamp}.jpg"

    # Save the frame as an image file
    cv2.imwrite(path, resized_img)
    end = time.time()

    print(f"\n📸 Took screenshot ({end - start:.2f}s)")
    return path


def record():
    while True:
        screenshot()
        time.sleep(6)


if __name__ == "__main__":
    record()
