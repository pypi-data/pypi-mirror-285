from pathlib import Path

from pydantic import BaseModel
from pypdown import run_step
from pypdown.models import Step


def test_simple_example():
    class StepParams(BaseModel):
        a1_i: Path = "a1.in"
        a2_i: Path = "a2.in"
        a_o: Path = "a.out"
        b_i: Path = "b.in"
        b_o: Path = "b.out"

    def cb_a(a1_i: Path, a2_i: Path, a_o: Path, config: StepParams):
        assert a1_i.exists() and a2_i.exists()
        a_o.touch()
        print(f"Touched {a_o=}")

    def cb_b(a_o: Path, b_i: Path, b_o: Path, config: StepParams):
        assert a_o.exists() and b_i.exists()
        b_o.touch()
        print(f"Touched {b_o=}")

    task_fields = [
        (["a1_i", "a2_i"], ["a_o"], cb_a),
        (["a_o", "b_i"], ["b_o"], cb_b),
    ]

    config = StepParams()

    # Turn the in/output lists into dicts keyed by config field name with filename values
    tasks = [
        {
            "src": config.model_dump(include=inputs),
            "dst": config.model_dump(include=outputs),
            "fn": func,
        }
        for inputs, outputs, func in task_fields
    ]

    step = Step(name="Demo Step", tasks=tasks, config=config)
    run_step(step)
