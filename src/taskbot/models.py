"""Modelo de dados do taskbot."""

from dataclasses import dataclass
from typing import Any, Self


@dataclass
class Task:
    """Uma tarefa: identificador, texto e estado."""

    id: int
    text: str
    done: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Converte a tarefa num dicionário serializável em JSON."""
        return {"id": self.id, "text": self.text, "done": self.done}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Cria uma tarefa a partir de um dicionário; `done` em falta assume False."""
        return cls(
            id=int(data["id"]),
            text=str(data["text"]),
            done=bool(data.get("done", False)),
        )
