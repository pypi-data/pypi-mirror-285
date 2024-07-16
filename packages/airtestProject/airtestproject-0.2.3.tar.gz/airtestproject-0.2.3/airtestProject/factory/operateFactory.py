import threading
from abc import ABC, abstractmethod

from airtestProject.abstractBase.OperateBase import OperateABC
from airtestProject.abstractBase.operateBaseImp.airtestOperate import myAirTest
from airtestProject.abstractBase.operateBaseImp.pocoOperate import myPoco
from airtestProject.poco.drivers.unity3d import UnityPoco
from airtestProject.factory.SingletonFactory import SingletonFactory


class AbstractFactory(ABC):
    def __init__(self):
        self._local = threading.local()

    @abstractmethod
    def create_operate_abc(self, **kwargs) -> OperateABC:
        pass


# 具体工厂
class PocoFactory(AbstractFactory, metaclass=SingletonFactory):
    def __init__(self):
        super().__init__()
        self._UnityPoco = None

    def create_operate_abc(self, **kwargs) -> OperateABC:
        if self._UnityPoco is None:
            self._UnityPoco = UnityPoco()
        if not hasattr(self._local, '_PageInstance'):
            self._local._PocoInstance = myPoco(self._UnityPoco)
        return self._local._PocoInstance


# 具体工厂
class AirTestFactory(AbstractFactory, metaclass=SingletonFactory):
    def __init__(self):
        super().__init__()

    def create_operate_abc(self, language=None, **kwargs) -> OperateABC:
        if not hasattr(self._local, '_AirTestInstance'):
            self._local._AirTestInstance = myAirTest(language)
        return self._local._AirTestInstance


def operate(factory_name: str, **kwargs) -> OperateABC:
    """

    :param factory_name: 工厂名称，可以是poco或air。
    :param kwargs: 可选参数。如果factory_name是air，可以传入language参数。设置语言需要在最开始设置，否者按照默认运行
    :return: 返回具体的工厂实例。
    """
    factories = {
        'poco': PocoFactory,
        'air': AirTestFactory
    }
    factory_class = factories[factory_name]
    factory = factory_class()
    product = factory.create_operate_abc(**kwargs)
    return product

# class operateFactoryOut:
#
#
