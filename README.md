# ProcrastiCoach

Hi. I'm charlie. I work at replicate. It's an api for running models.

One of the cool models is llava. llava is like an open source alternative to GPT vision. What can you do with llava? 🤔

![llava example](./readme_images/llava2.png)

Well, I procrastinate a lot. So I procrastinated by making a thing that helps me stop procrastinating!

![demo1](./readme_images/example1.png)
![demo2](./readme_images/example2.png)

## How does it work?

### First, give coach your goal.

> python coach.py --goal "work on a coding project"

### Take screenshots every 2s

https://github.com/cbh123/coach/assets/14149230/afb9e7fe-6a8c-49d7-bde0-cc9d3002a461

### Ask Llava what it sees

![llava](./readme_images/llava.png)

### Ask MacOS what song is focused

`osascript -e 'tell application "System Events" to get the name of the first process whose frontmost is true'`

### Track activities in a JSON file

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

### Use a language model to decide whether current activity is productive

![coach1](./readme_images/coach1.png)

![coach2](./readme_images/coach2.png)

Note: it's interesting how this works. It runs on Llama-2 70B with support for jsonschema. So, I provide the coach with a prompt:

```python
f"""You are a productivity coach. You are helping me accomplish my goal of {goal}. Let me know if you think the description of my current activity is in line with my goals.

## Current status
Goal: {goal}
Current activity: {description}

## Your response:"""
```

And a JSON schema:

```json
{
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
```

And then we guarantee that the output is JSON:

```json
{"explanation": "Your current activity does not align with your stated goal of working on a coding project. Watching videos on YouTube is not actively contributing to the development of your coding skills or making progress on a specific project. It may be helpful to close unnecessary tabs and focus on opening the code editor or IDE to start making progress towards your goal.", "productive": false}
```

# See it live!

`python coach.py --goal 'work on a coding project' --cloud`

OR remove cloud flag to run locally on Ollama:

`python coach.py --goal 'work on a coding project'`

Optionally, activate hard mode:
`python coach.py --goal 'work on a coding project' --cloud`

# Future ideas
What happens if you embed the text on your screen and see how far it is from distracting keywords?


# Models
- [Llava 1.6](https://replicate.com/yorickvp/llava-v1.6-mistral-7b)
- [Mixtral](https://replicate.com/mistralai/mixtral-8x7b-instruct-v0.1)
- [BGE embeddings](https://replicate.com/nateraw/bge-large-en-v1.5)
