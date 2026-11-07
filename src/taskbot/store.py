"""Persistência das tarefas num ficheiro JSON.

Formato do ficheiro:
    {"next_id": 3, "tasks": [{"id": 1, "text": "...", "done": false}]}

`next_id` só aumenta, por isso os ids nunca são reutilizados, mesmo depois de um `remove`.
"""

import json
import os
from pathlib import Path
from typing import Any

from taskbot.models import Task

ENV_VAR = "TASKBOT_FILE"
DEFAULT_FILENAME = ".taskbot.json"


class StoreError(Exception):
    """O ficheiro de tarefas existe mas não é legível como esperado."""


class TaskNotFound(Exception):
    """Não existe nenhuma tarefa com o id pedido."""

    def __init__(self, task_id: int) -> None:
        super().__init__(f"Tarefa {task_id} não existe")
        self.task_id = task_id


def default_path() -> Path:
    """Devolve o caminho do ficheiro: `TASKBOT_FILE` se definida, senão `~/.taskbot.json`.

    É lida em cada chamada (não na importação) para poder ser controlada nos testes.
    """
    env = os.environ.get(ENV_VAR)
    if env:
        return Path(env).expanduser()
    return Path.home() / DEFAULT_FILENAME


class TaskStore:
    """Repositório de tarefas sobre um ficheiro JSON cujo caminho é injetado."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    # --- leitura / escrita -------------------------------------------------

    def _load(self) -> tuple[int, list[Task]]:
        if not self.path.exists():
            return 1, []
        try:
            raw: Any = json.loads(self.path.read_text(encoding="utf-8"))
            tasks = [Task.from_dict(item) for item in raw["tasks"]]
            next_id = int(raw["next_id"])
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise StoreError(
                f"Ficheiro de tarefas inválido: {self.path} ({exc})"
            ) from exc
        except (KeyError, TypeError, ValueError) as exc:
            raise StoreError(
                f"Ficheiro de tarefas com estrutura inesperada: {self.path}"
            ) from exc
        # Defesa: o contador nunca pode ficar abaixo de um id já usado.
        next_id = max([next_id, *(t.id + 1 for t in tasks)])
        return next_id, tasks

    def _save(self, next_id: int, tasks: list[Task]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"next_id": next_id, "tasks": [t.to_dict() for t in tasks]}
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        os.replace(tmp, self.path)  # escrita atómica

    # --- operações ---------------------------------------------------------

    def add(self, text: str) -> Task:
        """Cria uma tarefa com o próximo id e grava-a."""
        next_id, tasks = self._load()
        task = Task(id=next_id, text=text)
        tasks.append(task)
        self._save(next_id + 1, tasks)
        return task

    def list_tasks(self) -> list[Task]:
        """Devolve todas as tarefas ordenadas por id."""
        _, tasks = self._load()
        return sorted(tasks, key=lambda t: t.id)

    def done(self, task_id: int) -> Task:
        """Marca a tarefa como concluída (idempotente)."""
        next_id, tasks = self._load()
        task = self._find(tasks, task_id)
        task.done = True
        self._save(next_id, tasks)
        return task

    def remove(self, task_id: int) -> Task:
        """Remove a tarefa; o contador de ids não é alterado."""
        next_id, tasks = self._load()
        task = self._find(tasks, task_id)
        tasks.remove(task)
        self._save(next_id, tasks)
        return task

    @staticmethod
    def _find(tasks: list[Task], task_id: int) -> Task:
        for task in tasks:
            if task.id == task_id:
                return task
        raise TaskNotFound(task_id)
