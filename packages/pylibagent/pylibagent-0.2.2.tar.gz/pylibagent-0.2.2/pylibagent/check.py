import abc
from typing import Dict, List, Any


class CheckBase(abc.ABC):
    """CheckBase can be used for writing demonized checks.
    """

    key: str  # Check key (should not be changed)
    interval: int  # Check interval

    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, 'key'):
            raise NotImplementedError('key not implemented')
        if not isinstance(cls.key, str):
            raise NotImplementedError('key must be type str')
        if not hasattr(cls, 'interval'):
            raise TypeError('interval not implemented')
        if not isinstance(cls.interval, int):
            raise TypeError('interval must be type int')
        return super().__init_subclass__(**kwargs)

    @abc.abstractclassmethod
    async def run(cls) -> Dict[str, List[Dict[str, Any]]]:
        ...
