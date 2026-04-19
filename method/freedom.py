from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.message.GDT_LI import GDT_LI
from gdo.message.GDT_UL import GDT_UL


class freedom(Method):

    def gdo_execute(self) -> GDT:

        return GDT_UL().add_fields(
            GDT_LI().ht
        )