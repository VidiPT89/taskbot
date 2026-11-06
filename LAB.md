# LAB — Constrói o `taskbot` com um agente de código

**Tempo:** 45-60 min · **Nível:** iniciante · **Aula 1 — trabalho de casa**

Vais construir uma pequena CLI de tarefas (`taskbot add`, `list`, `done`, `rm`) **com a ajuda de um agente de código**, seguindo o fluxo profissional:

```
Explorar → Planear → Implementar → Verificar → Commit
```

Este projeto continua nas aulas 2 a 7 (guard-rails, MCP/RAG, CI, modelos abertos, fine-tuning, segurança). **Guarda-o bem.**

> **Legenda**
> 🟠 = Claude Code · 🟣 = OpenCode (usa só um)
> 💻 = escreve no **terminal** · 💬 = escreve **dentro do agente**
> ✅ = como saber que correu bem · 🆘 = se algo correr mal

---

## Antes de começar

Precisas de: `git`, `python3` (3.10+), `node` (20+), `uv`, e um agente (🟠 Claude Code ou 🟣 OpenCode) já ligado a um modelo.

```bash
git --version && python3 --version && node --version && uv --version
```
✅ Os quatro mostram uma versão.

Faltam coisas? Segue o `passo-a-passo.md` da aula 1 (Parte 0), ou:
- `uv`: `curl -LsSf https://astral.sh/uv/install.sh | sh` (depois reabre o terminal)
- 🟠 `npm install -g @anthropic-ai/claude-code`
- 🟣 `curl -fsSL https://opencode.ai/install | bash` e dentro dele `/connect` + `/models`

Primeira vez com git? `git config --global user.name "O Teu Nome"` e `git config --global user.email "o.teu@email.com"`.

> ⚠️ **Modelo gratuito?** Pode recolher dados. Neste lab não há nada confidencial, mas nunca uses código do trabalho.

---

## Passo 1 — Preparar o projeto (5 min)

### 1.1 Clonar este repo
```bash
git clone https://github.com/professordiogodev/taskbot.git
cd taskbot
git switch -c meu-taskbot
```

### 1.2 Inicializar o projeto Python
```bash
uv init --package --name taskbot
uv add typer
uv add --dev pytest ruff
```

✅ Agora existem `pyproject.toml` e `src/taskbot/`. Confirma:
```bash
ls
ls src/taskbot
```

### 1.3 Primeiro commit
```bash
git add -A
git commit -m "chore: bootstrap"
git status
```
✅ `git status` diz *"nothing to commit, working tree clean"*.

🆘 `uv init` diz que já existe um projeto? Estás na pasta certa? (`pwd` deve acabar em `taskbot`.)

> 💡 **Regra do curso:** começa sempre cada tarefa com o git limpo. Se o agente fizer asneira, `git restore .` repõe tudo.

---

## Passo 2 — Dar contexto ao agente (10 min)

### 2.1 Abrir o agente na pasta do projeto
🟠 💻 `claude` · 🟣 💻 `opencode`

### 2.2 Gerar o rascunho do ficheiro de contexto
💬 `/init`

- 🟠 cria `CLAUDE.md` · 🟣 cria `AGENTS.md`
- Aceita as autorizações que pedir (lê o que pede!).

### 2.3 Cortar o ficheiro para ~25 linhas
Abre-o no editor. O rascunho vem quase sempre comprido de mais. Deixa **só**:

```markdown
# taskbot
CLI de tarefas em Python 3.10+. Gestor de pacotes: uv. CLI com Typer.

## Comandos
- Testes: `uv run pytest -q`
- Lint e formatação: `uv run ruff check . && uv run ruff format .`
- Correr a CLI: `uv run taskbot --help`

## Arquitetura
- `src/taskbot/models.py` — dataclass Task
- `src/taskbot/store.py` — persistência em JSON (variável TASKBOT_FILE)
- `src/taskbot/cli.py` — comandos Typer

## Regras
- Funções públicas com type hints e um teste em `tests/`.
- Não adicionar dependências sem perguntar.
- Nunca alterar testes existentes para os fazer passar.
```

