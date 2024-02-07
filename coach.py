import ollama
import time
import argparse
from recorder import screenshot
from utils import get_active_window_name, send_notification, send_slack_message
from pydantic import BaseModel
from datetime import datetime
from litellm import completion
import instructor
import replicate
import base64
from instructor.patch import wrap_chatcompletion
from halo import Halo

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
    iteration_duration: float = None

def coach_based_on_image_description(description, goal, cloud):
    spinner = Halo(text='🧠 Coach is thinking...', spinner='dots')
    spinner.start()
    if cloud:
        for attempt in range(3):  # Retry up to 3 times
            try:
                output = replicate.run("mistralai/mixtral-8x7b-instruct-v0.1:7b3212fbaf88310cfef07a061ce94224e82efc8403c26fc67e8f6c065de51f21",
                    input={
                        "prompt": f"""You are a productivity coach. You are helping me accomplish my goal of {goal}. Let me know if you think the description of my current activity is in line with my goals. Coding is always productive. Social media isn't.
    ## Rules
    Respond in a JSON format:

    {{"productive": {{
          "type": "boolean",
          "description": "This should be 'true' if the activity is helping me accomplish my goal, otherwise 'false'"
        }},
        "explanation": {{
          "type": "string",
          "description": "This should be a helpful description of why I am not productive, only required if productive == false"
        }}
    }}

    ## Current status
    Goal: {goal}
    Current activity: {description}

    ## Your response:""",
                    }
                )
                result = "".join([o for o in output]).strip()
                clean_result = result.rstrip('}{') + '}'
                record = GoalExtract.model_validate_json(clean_result)
            except ValueError as e:
                print(f"Attempt {attempt + 1}: Failed to validate JSON - {e}")
                if attempt == 2:  # Last attempt
                    raise ValueError("Failed to validate JSON after 3 attempts")
                time.sleep(1)  # Wait a bit before retrying
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
    spinner.stop()
    return record


def run_llava(image_path, model, prompt):
    spinner = Halo(text=f'👀 Running Llava ({model})...', spinner='dots')
    spinner.start()
    if "ollama" in model:
        model = model.split("/")[1]
        print(f"🦙 Running {model}")
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
    else:
        with open(image_path, "rb") as file:
            image_data = file.read()
            encoded_image = base64.b64encode(image_data).decode("utf-8")
            image_uri = f"data:image/jpeg;base64,{encoded_image}"

            deployment = replicate.deployments.get("cbh123/coach-small-llama")
            prediction = deployment.predictions.create(
                input={"image": image_uri, "prompt": prompt}
            )
            prediction.wait()
            output = prediction.output
            # output = replicate.run(model,
            #     input={"image": image_uri, "prompt": prompt}
            # )
        result = "".join([x for x in output])
    spinner.stop()
    return result



def main(goal, hard_mode, cloud):
    print("🎯 Your goal is to ", goal)
    print("💪 HARD MODE ACTIVE" if hard_mode else "🐥 Easy mode.")
    print(
        "☁️ Running in the cloud on Replicate ☁️"
        if cloud
        else "💻 Running locally on Ollama 💻"
    )
    print("")

    while True:
        iteration_start_time = time.time()  # Start timing the iteration

        print("------------------ NEW ITERATION ------------------")

        latest_image = screenshot()

        llava_prompt = "What is going on on this computer screen? Keep it very short and concise, and describe as matter of factly as possible."
        llava_model = (
            "ollama/llava:7b-v1.6-mistral-q4_0"
            if not cloud
            else "yorickvp/llava-v1.6-mistral-7b:19be067b589d0c46689ffa7cc3ff321447a441986a7694c01225973c2eafc874"
        )
        start = time.time()
        llava_output = run_llava(latest_image, llava_model, llava_prompt)
        end = time.time()

        print(f"👀 Ask Llava ({end - start:.2f}s)\noutput: {llava_output} \nsource: {latest_image}\n")

        # create new Activity object
        activity = Activity(
            activity=llava_output,
            application=get_active_window_name(),
            datetime=datetime.now(),
            image_path=latest_image,
            model=llava_model,
            prompt=llava_prompt,
        )

        start = time.time()
        # Ask language model if this is a good idea considering the current goals
        coaching_response = coach_based_on_image_description(
            llava_output, goal, cloud
        )
        end = time.time()

        print(f"🧠 Ask mixtral to decide if this is a good idea ({end - start:.2f}s)\noutput: {coaching_response}")

        activity.goal = goal
        activity.is_productive = coaching_response.productive
        activity.explanation = coaching_response.explanation

        # Send a notification if the user is not being productive
        if coaching_response.productive == False:
            send_notification(
                "🛑 PROCRASTINATIONALERT 🛑", coaching_response.explanation
            )

            if hard_mode:
                send_slack_message(
                    f"🚨 CHARLIE IS PROCRASTINATING! 🚨 \nHe said he wanted to work on: {goal} but I see: {llava_output}, which I've determined is not productive because: \n {coaching_response.explanation}",
                    latest_image,
                )



        # save the activity to a file
        with open("./logs/activities.jsonl", "a") as f:
            f.write(activity.model_dump_json() + "\n")

        iteration_end_time = time.time()  # End timing the iteration
        activity.iteration_duration = iteration_end_time - iteration_start_time
        print(f"\n⏱ Iteration took {activity.iteration_duration:.2f} seconds.\n\n")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process command line arguments for coach.py"
    )
    parser.add_argument("--goal", type=str, help="Enter your goal", required=True)
    parser.add_argument(
        "--hard", action="store_true", help="Whether or not to go hard mode"
    )
    parser.add_argument(
        "--cloud", action="store_true", help="Whether or not to run in the cloud"
    )

    args = parser.parse_args()

    main(args.goal, args.hard, args.cloud)
