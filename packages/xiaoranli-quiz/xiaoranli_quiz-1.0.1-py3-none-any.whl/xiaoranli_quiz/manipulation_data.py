import random
import json
import subprocess
from pathlib import Path

parent_dir = Path(__file__).resolve().parent
file_dir = parent_dir / "data"


def get_quiz_filepath(type):
    """Return the file path for the given quiz type."""
    if type in ["english", "python", "torch"]:
        return file_dir / f"{type}_quiz.json"
    else:
        print(f"Error: Quiz type '{type}' is not supported.")
        return None


def load_quiz_data(type):
    """Load quiz data from a JSON file based on the quiz type."""
    filepath = get_quiz_filepath(type)
    if not filepath:
        return []

    try:
        with open(filepath, "r") as file:
            quizzes = json.load(file)
            random.shuffle(quizzes)
        return quizzes
    except FileNotFoundError:
        print(f"Error in load_quiz_data: The file '{filepath}' was not found.")
        return []


def load_random_quiz_data(type):
    """Load a random quiz question and answer based on the quiz type."""
    filepath = get_quiz_filepath(type)
    if not filepath:
        return None, None

    try:
        with open(filepath, "r") as file:
            data = json.load(file)
            random_shape = tuple(random.randint(1, 10) for _ in range(random.randint(2, 4)))
            question = (
                data["question"]
                .replace("{{SHAPE_LENGTH}}", str(len(random_shape)))
                .replace("{{SHAPE}}", str(random_shape))
            )
            answer = data["answer"].replace("{{SHAPE}}", str(random_shape))
            return question, answer
    except FileNotFoundError:
        print(f"Error in load_random_quiz_data: The file '{filepath}' was not found.")
        return None, None


def copy_and_open_notebook(notebook_type: str) -> None:
    """Copy and open a Jupyter notebook of the given type."""
    copied_file_path = file_dir / f"{notebook_type}_quizz_copy.ipynb"
    try:
        subprocess.run(["cp", str(file_dir / f"{notebook_type}_quizz.ipynb"), str(copied_file_path)], check=True)
        subprocess.run(["jupyter", "notebook", str(copied_file_path)], check=True)
    except KeyboardInterrupt:
        if copied_file_path.exists():
            copied_file_path.unlink()
            print(f"Deleted {copied_file_path}")
        raise
