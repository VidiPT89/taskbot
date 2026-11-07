from pathlib import Path

import pytest
from typer.testing import CliRunner

from taskbot.cli import app, format_task
from taskbot.models import Task

runner = CliRunner()


@pytest.fixture(autouse=True)
def task_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "t.json"
    monkeypatch.setenv("TASKBOT_FILE", str(path))
    return path


def run(*args: str):
    return runner.invoke(app, list(args))


def test_format_task() -> None:
    assert format_task(Task(1, "a")) == "1 [ ] a"
    assert format_task(Task(2, "b", done=True)) == "2 [x] b"


def test_list_empty() -> None:
    result = run("list")
    assert result.exit_code == 0
    assert result.output.strip() == "Sem tarefas."


def test_add_and_list(task_file: Path) -> None:
    result = run("add", "estudar agentes")
    assert result.exit_code == 0
    assert "Criada tarefa 1" in result.output
    assert task_file.exists()
    assert run("list").output.splitlines() == ["1 [ ] estudar agentes"]


def test_add_empty_text_fails() -> None:
    result = run("add", "   ")
    assert result.exit_code == 1
    assert run("list").output.strip() == "Sem tarefas."


def test_done_marks_task() -> None:
    run("add", "a")
    run("add", "b")
    result = run("done", "1")
    assert result.exit_code == 0
    assert run("list").output.splitlines() == ["1 [x] a", "2 [ ] b"]


def test_rm_removes_task() -> None:
    run("add", "a")
    run("add", "b")
    result = run("rm", "1")
    assert result.exit_code == 0
    assert run("list").output.splitlines() == ["2 [ ] b"]


def test_ids_not_reused_after_rm() -> None:
    run("add", "a")
    run("add", "b")
    run("rm", "2")
    run("add", "c")
    assert run("list").output.splitlines() == ["1 [ ] a", "3 [ ] c"]


@pytest.mark.parametrize("command", ["done", "rm"])
def test_unknown_id_exits_1(command: str) -> None:
    result = run(command, "99")
    assert result.exit_code == 1
    assert "Tarefa 99 não existe" in result.output


@pytest.mark.parametrize("command", ["done", "rm"])
def test_non_integer_id_is_usage_error(command: str) -> None:
    assert run(command, "abc").exit_code == 2


def test_corrupt_file_exits_1_and_is_untouched(task_file: Path) -> None:
    task_file.write_text("{not json", encoding="utf-8")
    result = run("add", "x")
    assert result.exit_code == 1
    assert str(task_file) in result.output
    assert task_file.read_text(encoding="utf-8") == "{not json"


def test_no_args_shows_help() -> None:
    result = run()
    assert "add" in result.output and "list" in result.output
