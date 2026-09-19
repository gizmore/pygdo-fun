from gdo.base.GDO import GDO
from gdo.base.Query import Query
from gdo.base.Render import Mode
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_UserName import GDT_UserName
from gdo.core.GDT_User import GDT_User
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
    def gdo_method_config_server(cls) -> list:
        return [
            GDT_Duration('quitjoin_server_record').not_null().units(2).initial('0'),
            GDT_User('quitjoin_server_record_holder'),
        ]

    @classmethod
    def gdo_method_config_channel(cls) -> list:
        # Record data is always kept; notices require the channel opt-in.
        return [
            GDT_Bool('announce').initial('1'),
            GDT_Duration('quitjoin_channel_record').not_null().units(2).initial('0'),
            GDT_User('quitjoin_channel_record_holder'),
        ]

    def gdo_table_headers(self) -> list:
        return [
            GDT_UserName('user_name').label('username'),
            GDT_Duration('quitjoin_user_record').label('quitjoin_user_record'),
        ]

    def gdo_table_query(self) -> Query:
        query = GDO_User.table().select()
        GDO_User.join_setting(query, 'quitjoin_user_record')
        return query.where("setting_quitjoin_user_record.uset_val IS NOT NULL AND setting_quitjoin_user_record.uset_val != '0'")

    def gdo_order_default(self):
        return 'CAST(quitjoin_user_record AS DECIMAL(20,6)) ASC'

    def render_user_name(self, _field, user: GDO_User):
        return GDT_ProfileLink().user(user).render(Mode.render_cell)
