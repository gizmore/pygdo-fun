import random

from gdo.base.Method import Method
from gdo.fun.module_fun import module_fun


class roulette(Method):
    """A fictional, text-only seven-outcome roulette game."""

    JAM = 'jam'
    OUTCOMES = ('BANG', 'click', 'click', 'click', 'click', 'click', JAM)
    TURNS_PER_GAME = 6

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'roulette'

    def gdo_user_type(self) -> str | None:
        return 'member,guest,link'

    def gdo_in_private(self) -> bool:
        return False

    def gdo_execute(self):
        channel_id = self._env_channel.get_id()
        user_id = self._env_user.get_id()
        last_players = module_fun.ROULETTE_LAST_PLAYER
        if last_players.get(channel_id) == user_id:
            return self.err('err_fun_roulette_same_player')

        # Every trigger has exactly the requested 1/7 BANG probability.  The
        # duplicate click entries deliberately account for five of the seven
        # equally likely outcomes.
        outcome = self.OUTCOMES[random.randrange(len(self.OUTCOMES))]
        self._env_user.increase_setting('roulette_uses', 1)
        if outcome == self.JAM:
            module_fun.ROULETTE_TURN.pop(channel_id, None)
            last_players.pop(channel_id, None)
            return self.reply('msg_fun_roulette_jam')

        turn = module_fun.ROULETTE_TURN.get(channel_id, 0) + 1
        if outcome == 'BANG':
            self._env_user.increase_setting('roulette_bangs', 1)
        if outcome == 'BANG':
            module_fun.ROULETTE_TURN.pop(channel_id, None)
            last_players.pop(channel_id, None)
        elif turn == self.TURNS_PER_GAME:
            module_fun.ROULETTE_TURN.pop(channel_id, None)
            last_players[channel_id] = user_id
        else:
            module_fun.ROULETTE_TURN[channel_id] = turn
            last_players[channel_id] = user_id
        return self.reply('msg_fun_roulette', (outcome, turn, self.TURNS_PER_GAME))
