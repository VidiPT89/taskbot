import pytest

from taskbot.models import Priority, Task


def test_round_trip() -> None:
    task = Task(id=1, text="estudar", done=True)
    assert Task.from_dict(task.to_dict()) == task


def test_from_dict_without_done_defaults_to_false() -> None:
    assert Task.from_dict({"id": 2, "text": "x"}) == Task(id=2, text="x", done=False)


def test_default_priority_is_med() -> None:
    assert Task(1, "a").priority == Priority.MED


def test_from_dict_without_priority_defaults_to_med() -> None:
    task = Task.from_dict({"id": 1, "text": "x", "done": False})
    assert task.priority == Priority.MED


@pytest.mark.parametrize("priority", list(Priority))
def test_round_trip_with_priority(priority: Priority) -> None:
    task = Task(id=1, text="a", priority=priority)
    assert Task.from_dict(task.to_dict()) == task


def test_to_dict_omits_med_priority() -> None:
    assert "priority" not in Task(1, "a").to_dict()


def test_to_dict_includes_non_med_priority() -> None:
    assert Task(1, "a", priority=Priority.HIGH).to_dict()["priority"] == "high"


def test_from_dict_invalid_priority_raises() -> None:
    with pytest.raises(ValueError):
        Task.from_dict({"id": 1, "text": "a", "priority": "urgent"})
