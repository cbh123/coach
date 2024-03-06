# Coach

I work at [Replicate](https://replicate.com/home). It's an API for running models.

One of the cool models is llava. llava is like an open source alternative to GPT vision. What can you do with llava? 🤔

`prompt: what's in this fridge?`
![llava example](./readme_images/llava2.png)

Well, I procrastinate a lot. So I procrastinated by making a thing that helps me stop procrastinating!

![demo1](./readme_images/example1.png)
![Screenshot 2024-02-05 at 9 58 33 AM](https://github.com/cbh123/coach/assets/14149230/3b20c297-0fed-419e-9241-f187413b460a)

# How does it work?

## First, give coach your goal.

> python coach.py --goal "work on a coding project"

## Take screenshots every 2s

https://github.com/cbh123/coach/assets/14149230/afb9e7fe-6a8c-49d7-bde0-cc9d3002a461

## Ask Llava what it sees

![llava](./readme_images/llava.png)

## Ask MacOS what app is focused

`osascript -e 'tell application "System Events" to get the name of the first process whose frontmost is true'`

## Track activities in a JSON file

Each activity is saved in this format:

```python
Activity(
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
)
```

![activities](./readme_images/activities.png)

You can already do interesting things with this data:

![chart](./readme_images/time.png)

## Use a language model to decide whether current activity is productive

```bash
> python test_coach.py \
>       --image_description "The computer screen displays a code editor with a file open, showing a Python script." \
>       --goal "work on a coding project"
>
> productive=True explanation='Based on the information provided, it appears that you have a code editor open and are viewing a Python script, which aligns with your goal of working on a coding project. Therefore, your current activity is considered productive.'
```

```bash
> python test_coach.py \
>       --image_description "The computer screen displays a web browser with YouTube Open" \
>       --goal "work on a coding project"
>
> productive=False explanation='Watching videos on YouTube is not helping you work on your coding project. Try closing the YouTube tab and opening your coding project instead.'
```

How do I guarantee that the output is JSON? Mixtral doesn't support function calling yet, so I just ask it nicely to give me JSON. I then use a library called [instructor](https://jxnl.github.io/instructor/) to retry if the output fails.

```python
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
```

# See it live!

`python coach.py --goal 'work on a coding project' --cloud`

OR remove cloud flag to run locally on Ollama:

`python coach.py --goal 'work on a coding project'`

(note that you will need to first [install ollama](https://ollama.com/) and then run `ollama pull llava:7b-v1.6-mistral-q4_0` to grab the model)

Optionally, activate hard mode:
`python coach.py --goal 'work on a coding project' --cloud`

Demo video:

https://github.com/cbh123/coach/assets/14149230/4fe11e17-f521-411b-960e-e8ed0a98ebc3



# Future ideas
<img width="638" alt="Screenshot 2024-02-12 at 11 20 10 AM" src="https://github.com/cbh123/coach/assets/14149230/9864646f-b4ee-4fb3-b805-9df628acdf22">

What happens if you embed the text on your screen and see how far it is from distracting keywords?

`python ocr.py`

https://github.com/straussmaximilian/ocrmac


# Models
- [Llava 1.6](https://replicate.com/yorickvp/llava-v1.6-mistral-7b)
- [Mixtral](https://replicate.com/mistralai/mixtral-8x7b-instruct-v0.1)
- [BGE embeddings](https://replicate.com/nateraw/bge-large-en-v1.5)
