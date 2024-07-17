import subprocess
from collections.abc import Iterator

from backuper.utils import BaseModelForbidExtra


class ActionError(RuntimeError):
    def __init__(self, return_code: int) -> None:
        self.return_code = return_code


class Action(BaseModelForbidExtra):
    def run(self) -> None:
        raise NotImplementedError


class SubShellAction(Action):
    def collect_command(self) -> Iterator[str]:
        raise NotImplementedError

    def is_failed(self, return_code: int) -> bool:
        raise NotImplementedError

    def run(self) -> None:
        result = subprocess.run(list(self.collect_command()))  # noqa: S603
        if self.is_failed(result.returncode):
            raise ActionError(result.returncode)
