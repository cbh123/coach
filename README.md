# Coach

Coach watches what you do on your computer and yells at you if you're not being productive. It also records everything you do and gives you a handy dashboard for tracking your time.

By default, Coach runs in the cloud on Replicate, but can run locally via Ollama. That means your data never leaves your computer.

## How it works

Coach takes picture of your screen every 2 seconds. Coach then runs [llava 1.6](https://replicate.com/yorickvp/llava-v1.6-34b) to analyze what it sees. For example:








Record screen and run llava locally to analyze it:

```
python coach.py --record
```

Same as above, but add a goal. If you stop working on the goal, the coach annoys you:

```
python coach.py --record --goal
```
