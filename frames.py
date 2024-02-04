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

def record():
    while True:
        # Take a screenshot using PyAutoGUI
        screenshot = pyautogui.screenshot()

        # Convert the PIL Image to a numpy array
        screenshot_np = np.array(screenshot)

        # Convert RGB to BGR
        screenshot_np = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

        # Save the frame as an image file
        print("📸 Say cheese! Saving frame.")

        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        path = f"{frames_dir}/screenshot_{timestamp}.jpg"
        cv2.imwrite(path, screenshot_np)

        # Wait for 2 seconds
        time.sleep(2)


if __name__ == "__main__":
    record()
