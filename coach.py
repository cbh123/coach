import os
import ollama
import base64
import json
import time
import errno
import subprocess
import tkinter as tk
from tkinter import simpledialog
from frames import record
import threading

def send_notification(title, text):
    osascript_command = f'''
    display dialog "{text}" with title "{title}" buttons {{"Logs", "Thanks, Coach! Back to work."}} default button 2
    if the button returned of the result is "Logs" then
        do shell script "open coaching_responses.txt && tail -n +1 coaching_responses.txt"
    end if
    '''
    subprocess.run(['osascript', '-e', osascript_command])



def main(goal):
    while True:
        print("Running...")
        with open('./frames/frame.jpg', 'rb') as file:
            response = ollama.chat(
                model='llava:v1.6',
                messages=[
                {
                    'role': 'user',
                    'content': 'What is going on on this computer screen?',
                    'images': [file.read()],
                },
                ],
            )
        result = response['message']['content']

        print(f"👀 This is what I see: \n{result}\n")

        # Ask mixtral if this is a good idea considering the current goals
        response = ollama.chat(
            model='mixtral',
            messages=[
                {
                    'role': 'system',
                    'content': f"""You are a productivity coach. You are helping my accomplish my goal of {goal}. I'll periodically send you status updates.
                    Let me know if I'm doing a bad job. You must respond in the format: yes/no;;explanation""",
                },
                {
                    'role': 'user',
                    'content': f"""
                    The following describes what I'm doing. Try and choose yes or no, even if you're unsure. Is this a good idea considering my goal of {goal}? You MUST RESPOND in the format: [yes or no];;explanation

                    Description of what user is doing:
                    {result}.
                    """,
                },
            ],
        )
        coaching_response = response['message']['content']
        print(f"💡 This is my advice: {coaching_response}")

        # Append the result to a file, including a timestamp in YYYY-MM-DD HH:MM:SS format
        with open("coaching_responses.txt", "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n llava analysis:{result}\ncoaching response:{coaching_response}\n\n")

        # parse the response, if it's a no, send a notification
        coaching_response = coaching_response.split(";;")
        is_productive = coaching_response[0].strip().lower()
        explanation = coaching_response[1].strip()

        if is_productive == "no":
            send_notification("🛑 PROCRASTINATION ALERT 🛑", explanation)

        time.sleep(3)


if __name__ == "__main__":
    import sys
    if "--record" in sys.argv:
        record_thread = threading.Thread(target=record)
        record_thread.start()

    root = tk.Tk()
    root.withdraw()  # Hide the main window
    goal = simpledialog.askstring("What's your goal?", "Enter your goal:")

    if goal is None:
        print("User cancelled the input dialog.")
    else:
        print(f"User entered: {goal}")
        root.destroy()
        main(goal)
