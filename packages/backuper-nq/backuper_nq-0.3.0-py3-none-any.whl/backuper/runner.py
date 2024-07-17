from collections import OrderedDict
from typing import Annotated

from pydantic import Field, RootModel

from backuper.actions.abstract import ActionError
from backuper.actions.backup import BackupAction
from backuper.actions.compress import CompressAction

AnyAction = Annotated[BackupAction | CompressAction, Field(discriminator="type")]
ActionsModel = RootModel[OrderedDict[str, AnyAction]]


def run_action(action_name: str, action: AnyAction) -> None:
    try:
        action.run()
    except ActionError as e:  # noqa: WPS440
        raise RuntimeError(f"Action '{action_name}' failed with code {e.return_code}")


def run_actions(actions: ActionsModel) -> None:
    for action_name, action in actions.root.items():
        run_action(action_name=action_name, action=action)
