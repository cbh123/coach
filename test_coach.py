from coach import coach_based_on_image_description
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test the coach function."
    )
    description = """The computer screen displays a code editor with a file open, showing a Python script."""
    parser.add_argument("--image_description", type=str, help="Enter a description of the image.")
    parser.add_argument("--goal", type=str, help="Enter your goal")
    parser.add_argument("--cloud", type=bool, default=True, help="Whether or not to run on cloud")
    args = parser.parse_args()

    output = coach_based_on_image_description(
        args.image_description, args.goal, cloud=True
    )

    print(output)
