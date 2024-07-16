import copy

from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from rich import print as rich_print
from rich.panel import Panel

from RestrictedPython import compile_restricted, safe_builtins
from RestrictedPython.Eval import default_guarded_getitem
from RestrictedPython.Guards import guarded_iter_unpack_sequence, guarded_unpack_sequence


console = Console()


def get_user_answer(number, question):
    question_text = Text(f"Quiz {number}: {question}", style="bright_cyan bold")
    question_panel = Panel(question_text, title=f"Question {number}", border_style="bright_cyan", expand=False)

    # Display the question panel
    console.print(question_panel)

    # Capture the user's answer
    user_answer = Prompt.ask("Your answer", console=console)

    return user_answer


def check_answer(user_answer, correct_answer):
    # Ensure user_answer is a list
    if isinstance(user_answer, str):
        user_answer = [user_answer]

    # Split user_answer and correct_answer by commas and flatten the lists
    user_answer_split = [ans.strip().lower() for item in user_answer for ans in item.split(",")]
    correct_answer_split = [ans.strip().lower() for item in correct_answer for ans in item.split(",")]

    # Compare the sorted versions of the split and processed lists
    return sorted(user_answer_split) == sorted(correct_answer_split)


# Function to compare user answer with the correct answer in a restricted environment
def compare_answers(user_code, correct_code, shared_context):
    try:
        user_context = execute_user_code(user_code, copy.deepcopy(shared_context))
        correct_context = execute_user_code(correct_code, copy.deepcopy(shared_context))
    except Exception as e:
        return False, str(e)

    # Retrieve the variable names from the correct context
    variable_names = set(correct_context.keys()).difference(set(shared_context.keys()))
    if not variable_names:
        variable_names = correct_context.keys()

    for variable_name in variable_names:
        user_value = user_context.get(variable_name)
        correct_value = correct_context.get(variable_name)

        if callable(correct_value):
            if not is_function_equal(user_value, correct_value):
                return False, None
        else:
            if user_value != correct_value:
                return False, None

    return True, None


def is_function_equal(func1, func2):
    if callable(func1) and callable(func2):
        return func1.__code__.co_code == func2.__code__.co_code
    return False


# Function to safely execute user code
def execute_user_code(code, shared_context):
    restricted_globals = {
        "__builtins__": safe_builtins,
        "_getattr_": getattr,
        "_getitem_": default_guarded_getitem,
        "_iter_unpack_sequence_": guarded_iter_unpack_sequence,
        "_unpack_sequence_": guarded_unpack_sequence,
    }

    byte_code = compile_restricted(code, "<string>", "exec")
    exec(byte_code, restricted_globals, shared_context)

    return shared_context


def handle_question(number, question_data, shared_context):
    """Handle asking a question and checking the answer, return details if wrong."""

    def display_result(is_correct, answers=None):
        """Display the result of the question."""
        if is_correct:
            rich_print("[bright_green]Correct🎉🎉🎉[/bright_green]")
        else:
            correct_answers = ", ".join(answers)
            rich_print(f"[bright_red]Wrong❌ The correct answer are: {correct_answers}[/bright_red]")

    user_answer = get_user_answer(number, question_data["question"])
    is_correct = False

    is_correct = check_answer(user_answer, question_data["answer"])

    if is_correct:
        display_result(True)
        return True, None, shared_context
    else:
        display_result(False, question_data["answer"])
        return False, (question_data["question"], user_answer), shared_context
