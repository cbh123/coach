from coach import coach_based_on_image_description

if __name__ == "__main__":
    description = """The computer screen displays a code editor with a file open, showing a Python script."""

    output = coach_based_on_image_description(
        description, "work on a development project", cloud=True
    )

    print(output)
