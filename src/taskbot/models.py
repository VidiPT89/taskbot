"""Modelo de dados do taskbot."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Self


class Priority(StrEnum):
    """Prioridade de uma tarefa."""

    LOW = "low"
    MED = "med"
    HIGH = "high"

    @property
    def rank(self) -> int:
        """Ordem de listagem: 0 para high (primeiro), 2 para low (último)."""
        return {Priority.HIGH: 0, Priority.MED: 1, Priority.LOW: 2}[self]


@dataclass
class Task:
    """Uma tarefa: identificador, texto, estado e prioridade."""

    id: int
    text: str
    done: bool = False
    priority: Priority = Priority.MED

    def to_dict(self) -> dict[str, Any]:
        """Converte a tarefa num dicionário serializável em JSON.

        `priority` só é incluída quando difere de `med` (o default).
        """
        data: dict[str, Any] = {"id": self.id, "text": self.text, "done": self.done}
        if self.priority != Priority.MED:
            data["priority"] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Cria uma tarefa a partir de um dicionário.

        `done` em falta assume False; `priority` em falta assume `med`.
        Uma prioridade desconhecida levanta ValueError.
        """
        return cls(
            id=int(data["id"]),
            text=str(data["text"]),
            done=bool(data.get("done", False)),
            priority=Priority(data.get("priority", Priority.MED)),
        )
