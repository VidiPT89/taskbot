from taskbot.models import Task


def test_round_trip() -> None:
    task = Task(id=1, text="estudar", done=True)
    assert Task.from_dict(task.to_dict()) == task


def test_from_dict_without_done_defaults_to_false() -> None:
    assert Task.from_dict({"id": 2, "text": "x"}) == Task(id=2, text="x", done=False)
