from importlib import resources
from rich import print
from orm_study.quiz.constants import CHAPTER, MULTIPLE, SUBJECTIVE


def get_chapter(chapter_number: str, _type="1") -> str | tuple[str, str]:
    chapter_name = CHAPTER.get(chapter_number)
    quiz_path = f"orm_study.quiz.python.{chapter_name}"
    if _type == "1":
        return _get_multiple(quiz_path)
    elif _type == "3":
        multiple = _get_multiple(quiz_path)
        try:
            subjective = _get_subjective(quiz_path)
            return multiple + subjective
        except FileNotFoundError:
            print("[red bold]주관식 문제가 없습니다. \n객관식 문제만 출제합니다.ㅠㅠ")
            return multiple
    else:
        try:
            return _get_subjective(quiz_path)
        except FileNotFoundError:
            print("[red bold]객관식 문제가 없습니다. \n주관식 문제만 출제합니다.ㅠㅠ")
            return _get_multiple(quiz_path)


def _get_multiple(quiz_path: str) -> str:
    with resources.path(quiz_path, MULTIPLE) as quiz_path:
        with open(quiz_path, "r", encoding="utf-8") as multiple_file:
            return multiple_file.read()


def _get_subjective(quiz_path: str) -> str:
    with resources.path(quiz_path, SUBJECTIVE) as subjective_path:
        with open(subjective_path, "r", encoding="utf-8") as subjective_file:
            return subjective_file.read()


def parse_content(contents: str) -> tuple[list[str], list[str]]:
    quizes = []
    answers = []

    contents = contents.split("---")[:-1]
    for content in contents:
        quiz, answer = content.split("답.")
        quizes.append(quiz.lstrip())
        answers.append(answer.replace("\n", ""))
    return quizes, answers
