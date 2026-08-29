from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.date.GDT_Duration import GDT_Duration
from gdo.date.Time import Time


class module_fun(GDO_Module):

    # Connection times are intentionally process-local. A quitjoin measures a
    # single continuous connection, not time accumulated across restarts.
    JOINED_AT: dict[str, float] = {}

    def gdo_user_config(self) -> list[GDT]:
        return [
            GDT_Duration('quitjoin_min').not_null().units(2).initial('0'),
        ]

    def gdo_init(self):
        type(self).JOINED_AT = {}

    def gdo_subscribe_events(self):
        Application.EVENTS.subscribe('user_joined_server', self.on_user_joined)
        Application.EVENTS.subscribe('user_quit_server', self.on_user_quit)

    async def on_user_joined(self, user: GDO_User):
        self.remember_join(user)

    async def on_user_quit(self, user: GDO_User):
        await self.remember_quit(user)

    @classmethod
    def for_irc(cls):
        """Return Fun only when it is installed and enabled.

        IRC lifecycle commands must not acquire a hard dependency on an
        optional module.  They call this small bridge because JOIN/QUIT are
        the authoritative connection boundaries for IRC.
        """
        loader = getattr(Application, 'LOADER', None)
        if loader is None:
            return None
        fun = loader.get_module('fun')
        return fun if fun.is_enabled() else None

    def remember_join(self, user: GDO_User, now: float | None = None):
        if user.is_persisted():
            type(self).JOINED_AT[user.get_id()] = Application.TIME if now is None else now

    async def remember_quit(self, user: GDO_User, now: float | None = None):
        joined_at = type(self).JOINED_AT.pop(user.get_id(), None)
        if joined_at is None or not user.is_persisted():
            return False
        duration = max(0.0, (Application.TIME if now is None else now) - joined_at)
        previous = user.get_setting_value('quitjoin_min')
        if previous == 0 or duration < previous:
            # Duration values are stored in the same human form accepted by
            # GDT_Duration; an explicit seconds suffix also keeps SQL sorting
            # numeric for all recorded values.
            user.save_setting('quitjoin_min', f'{duration:.6f}s')
            await self.announce_quitjoin_record(user, duration)
            return True
        return False

    async def announce_quitjoin_record(self, user: GDO_User, duration: float):
        """Celebrate short new records only in explicitly configured rooms."""
        from gdo.fun.method.quitjoin import quitjoin
        for channel in list(user.get_server()._channels.values()):
            method = quitjoin().env_server(user.get_server()).env_channel(channel)
            if method.get_config_channel_value('disabled'):
                continue
            threshold = method.get_config_channel_value('announce_duration')
            if threshold and duration <= threshold:
                await channel.send(channel.t('msg_fun_quitjoin_record', (
                    user.render_name(), Time.human_duration(duration, 2),
                )))
