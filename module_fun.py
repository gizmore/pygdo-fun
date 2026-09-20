from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_UInt import GDT_UInt
from gdo.core.GDT_User import GDT_User
from gdo.date.GDT_Duration import GDT_Duration


class module_fun(GDO_Module):

    # Connection times are intentionally process-local. A quitjoin measures a
    # single continuous connection, not time accumulated across restarts.
    JOINED_AT: dict[str, float] = {}
    ROULETTE_LAST_PLAYER: dict[str, str] = {}
    ROULETTE_TURN: dict[str, int] = {}

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Duration('quitjoin_at_leastn').not_null().units(2).initial('32s'),
            GDT_Duration('quitjoin_world_record').not_null().units(2).initial('0'),
            GDT_User('quitjoin_world_record_holder'),
        ]

    def gdo_user_config(self) -> list[GDT]:
        return [
            GDT_UInt('roulette_uses').not_null().initial('0'),
            GDT_UInt('roulette_bangs').not_null().initial('0'),
            # Existing installations persist this enum key. Keep it hidden
            # until a dedicated data migration can remove it safely.
            GDT_Duration('quitjoin_min').not_null().units(2).initial('0').hidden(),
            GDT_Duration('quitjoin_user_record').not_null().units(2).initial('0'),
        ]

    def gdo_init(self):
        type(self).JOINED_AT = {}
        type(self).ROULETTE_LAST_PLAYER = {}
        type(self).ROULETTE_TURN = {}

    def gdo_subscribe_events(self):
        Application.EVENTS.subscribe('user_connected_server', self.on_user_connected)
        Application.EVENTS.subscribe('user_disconnected_server', self.on_user_disconnected)

    async def on_user_connected(self, user: GDO_User):
        self.remember_join(user)

    async def on_user_disconnected(self, user: GDO_User):
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
        # IRC may deliver JOIN and QUIT in one Dog tick (notably while
        # completing a names list). That is not a measurable connection and
        # must never turn into the unbeatable 0.000s record.
        if duration <= 0:
            return False
        from gdo.fun.method.quitjoin import quitjoin
        server = user.get_server()
        method = quitjoin().env_server(server).env_user(user)
        user_record = user.get_setting_value('quitjoin_user_record')
        value = f'{duration:.6f}s'
        personal_record = user_record == 0 or duration < user_record
        if personal_record:
            user.save_setting('quitjoin_user_record', value)

        server_record = method.get_config_server_value('quitjoin_server_record')
        server_recorded = server_record == 0 or duration < server_record
        if server_recorded:
            method.save_config_server('quitjoin_server_record', value)
            method.save_config_server('quitjoin_server_record_holder', str(user.get_id()))

        world_record = self.get_config_value('quitjoin_world_record')
        world_recorded = world_record == 0 or duration < world_record
        if world_recorded:
            await self.save_config_val('quitjoin_world_record', value)
            await self.save_config_val('quitjoin_world_record_holder', str(user.get_id()))

        user_channels = server.get_channels_for_user(user)
        for channel in user_channels:
            method.env_channel(channel)
            channel_record = method.get_config_channel_value('quitjoin_channel_record')
            channel_recorded = channel_record == 0 or duration < channel_record
            if channel_recorded:
                method.save_config_channel('quitjoin_channel_record', value)
                method.save_config_channel('quitjoin_channel_record_holder', str(user.get_id()))
            # A record in this room outranks a personal record for its own
            # audience.  No channel record is announced outside this room.
            if channel_recorded or personal_record:
                record_type = 'channel' if channel_recorded else 'personal'
                previous = channel_record if channel_recorded else user_record
                await self.announce_quitjoin_record(user, duration, record_type, previous, channel, method)

        # Server/world achievements are intentionally broader: every opted-in
        # room on this server gets the one highest-level announcement.
        if server_recorded or world_recorded:
            record_type = 'world' if world_recorded else 'server'
            previous = world_record if world_recorded else server_record
            for channel in server._channels.values():
                method.env_channel(channel)
                await self.announce_quitjoin_record(user, duration, record_type, previous, channel, method)

        if world_recorded:
            return 'world'
        if server_recorded:
            return 'server'
        if personal_record:
            return 'personal'
        return False

    async def announce_quitjoin_record(self, user: GDO_User, duration: float, record_type: str, previous: float, channel, method):
        """Celebrate the highest record reached by this QUIT in opted-in rooms."""
        if method.get_config_channel_value('disabled'):
            return
        if method.get_config_channel_value('announce') and duration <= self.get_config_value('quitjoin_at_leastn'):
            await channel.send(channel.t('msg_fun_quitjoin_record', (
                user.render_name(), record_type,
                self.render_quitjoin_duration(duration),
                self.render_quitjoin_duration(previous),
            )))

    @staticmethod
    def render_quitjoin_duration(duration: float) -> str:
        """Render records as 02.123s or 04:23.123s."""
        minutes, seconds = divmod(max(0, duration or 0), 60)
        hours, minutes = divmod(int(minutes), 60)
        if not minutes and not hours:
            return f'{seconds:06.3f}s'
        prefix = f'{hours:02d}:' if hours else ''
        return f'{prefix}{minutes:02d}:{seconds:06.3f}s'
