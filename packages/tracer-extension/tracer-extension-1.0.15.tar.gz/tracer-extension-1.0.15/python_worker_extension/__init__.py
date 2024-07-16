from ddtrace import patch_all, tracer
patch_all()

import typing
from logging import Logger

from azure.functions import AppExtensionBase, Context, HttpResponse
import time

class TracerExtension(AppExtensionBase):
    """A Python worker extension to start Datadog tracer for Azure Functions
    """

    @classmethod
    def init(cls):
        print("=========== in init NEW4 =============")

    @classmethod
    def pre_invocation_app_level(
        cls, logger: Logger, context: Context,
        func_args: typing.Dict[str, object],
        *args, **kwargs
    ) -> None:
        print("======= PRE ============")
        t = tracer.trace("top-level-span")
        cls.t = t
        # print("function args: " , func_args)
        # print("context: ", context, context.trace_context, context.function_directory )
       

    @classmethod
    def post_invocation_app_level(
        cls, logger: Logger, context: Context,
        func_args: typing.Dict[str, object],
        func_ret: typing.Optional[object],
        *args, **kwargs
    ) -> None:
        print("======= POST ============")
        cls.t.finish()