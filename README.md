# Coach

I procrastinate a lot. So I procrastinated by making a thing that helps me stop procrastinating!

![demo1](./readme_images/example1.png)
![demo2](./readme_images/example2.png)

## How does it work?

### First, give coach your goal.

> python coach.py --goal "work on a coding project"

### Take screenshots every 2s




## zeke
- im charlie. i work at replicate. it's an api for running models.
- one of the cool models is llava. llava is like an open source alt to gpt vision. what can I do with llava? 🤔
- well, im a procrastinator. so i procrastinated by making a thing that helps me stop procrastinating.
- SCREENSHOT! of my productivity coach yelling at me
- how does this work?
    - stage 0: define a goal
    - stage 1: takes screenshots every 2s
    - stage 2: run a llava script that asks llava what it sees! (it also works locally)
    - stage 3: ask macos what app is focused
    - stage 4: track activities in a json file
    - stage 5: use a language model to judge whether current activity is productive
    - stage 6: live demo. including hard mode.

## todo
- make a better llava example. fridge example.
- for each step until final demo, screenshot or link to prediction?
- add a list of the models that I'm using: llava, llama with function calling

## How it works

Coach watches what you do on your computer and yells at you if you're not being productive. It also records everything you do and gives you a handy dashboard for tracking your time.

By default, Coach runs in the cloud on Replicate, but can run locally via Ollama. That means your data never leaves your computer.

Coach takes picture of your screen every 2 seconds. Coach then runs [llava 1.6](https://replicate.com/yorickvp/llava-v1.6-34b) to analyze what it sees. For example:








Record screen and run llava locally to analyze it:

```
python coach.py --record
```

Same as above, but add a goal. If you stop working on the goal, the coach annoys you:

```
python coach.py --record --goal
```
