# ORM STUDY

Python 초보 학습자를 위한 Python 퀴즈 라이브러리입니다. 터미널에서 실행하는 Python 문제은행입니다.

## 설치

```bash
pip install orm-study
```

## 실행

다음과 같은 명령어로 사용합니다

### command

- Option
  - time-check: 문제 푸는 시간 출력 (Optional)
- Argment
  - name: 문제 푸는 사람 이름 입력 (Optional)

```
ost quiz start

ost quiz start --time-check

ost quiz start myname --time-check
```

## 프로젝트 실행

- 가상 환경 생성
- 의존성 설치

```bash
pip install -r requirements-dev.txt
```

- CLI 실행

```bash
python orm_study/main.py quiz start
```

- import 에러가 나는 경우가 있는데 PYTHONPATH가 프로젝트 경로로 설정을 해보세요

```bash
export PYTHONPATH=$PYTHONPATH:/내컴퓨터의경로/orm_study
```