> 🧠 Para cada linha pergunta: *"Se eu apagar isto, o agente erra?"* Se não, apaga.

### 2.4 Confirmar que os comandos são verdadeiros
```bash
uv run ruff check .
uv run pytest -q
```
(`pytest` pode dizer "no tests ran": é normal por agora.)

### 2.5 Guardar
```bash
git add -A
git commit -m "docs: add context file"
```

✅ **Checkpoint 2:** ficheiro de contexto com ≤ 40 linhas e commit feito.

---

## Passo 3 — Planear antes de programar (10 min)

### 3.1 Entrar no plan mode
O agente só **lê e propõe**, não edita.
- 🟠 `Shift + Tab` até aparecer **plan mode**
- 🟣 `Tab` até o agente ativo ser **Plan**

### 3.2 Pedir o plano
💬
```
Quero uma CLI de tarefas chamada taskbot com os comandos:
  add "texto"   → cria tarefa
  list          → lista tarefas (id e estado)
  done <id>     → marca como concluída
  rm <id>       → remove
Persistência num ficheiro JSON (caminho por variável de ambiente TASKBOT_FILE,
default ~/.taskbot.json). Usa Typer.
Faz-me as perguntas que precisares e depois propõe um plano:
ficheiros, funções, testes, riscos. Não escrevas código.
```

### 3.3 Responder às perguntas e ler o plano todo
### 3.4 Acrescentar **uma correção tua**
Por exemplo:
💬
```
Acrescenta ao plano: os ids são incrementais e nunca são reutilizados, mesmo depois de um rm.
O store tem de ser testável sem tocar no ficheiro real do utilizador.
```

✅ **Checkpoint 3:** o plano menciona `TASKBOT_FILE`, testes, e a tua correção.

> 💡 Corrigir um plano demora 20 segundos. Corrigir 200 linhas erradas demora 20 minutos.

---

## Passo 4 — Implementar e verificar, por passos (20 min)

Sai do plan mode (🟠 `Shift+Tab` · 🟣 `Tab` → **Build**). Faz **um passo de cada vez** e um commit por passo.

### 4.1 Modelo e store
💬
```
Implementa models.py e store.py (com testes do store em tests/test_store.py). Corre os testes.
```
Verifica **tu**:
```bash
git diff
uv run pytest -q
uv run ruff check .
```
Perguntas ao ler o `git diff`:
- Os testes testam mesmo o que importa (ids nunca reutilizados, ficheiro inexistente)?
- Algum teste toca no ficheiro real `~/.taskbot.json`? (Não devia.)

```bash
git add -A
git commit -m "feat: task store"
```

### 4.2 CLI
💬
```
Implementa a CLI em cli.py com os comandos add, list, done e rm, e testes com typer.testing.CliRunner. Corre os testes e o ruff.
```
Verifica:
```bash
git diff
uv run pytest -q
uv run ruff check .
git add -A
git commit -m "feat: cli"
```

### 4.3 Experimentar à mão
```bash
export TASKBOT_FILE=/tmp/taskbot-test.json
uv run taskbot add "estudar agentes"
uv run taskbot add "ler o AGENTS.md"
uv run taskbot list
uv run taskbot done 1
uv run taskbot list
uv run taskbot rm 2
uv run taskbot list
```
✅ **Checkpoint 4:** as tarefas aparecem, ficam concluídas e são removidas; testes verdes; ≥ 2 commits novos.

🆘 O comando `taskbot` não existe? 💬 `O entry point taskbot não funciona. Corrige o pyproject.toml e mostra-me o que mudaste.`
🆘 O agente "corrigiu" alterando testes? `git restore .` e repete, acrescentando *"não alteres os testes existentes"*.

---

## Passo 5 — Uma feature com o fluxo completo: prioridades (10 min)

