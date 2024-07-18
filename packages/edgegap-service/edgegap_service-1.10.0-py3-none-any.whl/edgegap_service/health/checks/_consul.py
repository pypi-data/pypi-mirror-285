from edgegap_consul import ConsulReaderFactory

from ._interface import CheckInterface
from ._model import CheckInstanceModel


class ConsulCheck(CheckInterface):
    __name__ = 'Consul'

    def __init__(self, name: str = None):
        super().__init__(name)
        self.__reader = ConsulReaderFactory().from_env()

    def _check(self, **kwargs) -> CheckInstanceModel:
        try:
            ok = self.__reader.check()
            message = 'ok'
        except Exception as e:
            ok = False
            message = str(e)

        return CheckInstanceModel(ok=ok, message=message)
