import os

from seth import command
from seth.tests import here
from seth.tests import UnitTestBase


test_ini = os.path.join(here, 'test.ini')


class CommandUtilityTestCase(UnitTestBase):

    def test_raises_TypeError_when_no_ini_file(self):
        self.assertRaises(TypeError, lambda: command.CommandManager())

    def test_raises_TypeError_when_registering_same_command_twice(self):
        class MyCommand(command.Command):
            name = 'my_cmd'

        manager = command.CommandManager(test_ini)
        manager.register_command(MyCommand)
        self.assertRaises(TypeError, lambda: manager.register_command(MyCommand))

    def test_instantiate_app_proper_ini_file(self):
        manager = command.CommandManager(test_ini)
        self.assertEqual(manager.commands, {})
        self.assertNotEqual(manager.ini_file, None)
        env = manager.bootstrap_application()
        self.assertNotEqual(env, None)
        self.assertIn('app', env)
        self.assertIn('root', env)
        self.assertIn('root_factory', env)
        self.assertIn('registry', env)

    def test_instantiate_app_ini_file_does_not_exist(self):
        manager = command.CommandManager('i_dont_exist.ini')
        self.assertEqual(manager.commands, {})
        self.assertNotEqual(manager.ini_file, None)
        self.assertRaises(IOError, lambda: manager.bootstrap_application())

    def test_register_command(self):
        class MyCommand(command.Command):
            name = 'my_cmd'

            def run(self):
                print "hello"

        manager = command.CommandManager(test_ini)
        manager.register_command(MyCommand)

        self.assertIn('my_cmd', manager.commands)
        self.assertEqual(manager.commands['my_cmd'], MyCommand)

    def test_run_no_command_found_pasess(self):
        manager = command.CommandManager(test_ini)
        manager.run('my_cmd', testing=True)

    def test_run_command(self):
        class MyCommand(command.Command):
            name = 'my_cmd'

            def run(self):
                pass

        manager = command.CommandManager(test_ini)
        manager.register_command(MyCommand)
        manager.run('my_cmd', testing=True)

    def test_raise_NotImplementedError(self):
        class MyCommand(command.Command):
            name = 'my_cmd'


        manager = command.CommandManager(test_ini)
        manager.register_command(MyCommand)
        self.assertRaises(NotImplementedError, lambda: manager.run('my_cmd', testing=True))