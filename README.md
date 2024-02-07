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

![recorder](./readme_images/recorder.mp4)

### Ask Llava what it sees

![llava](./readme_images/llava.png)

### Ask MacOS what song is focused

`osascript -e 'tell application "System Events" to get the name of the first process whose frontmost is true'`

### Track activities in a JSON file

![activities](./readme_images/activities.png)

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

# see it live!

`python coach.py --goal 'work on a coding project' --cloud`

OR remove cloud flag to run locally on Ollama:

`python coach.py --goal 'work on a coding project'`

Optionally, activate hard mode:
`python coach.py --goal 'work on a coding project' --cloud`



## todo
- make a better llava example. fridge example.
- for each step until final demo, screenshot or link to prediction?
- add a list of the models that I'm using: llava, llama with function calling
