from gdo.base.GDT import GDT
from gdo.base.Method import Method


class gizmore(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'gizmore'

    def gdo_execute(self) -> GDT:
        return self.msg('md_fun_gizmore')
