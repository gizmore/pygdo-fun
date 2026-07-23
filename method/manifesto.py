from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Trans import t


class manifesto(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'manifesto'

    def gdo_execute(self) -> GDT:
        return self.empty(t('msg_fun_manifesto'))
