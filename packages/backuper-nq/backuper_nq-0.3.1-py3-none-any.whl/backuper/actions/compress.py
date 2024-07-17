from collections.abc import Iterator
from typing import Annotated, Literal

from pydantic import Field

from backuper.actions.abstract import SubShellAction
from backuper.variables import SubstitutedStr


class CompressAction(SubShellAction):
    type: Literal["compress"]
    source: SubstitutedStr
    archive_name: SubstitutedStr
    archive_type: Literal["7z", "zip", "gzip", "bzip2", "tar"] = "7z"
    volume_size: Annotated[SubstitutedStr | None, Field(pattern=r"\d+[bkmg]")] = None
    password: SubstitutedStr | None = None

    def collect_command(self) -> Iterator[str]:
        yield "7za"
        yield "a"
        yield f"{self.archive_name}.{self.archive_type}"

        if self.archive_type != "7z":
            yield f"-t{self.archive_type}"

        if self.volume_size:
            yield f"-v{self.volume_size}"

        if self.password:
            yield f"-p{self.password}"
            if self.archive_type == "7z":
                yield "-mhe"

        yield self.source

    def is_failed(self, return_code: int) -> bool:
        return return_code != 0
