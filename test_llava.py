from coach import run_llava, get_latest_image
import argparse

if __name__ == "__main__":
    # parse out --cloud arg
    parser = argparse.ArgumentParser(
        description="Process command line arguments for coach.py"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        default=False,
        help="Whether or not to run in the cloud",
    )
    args = parser.parse_args()
    image = get_latest_image()

    image = "./frames/screenshot_2024-02-02_15-41-17.jpg"

    if not args.local:
        print("Running on Replicate")
        model = "yorickvp/llava-v1.6-34b:41ecfbfb261e6c1adf3ad896c9066ca98346996d7c4045c5bc944a79d430f174"
    else:
        print("Running locally")
        model = "ollama/llava:34b-v1.6"

    prompt = "What is going on on this computer screen? Keep it very short and concise, and describe as matter of factly as possible."
    output = run_llava(image, model, prompt)
    print("Image: ", image)
    print(output)
