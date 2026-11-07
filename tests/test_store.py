import json
from pathlib import Path

import pytest

from taskbot.models import Task
from taskbot.store import StoreError, TaskNotFound, TaskStore, default_path


@pytest.fixture
def path(tmp_path: Path) -> Path:
    return tmp_path / "tasks.json"


@pytest.fixture
def store(path: Path) -> TaskStore:
    return TaskStore(path)


def test_missing_file_is_empty_and_not_created(store: TaskStore, path: Path) -> None:
    assert store.list_tasks() == []
    assert not path.exists()


def test_add_assigns_incremental_ids_and_persists(store: TaskStore, path: Path) -> None:
    assert store.add("a").id == 1
    assert store.add("b").id == 2
    assert store.add("c").id == 3
    reopened = TaskStore(path)
    assert [t.text for t in reopened.list_tasks()] == ["a", "b", "c"]


def test_ids_are_not_reused_after_remove(store: TaskStore) -> None:
    store.add("a")
    store.add("b")
    store.remove(2)
    assert store.add("c").id == 3


def test_ids_are_not_reused_after_removing_everything(store: TaskStore) -> None:
    store.add("a")
    store.add("b")
    store.remove(1)
    store.remove(2)
    assert store.list_tasks() == []
    assert store.add("c").id == 3


def test_done_marks_and_persists(store: TaskStore, path: Path) -> None:
    store.add("a")
    store.done(1)
    assert TaskStore(path).list_tasks() == [Task(id=1, text="a", done=True)]


def test_done_is_idempotent(store: TaskStore) -> None:
    store.add("a")
    store.done(1)
    assert store.done(1).done is True


def test_remove_returns_task_and_deletes_it(store: TaskStore) -> None:
    store.add("a")
    store.add("b")
    removed = store.remove(1)
    assert removed.text == "a"
    assert [t.id for t in store.list_tasks()] == [2]


@pytest.mark.parametrize("op", ["done", "remove"])
def test_unknown_id_raises(store: TaskStore, op: str) -> None:
    store.add("a")
    with pytest.raises(TaskNotFound):
        getattr(store, op)(99)


@pytest.mark.parametrize("content", ["{not json", '{"tasks": "oops"}', "[]"])
def test_corrupt_file_raises_and_is_left_untouched(
    store: TaskStore, path: Path, content: str
) -> None:
    path.write_text(content, encoding="utf-8")
    with pytest.raises(StoreError):
        store.add("x")
    assert path.read_text(encoding="utf-8") == content


def test_non_ascii_text_round_trips(store: TaskStore, path: Path) -> None:
    store.add("ler o capítulo — ação")
    assert TaskStore(path).list_tasks()[0].text == "ler o capítulo — ação"
    assert "capítulo" in path.read_text(encoding="utf-8")


def test_file_format(store: TaskStore, path: Path) -> None:
    store.add("a")
    store.add("b")
    store.remove(2)
    assert json.loads(path.read_text(encoding="utf-8")) == {
        "next_id": 3,
        "tasks": [{"id": 1, "text": "a", "done": False}],
    }


def test_creates_parent_directory(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "dir" / "tasks.json"
    TaskStore(path).add("a")
    assert path.exists()


def test_default_path_uses_env_var(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "custom.json"
    monkeypatch.setenv("TASKBOT_FILE", str(target))
    assert default_path() == target


def test_default_path_falls_back_to_home(isolate_home: Path) -> None:
    assert default_path() == isolate_home / ".taskbot.json"
