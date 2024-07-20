"""
@author: jldupont
"""
import logging
import subprocess
import sys
from typing import List, Tuple, Any, Union
from .models import Result, Param, Params
from .utils import prepare_params, split_head_tail

logger = logging.getLogger("pygcloud")

__all__ = ["CommandLine", "GCloud", "gcloud"]


class CommandLine:

    def __init__(self, _exec_path: str, exit_on_error: bool = False,
                 log_error: bool = False):
        assert isinstance(_exec_path, str)
        self._exec_path = _exec_path
        self._last_command_args = None
        self._exit_on_error = exit_on_error
        self._last_result = None
        self._log_error = log_error

    @property
    def last_result(self):
        return self._last_result

    @property
    def last_command_args(self) -> List[Any]:
        return self._last_command_args

    def exec(self, params: Params, common: Params = None) -> Result:
        assert isinstance(params, list), f"Expected list, got: {type(params)}"

        if common is None:
            common = []

        command_args = prepare_params([self._exec_path] + params + common)

        logger.debug(f"CommandLine.exec: {command_args}")

        try:
            result = subprocess.run(
                command_args,              # Command to execute
                capture_output=True,
                text=True                  # Decode output as text
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"Command not found: {self._exec_path}")
        except PermissionError:
            raise PermissionError("Permission denied (or possibly "
                                  f"invalid exec path): {self._exec_path}")

        self._last_command_args = command_args

        if result.returncode == 0:
            r = Result(
                success=True,
                message=result.stdout.strip(),
                code=0
            )
        else:
            r = Result(
                success=False,
                message=result.stderr.strip(),
                code=result.returncode
            )

        already_logged = False

        if not r.success:
            if self._log_error:
                logging.error(f"Error executing command: {result}")
                already_logged = True

        if self._exit_on_error:
            if not r.success:
                sys.exit(r.code)

        if not already_logged:
            logger.debug(f"CommandLine.exec result: {result}")

        self._last_result = r

        return r


class GCloud(CommandLine):
    """
    https://cloud.google.com/sdk/gcloud/reference

    gcloud [alpha|beta] group [subgroup] command [params]

    Examples:
    ---------
    gcloud run describe my-service
    gcloud run deploy $name
    gcloud run jobs create $name
    gcloud run jobs describe $name
    gcloud run services list
    """

    def __init__(self, *head_tail: Union[List[Union[str, Tuple[str, str]]],
                                         Param], cmd="gcloud", **kw):
        """
        head_tail: [head_parameters ...] tail_parameters
        """
        super().__init__(cmd, **kw)
        self.head_tail = head_tail

    def __call__(self, *head_after: List[Union[str, Tuple[str, str], Param]]) \
            -> Result:
        """
        head_after: parameters that will be added at the head of the list
              following what was provided during initialization
        """
        head, tail = split_head_tail(self.head_tail)
        liste = head + list(head_after)
        liste.extend(tail)
        return self.exec(liste)


gcloud = GCloud()
