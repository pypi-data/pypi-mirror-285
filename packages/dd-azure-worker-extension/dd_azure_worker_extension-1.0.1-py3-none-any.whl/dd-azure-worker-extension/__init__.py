from ddtrace import patch_all, tracer
patch_all()

from azure.functions import AppExtensionBase

class TracerExtension(AppExtensionBase):
    """A Python worker extension to start Datadog tracer and insturment Azure Functions 
    """
    @classmethod
    def init(cls):
        pass

    @classmethod
    def pre_invocation_app_level(cls, *args, **kwargs) -> None:
        t = tracer.trace("azure.function")
        cls.t = t      

    @classmethod
    def post_invocation_app_level(cls, *args, **kwargs ) -> None:
        cls.t.finish()