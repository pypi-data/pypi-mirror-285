import abc

from ._model import CheckInstanceModel, CheckModel


class CheckInterface(abc.ABC):
    __name__: str

    def __init__(self, name: str = None):
        self.__name = name if isinstance(name, str) else self.__name__

    def check(self, **kwargs) -> CheckModel:
        instance = self._check(**kwargs)

        return CheckModel(name=self.__name, **instance.model_dump())

    @abc.abstractmethod
    def _check(self, **kwargs) -> CheckInstanceModel:
        """

        @return: tuple[bool, str]
        bool: if the check is ok
        str: message
        """
