# taskbot
CLI de tarefas em Python (`requires-python >=3.13`). Gestor de pacotes: uv. CLI com Typer.

## Comandos
- Testes: `uv run pytest -q`
- Lint e formatação: `uv run ruff check . && uv run ruff format .`
- Correr a CLI: `uv run taskbot --help`
- Testar à mão sem tocar em `~/.taskbot.json`: `TASKBOT_FILE=/tmp/taskbot-test.json uv run taskbot list`

## Arquitetura
- `src/taskbot/models.py` — dataclass Task
- `src/taskbot/store.py` — persistência em JSON (variável TASKBOT_FILE, default `~/.taskbot.json`)
- `src/taskbot/cli.py` — comandos Typer

## Regras
- Funções públicas com type hints e um teste em `tests/`.
- Não adicionar dependências sem perguntar.
- Nunca alterar testes existentes para os fazer passar.
- Argumentos e opções do Typer com `Annotated[..., typer.Option(...)]`, como já está em `cli.py` (estilo recomendado pelo Typer).
