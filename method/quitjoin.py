from gdo.base.GDO import GDO
from gdo.base.GDO_ModuleVal import GDO_ModuleVal
from gdo.base.GDT import GDT
from gdo.base.Cache import Cache
from gdo.base.Query import Query
from gdo.base.Render import Mode
from gdo.core.GDO_Method import GDO_Method
from gdo.core.GDO_MethodValChannel import GDO_MethodValChannel
from gdo.core.GDO_MethodValServer import GDO_MethodValServer
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UserName import GDT_UserName
from gdo.core.GDT_User import GDT_User
from gdo.core.GDO_UserSetting import GDO_UserSetting
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

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_String('reset').maxlen(16),
        ]

    async def gdo_execute(self) -> GDT:
        reset = self.param_val('reset')
        if reset:
            if reset != 'iamsure':
                return self.reply('msg_quitjoin_reset_confirm')
            if not self._env_user.is_staff():
                return self.reply('msg_quitjoin_reset_staff')
            return await self.reset_records()
        return super().gdo_execute()

    async def reset_records(self) -> GDT:
        """Purge every stored record scope without touching room preferences."""
        from gdo.fun.module_fun import module_fun

        fun = module_fun.instance()
        # Delete per-user values through the model so active user caches and
        # other Dog processes are notified too.
        user_settings = GDO_UserSetting.table().select().where(
            "uset_key='quitjoin_user_record'"
        ).exec().fetch_all()
        for setting in user_settings:
            if user := GDO_User.table().get_by_id(setting.gdo_val('uset_user')):
                user.reset_setting('quitjoin_user_record')

        method_id = GDO_Method.for_method(self).get_id()
        server_settings = GDO_MethodValServer.table().select().where(
            f"mv_method={method_id} AND mv_key IN "
            "('quitjoin_server_record', 'quitjoin_server_record_holder')"
        ).exec().fetch_all()
        GDO_MethodValServer.table().delete_where(
            f"mv_method={method_id} AND mv_key IN "
            "('quitjoin_server_record', 'quitjoin_server_record_holder')"
        )
        for server in GDO_Server.table().all():
            for key in ('quitjoin_server_record', 'quitjoin_server_record_holder'):
                Cache.obj_search_id(GDO_MethodValServer.table(), {
                    'mv_method': str(method_id), 'mv_server': str(server.get_id()), 'mv_key': key,
                }, True)
        self._config_server_for('quitjoin_server_record').val('0')
        self._config_server_for('quitjoin_server_record_holder').val('')

        channel_settings = GDO_MethodValChannel.table().select().where(
            f"mv_method={method_id} AND mv_key IN "
            "('quitjoin_channel_record', 'quitjoin_channel_record_holder')"
        ).exec().fetch_all()
        GDO_MethodValChannel.table().delete_where(
            f"mv_method={method_id} AND mv_key IN "
            "('quitjoin_channel_record', 'quitjoin_channel_record_holder')"
        )
        for channel in GDO_Channel.table().all():
            for key in ('quitjoin_channel_record', 'quitjoin_channel_record_holder'):
                Cache.obj_search_id(GDO_MethodValChannel.table(), {
                    'mv_method': str(method_id), 'mv_channel': str(channel.get_id()), 'mv_key': key,
                }, True)
        self._config_channel_for('quitjoin_channel_record').val('0')
        self._config_channel_for('quitjoin_channel_record_holder').val('')
        world_records = len(GDO_ModuleVal.table().select().where(
            f"mv_module={fun.get_id()} AND mv_key IN "
            "('quitjoin_world_record', 'quitjoin_world_record_holder')"
        ).exec().fetch_all())
        # Module configuration is cached in the running Dog. Persisting its
        # defaults instead of deleting rows updates that cache immediately and
        # also keeps a restart from resurrecting the old record.
        await fun.save_config_val('quitjoin_world_record', '0', force=True)
        await fun.save_config_val('quitjoin_world_record_holder', '', force=True)

        active_runs = len(fun.JOINED_AT)
        fun.JOINED_AT.clear()
        deleted = len(user_settings) + len(server_settings) + len(channel_settings) + world_records
        await self.announce_reset(deleted, active_runs)
        return self.reply('msg_quitjoin_reset', (deleted, active_runs))

    async def announce_reset(self, deleted: int, active_runs: int):
        """Tell currently connected channels which opted into announcements."""
        for channel in GDO_Channel.with_setting(self, 'announce', '1'):
            if channel.is_online():
                await channel.send_text('msg_quitjoin_records_reset', (deleted, active_runs))

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
            GDT_Bool('announce').initial('0'),
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
