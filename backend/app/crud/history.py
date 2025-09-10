from backend.app.crud.base import BaseCURD
from backend.app.models.user import History


class HistoryCURD(BaseCURD[History]):
    ...


crud_history = HistoryCURD(History)