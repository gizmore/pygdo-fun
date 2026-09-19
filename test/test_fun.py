from gdo.base.Application import Application
import os
from gdo.base.ModuleLoader import ModuleLoader
from gdo.fun.GDT_CowsayType import GDT_CowsayType
from gdo.fun.method.quitjoin import quitjoin
from gdo.fun.module_fun import module_fun
from gdotest.TestUtil import reinstall_module, text_plug, GDOTestCase, cli_plug, cli_gizmore, all_private_messages, install_module

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

    def test_07_quitjoin_duration_rendering(self):
        self.assertEqual('02.123s', module_fun.render_quitjoin_duration(2.123))
        self.assertEqual('04:23.123s', module_fun.render_quitjoin_duration(263.123))
