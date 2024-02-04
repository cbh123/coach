from coach import coach_based_on_image_description

if __name__ == "__main__":
    description = """The computer screen displays a code editor with a file open, showing a Python script. The script includes a traceback error indicating a problem with a file named "coach.py". The user appears to be working on a project related to a chat application, as suggested by the context of the error message."""

    output = coach_based_on_image_description(description, "watch YouTube", cloud=False)

    print(output)
