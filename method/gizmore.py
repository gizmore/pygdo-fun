from gdo.base.GDT import GDT
from gdo.base.Method import Method


class gizmore(Method):

    def gdo_execute(self) -> GDT:
        return self.msg('md_fun_gizmore')
