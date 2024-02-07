import ollama
import time
import argparse
import os
from frames import record
from utils import get_active_window_name, send_notification, send_slack_message
import threading
from pydantic import BaseModel
from datetime import datetime
from litellm import completion
import instructor
import replicate
import base64
from instructor.patch import wrap_chatcompletion

completion = wrap_chatcompletion(completion, mode=instructor.Mode.MD_JSON)


class GoalExtract(BaseModel):
    productive: bool
    explanation: str


class Activity(BaseModel):
    datetime: datetime
    application: str
    activity: str
    image_path: str
    model: str
    prompt: str
    goal: str = None
    is_productive: bool = None
    explanation: str = None


def coach_based_on_image_description(description, goal, cloud):
    print("🧠 Coach is thinking...")
    if cloud:
        deployment = replicate.deployments.get("cbh123/coach-llama")
        prediction = deployment.predictions.create(
            input={
                "prompt": f"""You are a productivity coach. You are helping me accomplish my goal of {goal}. Let me know if you think the description of my current activity is in line with my goals.

## Current status
Goal: {goal}
Current activity: {description}

## Your response:""",
                "jsonschema": """{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "productive": {
      "type": "boolean",
      "description": "This should be 'true' if the activity is helping me accomplish my goal, otherwise 'false'"
    },
    "explanation": {
      "type": "string",
      "description": "This should be a helpful description of why I am not productive, only required if productive == false"
    }
  },
  "required": ["productive", "explanation"],
  "additionalProperties": false
}
""",
            }
        )
        prediction.wait()
        result = "".join(prediction.output)
        return GoalExtract.model_validate_json(result)

    else:
        model = "ollama/mixtral"
        messages = [
            {
                "role": "system",
                "content": """You are a JSON extractor. Please extract the following JSON, No Talking at all. Just output JSON based on the description. NO TALKING AT ALL!!""",
            },
            {
                "role": "user",
                "content": f"""You are a productivity coach. You are helping my accomplish my goal of {goal}. Let me know if you think the description of my current activity is in line with my goals.

RULES: You must respond in JSON format. DO NOT RESPOND WITH ANY TALKING.

## Current status:
Goal: {goal}
Current activity: {description}

## Result:""",
            },
        ]

        record = completion(
            model=model,
            response_model=GoalExtract,
            max_retries=5,
            messages=messages,
        )

        return record


def run_llava(image_path, model, prompt):
    if "ollama" in model:
        model = model.split("/")[1]
        print(f"Running Ollama model {model}")
        with open(image_path, "rb") as file:
            response = ollama.chat(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [file.read()],
                    },
                ],
            )
        result = response["message"]["content"]
        return result
    else:
        with open(image_path, "rb") as file:
            image_data = file.read()
            encoded_image = base64.b64encode(image_data).decode("utf-8")
            image_uri = f"data:image/jpeg;base64,{encoded_image}"
            deployment = replicate.deployments.get("cbh123/coach-llava")
            prediction = deployment.predictions.create(
                input={"image": image_uri, "prompt": prompt}
            )
            prediction.wait()
            print(
                f"See prediction status: https://replicate.com/predictions/{prediction.id}"
            )
            output = prediction.output
        return "".join([x for x in output])


def get_latest_image(directory="./frames"):
    """
    Gets the latest image file from the specified directory.

    :param directory: The directory to search for image files.
    :return: The path to the latest image file.
    """
    image_files = os.listdir(directory)
    image_files.sort(
        key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True
    )

    if image_files:
        return os.path.join(directory, image_files[0])
    else:
        return None


def main(goal, hard_mode, cloud):
    print("💪 HARD MODE ACTIVE" if hard_mode else "🐥 Easy mode.")
    print(
        "☁️ Running in the cloud on Replicate ☁️"
        if cloud
        else "💻 Running locally on Ollama 💻"
    )

    while True:
        latest_image = get_latest_image()

        if not latest_image:
            print("No image found. Waiting for 5 seconds.")
            time.sleep(5)
            continue

        llava_model = (
            "ollama/llava:34b-v1.6"
            if not cloud
            else "yorickvp/llava-v1.6-34b:41ecfbfb261e6c1adf3ad896c9066ca98346996d7c4045c5bc944a79d430f174"
        )
        llava_prompt = "What is going on on this computer screen? Keep it very short and concise, and describe as matter of factly as possible."

        result = run_llava(latest_image, llava_model, llava_prompt)

        print(f"👀 This is what I see for {latest_image}: {result}\n")

        # create new Activity object
        activity = Activity(
            activity=result,
            application=get_active_window_name(),
            datetime=datetime.now(),
            image_path=latest_image,
            model=llava_model,
            prompt=llava_prompt,
        )

        if goal:
            # Ask mixtral if this is a good idea considering the current goals
            try:
                coaching_response = coach_based_on_image_description(
                    result, goal, cloud
                )
            except Exception as e:
                print(f"🚨 Error: {e}")
                break

            print(f"💡 This is my advice: {coaching_response}")

            activity.goal = goal
            activity.is_productive = coaching_response.productive
            activity.explanation = coaching_response.explanation

            # Send a notification if the user is not being productive
            if coaching_response.productive == False:
                send_notification(
                    "🛑 PROCRASTINATION ALERT 🛑", coaching_response.explanation
                )

                if hard_mode:
                    send_slack_message(
                        f"🚨 CHARLIE IS PROCRASTINATING! 🚨 \nHe said he wanted to work on: {goal} but I see: {result}, which I've determined is not productive because: \n {coaching_response.explanation}",
                        latest_image,
                    )

        # save the activity to a file
        with open("./logs/activities.jsonl", "a") as f:
            f.write(activity.model_dump_json() + "\n")

        time.sleep(3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process command line arguments for coach.py"
    )
    parser.add_argument("--record", action="store_true", help="Start recording")
    parser.add_argument("--goal", type=str, help="Enter your goal")
    parser.add_argument(
        "--hard", action="store_true", help="Whether or not to go hard mode"
    )
    parser.add_argument(
        "--cloud", action="store_true", help="Whether or not to run in the cloud"
    )

    args = parser.parse_args()

    if args.record:
        record_thread = threading.Thread(target=record)
        record_thread.start()

    goal = args.goal if args.goal else None

    main(goal, args.hard, args.cloud)
