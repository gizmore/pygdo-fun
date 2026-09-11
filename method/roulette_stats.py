from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_User import GDT_User
from gdo.fun.method.roulette import roulette
from gdo.fun.module_fun import module_fun


class roulette_stats(Method):
    """Show the roulette counters for oneself or another user."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'roulette.stats'

    def gdo_user_type(self) -> str | None:
        return 'member,guest,link'

    def gdo_in_private(self) -> bool:
        return False

    def gdo_parameters(self) -> list[GDT]:
        return [GDT_User('user').positional()]

    def gdo_execute(self):
        user = self.param_value('user') or self._env_user
        turn = module_fun.ROULETTE_TURN.get(self._env_channel.get_id(), 0)
        return self.reply('msg_fun_roulette_stats', (
            user.render_name(),
            user.get_setting_value('roulette_uses'),
            user.get_setting_value('roulette_bangs'),
            turn,
            roulette.TURNS_PER_GAME,
        ))
