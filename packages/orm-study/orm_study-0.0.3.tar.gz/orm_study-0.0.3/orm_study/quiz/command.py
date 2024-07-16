import time
import random
import typer
from typing import List, Tuple, Annotated
from typer import Typer
from rich.prompt import Prompt
from rich.panel import Panel
from rich import print
from orm_study.quiz.constants import CHAPTER, CHAPTER_CHOICE, TYPE_CHOICE
from orm_study.quiz.reader import get_chapter, parse_content

app = Typer()


def fetch_quiz(chapter_input: str, type_input: str) -> List[Tuple[str, str]]:
    if type_input == "1":
        quiz_txt = get_chapter(chapter_number=chapter_input)
    elif type_input == "2":
        quiz_txt = get_chapter(chapter_number=chapter_input, _type="2")
    else:
        quiz_txt = get_chapter(chapter_number=chapter_input, _type="3")
    quizes, answers = parse_content(quiz_txt)
    quiz_answer_set = list(zip(quizes, answers))
    random.shuffle(quiz_answer_set)

    return quiz_answer_set


def select_chapter() -> str:
    print(Panel(CHAPTER_CHOICE, title="챕터 선택", title_align="center"))
    chapter_input = Prompt.ask("[white bold]도전할 문제의 챕터를 선택해주세요 ")
    if chapter_input not in CHAPTER:
        print("[red bold]존재하지 않는 챕터입니다.")
        raise typer.Exit()
    return chapter_input


def select_quiz_type() -> str:
    print(Panel(TYPE_CHOICE, title="문제 유형 선택", title_align="center"))
    while True:
        type_input = Prompt.ask("[white bold]도전할 문제의 유형을 선택해주세요 ", choices=["1", "2", "3"])
        if type_input not in ["1", "2", "3"]:
            print("[red bold]존재하지 않는 유형입니다.")
        else:
            break
    return type_input


def select_quiz_num(max_num: int) -> int:
    while True:
        quiz_num = Prompt.ask(f"[white bold]문항 수를 선택해주세요. (최대 {max_num}개)")
        if not quiz_num:
            return max_num
        elif int(quiz_num) > max_num:
            print("[red bold]최대 문항 수를 넘을 수 없습니다.ㅠㅠ")
        else:
            return int(quiz_num)


def solve_quiz(quiz_answer_set: List[Tuple[str, str]]) -> List[bool]:
    user_answers = []
    for i, (quiz, answer) in enumerate(quiz_answer_set, start=1):
        print(Panel(f"[blue bold]문제 {i}{quiz}", title_align="center"))
        user_input = Prompt.ask("[white bold] 정답을 입력해주세요")
        user_answers.append(user_input == answer)
        print()
    return user_answers


def display_results(chapter_input: str, user_answers: List[bool]):
    print(f"[green bold]챕터 {chapter_input} 퀴즈 결과")
    print(f"[blue bold]총 {len(user_answers)}문제 중 {user_answers.count(True)}문제를 맞추셨습니다.")


@app.command(help="파이썬 퀴즈를 시작합니다.")
def start(
    time_check: Annotated[bool, typer.Option(help="퀴즈 타이머 추가")] = False,
    name: Annotated[str, typer.Argument(help="이름을 입력해주세요")] = "익명",
):
    print(f"[green bold]안녕하세요, {name}님! 파이썬 퀴즈를 시작합니다.")
    chapter_input = select_chapter()
    type_input = select_quiz_type()
    quiz_answer_set = fetch_quiz(chapter_input, type_input)
    quiz_num = select_quiz_num(len(quiz_answer_set))
    quiz_answer_set = quiz_answer_set[:quiz_num]

    print(f"[green bold]챕터 {chapter_input}: {CHAPTER[chapter_input]}\n")

    start_time = time.time() if time_check else None
    user_answers = solve_quiz(quiz_answer_set)
    end_time = time.time() if time_check else None

    if all([start_time, end_time]):
        print(f"[red bold]소요 시간: {end_time - start_time:.2f}초")
    display_results(chapter_input, user_answers)


if __name__ == "__main__":
    app()
