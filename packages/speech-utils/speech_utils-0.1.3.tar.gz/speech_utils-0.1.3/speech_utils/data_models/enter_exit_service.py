import types
from typing import final

from typing_extensions import Self


class EnterExitService:
    @final
    def __enter__(self) -> Self:
        self._enter_service()
        return self

    @final
    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: types.TracebackType | None = None,
    ):
        self._exit_service()

    def _enter_service(self) -> None:
        """
        load model/data into memory or establish some connection
        """

    def _exit_service(self) -> None:
        """
        tear-down
        """


SetupTeardown = EnterExitService
