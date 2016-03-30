import mock

from seth.tests import UnitTestBase, IntegrationTestBase
from seth import i18n


class I18nTestCase(UnitTestBase):

    def test_inappropriate_file_provided(self):
        handler = i18n.JSTranslationsHandler()
        self.assertRaises(IOError, lambda: handler.pofile_to_js('/tmp/i_dont_exist', 'en'))

    def test_inappropriate_contents_provided_for_locale(self):
        handler = i18n.JSTranslationsHandler()
        open_ = mock.mock_open(read_data="asd")
        with mock.patch('__builtin__.open', open_):
            self.assertRaises(Exception, lambda: handler.pofile_to_js('/tmp/i_dont_exist', 'en'))

    def test_proper_pofile_provided(self):
        handler = i18n.JSTranslationsHandler()
        read_data = '''
        msgid "foo"
        msgstr "bar"
        '''
        open_ = mock.mock_open(read_data=read_data)
        with mock.patch('__builtin__.open', open_):
            json_output = handler.pofile_to_js('', 'en')
            self.assertIn('translations', json_output)

    def test_proper_pofile_provided_triggers_file_generation(self):
        handler = i18n.JSTranslationsHandler()
        temp_file = '/tmp/out.js'

        class File(object):

            def readlines(self, *args, **kwargs):
                return '''
                msgid "foo"
                msgstr "bar"
                '''

        handler.generate_file('en', File(), temp_file)

        with open(temp_file, 'r') as f:
            json_output = f.read()
            self.assertIn('translations', json_output)