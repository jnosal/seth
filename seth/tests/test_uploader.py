import os
import tempfile
import StringIO

from seth.tests import UnitTestBase
from seth.helpers.uploader import FileUploader


class MockCGIFieldStorage(object):

    def __init__(self, name='foo.png'):
        self.file = StringIO.StringIO('foo')
        self.filename = name


class UploaderTestCase(UnitTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

    def test_uploadf_get_request(self):
        request = self.get_csrf_request()
        uploader = FileUploader(request=request)
        self.assertEqual(uploader.push(), False)

    def test_uploader_request_does_not_have_file(self):
        request = self.get_csrf_request(request_method='POST')
        uploader = FileUploader(request=request)
        self.assertEqual(uploader.push(), False)

    def test_uploader_request_hav_file_key_in_post_but_its_a_data(self):
        request = self.get_csrf_request(post={
            'file': 'asd'
        }, request_method='POST')
        uploader = FileUploader(request=request)
        self.assertEqual(uploader.push(), False)

    def test_uploader_file_upload_is_successful(self):
        root = '/tmp'
        request = self.get_csrf_request(post={
            'file': MockCGIFieldStorage()
        }, request_method='POST')

        request.registry.settings['uploader.root_path'] = root
        request.registry.settings['uploader.valid_types'] = ['png']
        request.registry.settings['uploader.min_size'] = 0
        request.registry.settings['uploader.max_size'] = 12731278358

        with tempfile.NamedTemporaryFile() as f:
            uploader = FileUploader(request=request)
            identifier = uploader.push()
            self.assertNotEqual(identifier, None)
            self.assertIn('png', identifier)

        os.unlink(os.path.join(root, identifier))


