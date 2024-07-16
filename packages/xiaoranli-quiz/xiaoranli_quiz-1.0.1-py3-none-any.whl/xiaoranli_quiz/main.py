from colorama import init
from rich import print as rich_print
import argparse
from typing import List, Dict, Any

from xiaoranli_quiz import generate_summary, handle_question, load_quiz_data, copy_and_open_notebook

init(autoreset=True)


def run_quiz(quiz_type: str, num_quizzes: int = 100) -> None:
    """Run the quiz application."""
    match quiz_type:
        case "english":
            quizzes = load_quiz_data(quiz_type)
            if not quizzes:
                return

            wrong_answers: List[str] = []
            shared_context: Dict[str, Any] = {}
            quiz_counter = 0  # Initialize counter for both primary and follow-up quizzes

            try:
                for i, quiz in enumerate(quizzes[:num_quizzes]):
                    correct, wrong_answer, shared_context = handle_question(i, quiz, shared_context)
                    quiz_counter += 1  # Increment for the primary quiz
                    if not correct and wrong_answer:
                        wrong_answers.append(wrong_answer)
                    if "follow_up" in quiz:
                        print("Follow-up question:")
                        for follow_up in quiz["follow_up"]:
                            _, follow_up_wrong_answer, shared_context = handle_question(i, follow_up, shared_context)
                            quiz_counter += 1  # Increment for the follow-up quiz
                            if follow_up_wrong_answer:
                                wrong_answers.append(follow_up_wrong_answer)
                    if quiz_counter >= num_quizzes:
                        break
                generate_summary(quiz_counter, wrong_answers)
            except KeyboardInterrupt:
                rich_print("[bold bright_magenta]\nQuiz interrupted. Here's your summary so far:[/bold bright_magenta]")
                generate_summary(quiz_counter, wrong_answers)
        case _:
            copy_and_open_notebook(quiz_type)


def main() -> None:
    """Parse command-line arguments and run the quiz."""
    parser = argparse.ArgumentParser(description="Quiz Application")
    parser.add_argument(
        "type",
        nargs="?",
        type=str,
        default="english",
        choices=["english", "python", "torch"],
        help="Type of quiz (default: english)",
    )
    parser.add_argument("num_quizzes", nargs="?", type=int, default=100, help="Number of quizzes (default: 50)")
    args = parser.parse_args()
    run_quiz(args.type, args.num_quizzes)


if __name__ == "__main__":
    main()
