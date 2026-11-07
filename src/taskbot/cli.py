"""Comandos da CLI do taskbot."""

from collections.abc import Callable
from typing import Annotated

import typer

from taskbot.models import Priority, Task
from taskbot.store import StoreError, TaskNotFound, TaskStore, default_path

app = typer.Typer(no_args_is_help=True, help="Gestor de tarefas simples.")


def _store() -> TaskStore:
    return TaskStore(default_path())


def _fail(message: str) -> typer.Exit:
    typer.echo(message, err=True)
    return typer.Exit(code=1)


def _run[T](action: Callable[[], T]) -> T:
    """Executa uma operação do store e converte erros conhecidos em exit code 1."""
    try:
        return action()
    except TaskNotFound as exc:
        raise _fail(str(exc)) from exc
    except StoreError as exc:
        raise _fail(str(exc)) from exc


def format_task(task: Task) -> str:
    """Formata uma tarefa numa linha: `1 [x] texto` ou `1 [x] (high) texto`.

    A prioridade só é mostrada quando difere de `med`.
    """
    mark = "x" if task.done else " "
    label = "" if task.priority == Priority.MED else f"({task.priority}) "
    return f"{task.id} [{mark}] {label}{task.text}"


@app.command()
def add(
    text: str = typer.Argument(..., help="Texto da tarefa."),
    priority: Annotated[
        Priority,
        typer.Option(
            "--priority", "-p", help="Prioridade da tarefa.", case_sensitive=False
        ),
    ] = Priority.MED,
) -> None:
    """Cria uma tarefa."""
    text = text.strip()
    if not text:
        raise _fail("O texto da tarefa não pode estar vazio.")
    task = _run(lambda: _store().add(text, priority))
    typer.echo(f"Criada tarefa {task.id}: {task.text}")


@app.command("list")
def list_tasks() -> None:
    """Lista as tarefas por prioridade (high primeiro), com id e estado."""
    tasks = _run(lambda: _store().list_tasks())
    if not tasks:
        typer.echo("Sem tarefas.")
        return
    for task in tasks:
        typer.echo(format_task(task))


@app.command()
def done(task_id: int = typer.Argument(..., metavar="ID")) -> None:
    """Marca uma tarefa como concluída."""
    task = _run(lambda: _store().done(task_id))
    typer.echo(f"Concluída tarefa {task.id}: {task.text}")


@app.command()
def rm(task_id: int = typer.Argument(..., metavar="ID")) -> None:
    """Remove uma tarefa."""
    task = _run(lambda: _store().remove(task_id))
    typer.echo(f"Removida tarefa {task.id}: {task.text}")


def main() -> None:
    """Entry point da CLI."""
    app()
