import typing
# flake8: noqa: I005
from logging import Logger

from azure.functions import AppExtensionBase, Context


class InvocationIdMidleware(AppExtensionBase):
    """A Python worker extension to add the invocation id to the response headers.
    """

    @classmethod
    def init(cls):
        pass

    @classmethod
    def configure(cls, *args, append_to_http_response:bool=False, **kwargs):
        pass

    @classmethod
    def pre_invocation_app_level(
        cls, logger: Logger, context: Context,
        func_args: typing.Dict[str, object],
        *args, **kwargs
    ) -> None:
        pass

    @classmethod
    def post_invocation_app_level(
        cls, logger: Logger, context: Context,
        func_args: typing.Dict[str, object],
        func_ret: typing.Optional[object],
        *args, **kwargs
    ) -> None:
        if func_ret.headers is not None:
            func_ret.headers.add('x-ms-invocation-id', context.invocation_id)