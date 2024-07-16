from typer import Typer
from orm_study.quiz.command import app as quiz_app


app = Typer(help="ORM Study 문제풀기 CLI APP 입니다.")
app.add_typer(quiz_app, name="quiz")


def main():
    app()


if __name__ == "__main__":
    main()
