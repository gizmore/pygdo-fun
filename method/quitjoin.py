from gdo.base.GDO import GDO
from gdo.base.Query import Query
from gdo.base.Render import Mode
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_UserName import GDT_UserName
from gdo.date.GDT_Duration import GDT_Duration
from gdo.table.MethodQueryTable import MethodQueryTable
from gdo.user.GDT_ProfileLink import GDT_ProfileLink


class quitjoin(MethodQueryTable):
    """Rank the shortest observed connection lifetimes."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'quitjoin'

    @classmethod
    def gdo_trig(cls) -> str:
        return 'qj'

    def gdo_table(self) -> GDO:
        return GDO_User.table()

    @classmethod
    def gdo_method_config_channel(cls) -> list:
        # Zero is deliberately silent; a room must opt in to record notices.
        return [GDT_Duration('announce_duration').not_null().units(2).initial('0')]

    def gdo_table_headers(self) -> list:
        return [
            GDT_UserName('user_name').label('username'),
            GDT_Duration('quitjoin_min').label('quitjoin_min'),
        ]

    def gdo_table_query(self) -> Query:
        query = GDO_User.table().select()
        GDO_User.join_setting(query, 'quitjoin_min')
        return query.where("setting_quitjoin_min.uset_val IS NOT NULL AND setting_quitjoin_min.uset_val != '0'")

    def gdo_order_default(self):
        return 'CAST(quitjoin_min AS DECIMAL(20,6)) ASC'

    def render_user_name(self, _field, user: GDO_User):
        return GDT_ProfileLink().user(user).render(Mode.render_cell)