### 5.1 Conversa nova
🟠 `/clear` · 🟣 `/new`  (mudaste de tarefa → conversa nova). Confirma `git status` limpo.

### 5.2 Plan mode e pedido
💬
```
Adiciona o campo priority (low/med/high, default med) às tarefas.
`add` ganha a opção --priority/-p. `list` ordena por prioridade (high primeiro) e mostra-a.
Ficheiros JSON antigos sem priority têm de continuar a funcionar (assumir med).
Escreve primeiro os testes que falham, depois implementa.
Verifica com pytest e ruff.
```

### 5.3 Aprovar o plano, implementar, ler o diff
```bash
git diff
uv run pytest -q
uv run ruff check .
```

### 5.4 O ponto que um pedido vago esqueceria
Existe **um teste para ficheiros JSON antigos** (sem `priority`)? Se não, 💬:
```
Acrescenta um teste para um ficheiro JSON antigo sem o campo priority.
```

```bash
git add -A
git commit -m "feat: task priorities"
```

✅ **Checkpoint 5:** existe teste de retrocompatibilidade e passa.

---

## Passo 6 — Afinar o contexto (5 min)

Houve algum erro que o agente repetiu (comando errado, convenção ignorada)?
1. Acrescenta **uma regra concreta** ao ficheiro de contexto.
2. Remove **uma linha** inútil.
3. Commit:
```bash
git add -A
git commit -m "docs: refine context file"
```

---

## Passo 7 — Publicar no TEU GitHub (5 min)

Vais precisar disto na **aula 3** (CI no GitHub).

```bash
gh auth login          # só se ainda não fizeste
gh repo create taskbot --private --source . --remote meu --push
```
✅ O comando imprime o URL do teu repo.

(Sem `gh`? Cria um repo vazio no site do GitHub e faz `git remote add meu <url>` e `git push -u meu meu-taskbot`.)

---

## ✅ Entregável

- [ ] Ficheiro de contexto (`CLAUDE.md`/`AGENTS.md`) com ≤ 40 linhas
- [ ] ≥ 5 commits em `git log --oneline`
- [ ] `uv run pytest -q` e `uv run ruff check .` a passar
- [ ] Teste de retrocompatibilidade (prioridades)
- [ ] Repo publicado no teu GitHub

---

## 🧗 Desafios extra

1. **Comparação:** repete o Passo 5 **sem plan mode** e com um pedido vago ("adiciona prioridades") numa branch à parte (`git switch -c vago`). Compara os dois diffs: o que ficou de fora?
2. **Permissões:** pré-aprova `pytest` e `git diff` para deixares de ser interrompido (🟠 `/permissions` · 🟣 `opencode.json`).
3. **Contexto:** mede os tokens antes e depois de pedires *"lê todo o projeto"*.
4. **Outro agente:** abre o mesmo repo com o outro agente. Aproveita o ficheiro de contexto?
5. **Comando novo:** `taskbot clear-done` (remove todas as concluídas), com o fluxo completo.

---

## 🆘 Problemas frequentes

| Sintoma | O que fazer |
|---|---|
| `command not found: uv/claude/opencode` | Fecha e reabre o terminal; repete a instalação |
| `git commit` pede nome e email | `git config --global user.name ...` e `user.email ...` |
| `uv run pytest` não encontra o pacote | `uv sync`; confirma `pyproject.toml` |
| O agente ignora o ficheiro de contexto | Abre o agente na raiz do projeto; corta o ficheiro |
| Agente em loop a corrigir o mesmo erro | Conversa nova com o erro exato |
| Diff enorme e confuso | `git restore .` e divide o pedido em passos |
| Modelo gratuito esgotou a quota | Outro modelo (🟣 `/models`) ou espera |
| O agente fez asneira | `git restore .` (e `git clean -fd` para ficheiros novos) · 🟣 `/undo` |

---

## Reflexão final (2 min)

- Que parte do fluxo te poupou mais tempo?
- Onde o agente "inventou" algo que não pedias?
- O que vais mudar no teu ficheiro de contexto?
