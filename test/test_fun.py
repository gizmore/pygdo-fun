from gdo.base.Application import Application
from gdo.core.GDO_UserSetting import GDO_UserSetting
import os
import unittest
from unittest.mock import ANY, AsyncMock, MagicMock, patch
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_Channel import GDO_Channel
from gdo.fun.GDT_CowsayType import GDT_CowsayType
from gdo.fun.method.quitjoin import quitjoin
from gdo.fun.method.hh import hh
from gdo.fun.method.afd import afd
from gdo.fun.module_fun import module_fun
from gdo.base.Trans import tiso
from gdotest.TestUtil import reinstall_module, text_plug, GDOTestCase, cli_plug, cli_gizmore, all_private_messages, install_module


class HattedHackerTest(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        Application.init_cli()

    async def test_uses_local_channel_translations_without_a_parameter(self):
        channel = MagicMock()
        channel.get_lang_iso.return_value = 'de'
        method = hh().env_channel(channel)
        method.empty = MagicMock(side_effect=lambda text: text)
        self.assertEqual(tiso('de', 'msg_fun_hh'), await method.gdo_execute())

    async def test_uses_the_local_english_text(self):
        channel = MagicMock()
        channel.get_lang_iso.return_value = 'en'
        method = hh().env_channel(channel)
        method.empty = MagicMock(side_effect=lambda text: text)
        self.assertEqual(tiso('en', 'msg_fun_hh'), await method.gdo_execute())

    async def test_uses_the_local_korean_text(self):
        channel = MagicMock()
        channel.get_lang_iso.return_value = 'ko'
        method = hh().env_channel(channel)
        method.empty = MagicMock(side_effect=lambda text: text)
        self.assertEqual(tiso('ko', 'msg_fun_hh'), await method.gdo_execute())

    async def test_afd_returns_its_local_explanation(self):
        self.assertEqual('afd', afd.gdo_trigger())
        for language in ('en', 'de', 'ko'):
            channel = MagicMock()
            channel.get_lang_iso.return_value = language
            method = afd().env_channel(channel)
            method.empty = MagicMock(side_effect=lambda text: text)
            self.assertEqual(tiso(language, 'msg_fun_afd'), method.gdo_execute())

class FunTestCase(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        Application.init_cli()
        loader = ModuleLoader.instance()
        install_module('fun')
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        loader.init_cli()

    async def test_00_reinstall(self):
        reinstall_module('fun')

    async def test_01_cowsay(self):
        giz = cli_gizmore()
        types = GDT_CowsayType('goo').init_choices()
        out = cli_plug(giz, '$cowsay Hello World')
        self.assertIn('Hello World', out, "cowsay does not work.")
        out = cli_plug(giz, '$cowsay --img=bee Hello World')
        self.assertIn('Hello World', out, "cowsay does not work.")
        out = cli_plug(giz, '$cowsay --img=be Hello World')
        self.assertIn('Hello World', out, "cowsay does not work.")

    async def test_05_gizmore(self):
        giz = cli_gizmore()

    async def test_055_world_domination_is_a_text_only_joke(self):
        giz = cli_gizmore()
        out = cli_plug(giz, '$world_domination acquire every cat')
        self.assertTrue(any(message in out for message in (
            'This is not bizarroworld.',
            'Your evil plan failed.',
            'Syntax error in the evil plan.',
            'Evil plan is running.',
            'Database error.',
        )))

    async def test_06_quitjoin_tracks_the_shortest_connection(self):
        user = cli_gizmore()
        fun = module_fun.instance()
        server = user.get_server()
        channel = server.get_or_create_channel('#quitjoin-test')
        server._channels[channel.get_name()] = channel
        await channel.on_user_joined(user)
        method = quitjoin().env_server(server).env_channel(channel).env_user(user)
        await fun.save_config_val('quitjoin_world_record', '0')
        method.save_config_server('quitjoin_server_record', '0')
        method.save_config_channel('quitjoin_channel_record', '0')
        user.save_setting('quitjoin_user_record', '0')
        fun.remember_join(user, 100)
        self.assertEqual('world', await fun.remember_quit(user, 194))
        self.assertEqual(94, fun.get_config_value('quitjoin_world_record'))
        self.assertEqual(str(user.get_id()), fun.get_config_val('quitjoin_world_record_holder'))
        self.assertEqual(94, method.get_config_server_value('quitjoin_server_record'))
        self.assertEqual(str(user.get_id()), method.get_config_server_val('quitjoin_server_record_holder'))
        self.assertEqual(94, method.get_config_channel_value('quitjoin_channel_record'))
        self.assertEqual(str(user.get_id()), method.get_config_channel_val('quitjoin_channel_record_holder'))
        self.assertEqual(94, user.get_setting_value('quitjoin_user_record'))

        await fun.save_config_val('quitjoin_world_record', '70s')
        method.save_config_server('quitjoin_server_record', '80s')
        user.save_setting('quitjoin_user_record', '0')
        fun.remember_join(user, 300)
        self.assertEqual('personal', await fun.remember_quit(user, 390))
        self.assertEqual(70, fun.get_config_value('quitjoin_world_record'))
        self.assertEqual(80, method.get_config_server_value('quitjoin_server_record'))
        self.assertEqual(90, user.get_setting_value('quitjoin_user_record'))

        method.save_config_server('quitjoin_server_record', '100s')
        user.save_setting('quitjoin_user_record', '0')
        fun.remember_join(user, 500)
        self.assertEqual('server', await fun.remember_quit(user, 590))
        self.assertEqual(70, fun.get_config_value('quitjoin_world_record'))
        self.assertEqual(90, method.get_config_server_value('quitjoin_server_record'))
        self.assertEqual(90, user.get_setting_value('quitjoin_user_record'))

        user.save_setting('quitjoin_user_record', '80s')
        method.save_config_channel('quitjoin_channel_record', '100s')
        fun.remember_join(user, 700)
        self.assertFalse(await fun.remember_quit(user, 790))
        self.assertEqual(90, method.get_config_channel_value('quitjoin_channel_record'))

        fun.remember_join(user, 300)
        self.assertFalse(await fun.remember_quit(user, 500))
        self.assertEqual(70, fun.get_config_value('quitjoin_world_record'))
        self.assertEqual(90, method.get_config_server_value('quitjoin_server_record'))
        self.assertEqual(90, method.get_config_channel_value('quitjoin_channel_record'))
        self.assertEqual(80, user.get_setting_value('quitjoin_user_record'))

        fun.remember_join(user, 600)
        self.assertFalse(await fun.remember_quit(user, 600))
        self.assertEqual(70, fun.get_config_value('quitjoin_world_record'))
        self.assertEqual(90, method.get_config_server_value('quitjoin_server_record'))
        self.assertEqual(90, method.get_config_channel_value('quitjoin_channel_record'))
        self.assertEqual(80, user.get_setting_value('quitjoin_user_record'))

        out = cli_plug(user, '$quitjoin')
        self.assertIn('Quitjoin', out)
        self.assertIn(user.render_name(), out)

    async def test_065_quitjoin_reset_requires_confirmation_and_purges_records(self):
        user = cli_gizmore()
        fun = module_fun.instance()
        server = user.get_server()
        channel = server.get_or_create_channel('#quitjoin-reset-test')
        method = quitjoin().env_server(server).env_channel(channel).env_user(user)
        await fun.save_config_val('quitjoin_world_record', '10s')
        await fun.save_config_val('quitjoin_world_record_holder', str(user.get_id()))
        method.save_config_server('quitjoin_server_record', '11s')
        method.save_config_server('quitjoin_server_record_holder', str(user.get_id()))
        method.save_config_channel('quitjoin_channel_record', '12s')
        method.save_config_channel('quitjoin_channel_record_holder', str(user.get_id()))
        user.save_setting('quitjoin_user_record', '13s')
        fun.remember_join(user, 100)

        self.assertIn('iamsure', cli_plug(user, '$quitjoin --reset nope'))
        out = cli_plug(user, '$quitjoin --reset iamsure')
        self.assertIn('QuitJoin reset', out)
        self.assertEqual(0, fun.get_config_value('quitjoin_world_record'))
        # A real future JOIN/QUIT constructs a fresh method, just as the
        # command does.  Its values must come back as their defaults.
        method = quitjoin().env_server(server).env_channel(channel).env_user(user)
        self.assertEqual(0, method.get_config_server_value('quitjoin_server_record'))
        self.assertEqual(0, method.get_config_channel_value('quitjoin_channel_record'))
        self.assertIsNone(GDO_UserSetting.get_setting(user, 'quitjoin_user_record'))
        self.assertEqual({}, fun.JOINED_AT)

    async def test_066_quitjoin_reset_announces_to_opted_in_online_channels(self):
        channel = MagicMock()
        channel.is_online.return_value = True
        channel.send_text = AsyncMock()
        with patch.object(GDO_Channel, 'with_setting', return_value=[channel]) as opted_in:
            await quitjoin().announce_reset(42, 3)

        opted_in.assert_called_once_with(ANY, 'announce', '1')
        channel.send_text.assert_awaited_once_with('msg_quitjoin_records_reset', (42, 3))

    def test_07_quitjoin_duration_rendering(self):
        self.assertEqual('02.123s', module_fun.render_quitjoin_duration(2.123))
        self.assertEqual('04:23.123s', module_fun.render_quitjoin_duration(263.123))
