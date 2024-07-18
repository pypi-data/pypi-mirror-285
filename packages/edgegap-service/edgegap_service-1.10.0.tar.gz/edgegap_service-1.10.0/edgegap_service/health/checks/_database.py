from edgegap_database import DatabaseOperator
from sqlmodel import Session, select

from ._interface import CheckInterface
from ._model import CheckInstanceModel


class DatabaseCheck(CheckInterface):
    __name__ = 'Database'

    def _check(self, **kwargs) -> CheckInstanceModel:
        ok = False
        message = 'No Session Supplied to Database Check'

        session = kwargs.get('session')

        if isinstance(session, Session):
            try:
                operator = DatabaseOperator(session)
                operator.exec(select(True))
                ok = True
                message = 'ok'
            except Exception as e:
                message = str(e)

        return CheckInstanceModel(ok=ok, message=message)
