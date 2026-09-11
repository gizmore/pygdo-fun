import unittest
from unittest.mock import Mock, patch

from gdo.fun.method.roulette import roulette
from gdo.fun.method.roulette_stats import roulette_stats
from gdo.fun.module_fun import module_fun


class RouletteTest(unittest.TestCase):
    def test_outcomes(self):
        self.assertEqual(7, len(roulette.OUTCOMES))
        self.assertEqual(1, roulette.OUTCOMES.count('BANG'))
        self.assertEqual(5, roulette.OUTCOMES.count('click'))
        self.assertEqual(1, roulette.OUTCOMES.count('*WTF*JAM*'))

    def test_counters(self):
        for outcome in roulette.OUTCOMES:
            with self.subTest(outcome=outcome):
                method = object.__new__(roulette)
                method._env_user = Mock()
                method._env_user.get_id.return_value = f'user-{outcome}'
                method._env_channel = Mock()
                method._env_channel.get_id.return_value = 'channel'
                method.reply = Mock()
                module_fun.ROULETTE_LAST_PLAYER = {}
                module_fun.ROULETTE_TURN = {}
                outcome_index = roulette.OUTCOMES.index(outcome)
                with patch('gdo.fun.method.roulette.random.randrange', return_value=outcome_index):
                    method.gdo_execute()
                calls = method._env_user.increase_setting.call_args_list
                self.assertEqual(('roulette_uses', 1), calls[0].args)
                self.assertEqual(2 if outcome == 'BANG' else 1, len(calls))
                if outcome == 'BANG':
                    self.assertEqual(('roulette_bangs', 1), calls[1].args)
                method.reply.assert_called_once_with('msg_fun_roulette', (outcome, 1, 6))

    def test_same_player_cannot_play_twice(self):
        method = object.__new__(roulette)
        method._env_user = Mock()
        method._env_user.get_id.return_value = 'user-1'
        method._env_channel = Mock()
        method._env_channel.get_id.return_value = 'channel-1'
        method.reply = Mock()
        method.err = Mock()
        module_fun.ROULETTE_LAST_PLAYER = {'channel-1': 'user-1'}
        module_fun.ROULETTE_TURN = {'channel-1': 3}

        method.gdo_execute()

        method.err.assert_called_once_with('err_fun_roulette_same_player')
        method._env_user.increase_setting.assert_not_called()
        self.assertEqual(3, module_fun.ROULETTE_TURN['channel-1'])

    def test_game_counter_resets_after_six_turns(self):
        module_fun.ROULETTE_LAST_PLAYER = {}
        module_fun.ROULETTE_TURN = {'channel-1': 5}
        method = object.__new__(roulette)
        method._env_user = Mock()
        method._env_user.get_id.return_value = 'user-1'
        method._env_channel = Mock()
        method._env_channel.get_id.return_value = 'channel-1'
        method.reply = Mock()

        with patch('gdo.fun.method.roulette.random.randrange', return_value=1):
            method.gdo_execute()

        method.reply.assert_called_once_with('msg_fun_roulette', ('click', 6, 6))
        self.assertNotIn('channel-1', module_fun.ROULETTE_TURN)

    def test_stats_default_to_current_user(self):
        method = object.__new__(roulette_stats)
        method._env_user = Mock()
        method._env_user.render_name.return_value = 'Mira'
        method._env_user.get_setting_value.side_effect = lambda key: {
            'roulette_uses': 7,
            'roulette_bangs': 2,
        }[key]
        method.param_value = Mock(return_value=None)
        method._env_channel = Mock()
        method._env_channel.get_id.return_value = 'channel-1'
        method.reply = Mock()
        module_fun.ROULETTE_TURN = {'channel-1': 4}

        method.gdo_execute()

        method.reply.assert_called_once_with(
            'msg_fun_roulette_stats', ('Mira', 7, 2, 4, 6))

    def test_stats_accept_another_user(self):
        target = Mock()
        target.render_name.return_value = 'Gizmore'
        target.get_setting_value.side_effect = lambda key: {
            'roulette_uses': 12,
            'roulette_bangs': 3,
        }[key]
        method = object.__new__(roulette_stats)
        method._env_user = Mock()
        method._env_channel = Mock()
        method._env_channel.get_id.return_value = 'channel-1'
        method.param_value = Mock(return_value=target)
        method.reply = Mock()
        module_fun.ROULETTE_TURN = {'channel-1': 2}

        method.gdo_execute()

        method.reply.assert_called_once_with(
            'msg_fun_roulette_stats', ('Gizmore', 12, 3, 2, 6))
