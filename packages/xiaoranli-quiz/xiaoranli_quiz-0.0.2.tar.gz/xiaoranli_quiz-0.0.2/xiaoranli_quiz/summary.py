from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()


def generate_summary(total_questions, wrong_answers):
    """Generate a summary of the quiz, including wrong answers and correct answers."""
    num_wrong_answers = len(wrong_answers)
    num_correct_answers = total_questions - num_wrong_answers

    # Statistics
    table = Table(show_header=False, show_lines=False, box=None)
    table.add_row(
        Text(f"Total Questions: {total_questions}", style="bold bright_magenta"),
        Text(f"Wrong Answers: {num_wrong_answers}", style="bright_red"),
        Text(f"Correct Answers: {num_correct_answers}", style="bright_green"),
    )

    summary = Text()

    # Detailed Wrong Answers
    if wrong_answers:
        summary.append("You got the following questions wrong:\n", style="bright_yellow")
        for question, user_answer in wrong_answers:
            summary.append(f"- Question: {question}\n", style="bright_cyan")
            summary.append(f"  Your answer: {user_answer}\n", style="bright_red")
    else:
        summary.append("🎉 Great job! You got all questions right.\n", style="bright_green")

    # Displaying the table and summary within a panel
    panel_1 = Panel(table, title="Quiz Summary", border_style="bright_magenta", expand=False)
    panel = Panel(summary, title="Details", border_style="bright_magenta", expand=False)
    console.print(panel_1)
    console.print(panel)
