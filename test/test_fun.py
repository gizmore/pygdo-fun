from gdo.base.Application import Application
import os
from gdo.base.ModuleLoader import ModuleLoader
from gdo.fun.GDT_CowsayType import GDT_CowsayType
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
        fun.remember_join(user, 100)
        self.assertTrue(await fun.remember_quit(user, 194))
        self.assertEqual(94, user.get_setting_value('quitjoin_min'))
        fun.remember_join(user, 300)
        self.assertFalse(await fun.remember_quit(user, 500))
        self.assertEqual(94, user.get_setting_value('quitjoin_min'))
        out = cli_plug(user, '$quitjoin')
        self.assertIn('Quitjoin', out)
        self.assertIn(user.render_name(), out)
