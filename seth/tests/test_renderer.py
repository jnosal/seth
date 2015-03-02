from pyramid.renderers import render

from seth.tests import IntegrationTestBase, UnitTestBase
from seth.renderers import BaseSethRenderer, SethRendererException


class BaseRendererTestCase(UnitTestBase):

    def test_base_renderer_class(self):
        request = self.get_csrf_request()
        renderer = BaseSethRenderer()
        # Test prepare response flow
        renderer.prepare_response(request, 'text/html', file_name='file.pdf')


class CsvRendererTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

    def test_csv_renderer_raises_exception_when_inappropriate_params(self):
        self.assertRaises(SethRendererException, lambda: render('csv', {}))

    def test_csv_renderer_render_empty_rows(self):
        body = render('csv', {'rows': []})
        self.assertEqual(body, u"")

    def test_csv_renderer_is_succesful(self):
        body = render('csv', {'rows': [('a', 'b'), ('c', 'd')]})
        assert body
        for el in ['a', 'b', 'c', 'd']:
            self.assertIn(el, body)

    def test_csv_renderer_with_header_is_succesful(self):
        body = render('csv', {'header': ('d1', 'd2'), 'rows': [('a', 'b'), ('c', 'd')]})
        assert body
        for el in ['d1', 'd2', 'a', 'b', 'c', 'd']:
            self.assertIn(el, body)


class PdfRendererTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

    def test_pdf_renderer_raises_exception_when_inappropriate_params(self):
        self.assertRaises(SethRendererException, lambda: render('pdf', {}))
        self.assertRaises(SethRendererException, lambda: render('pdf', {'template': 'ads.txt'}))

    def test_pdf_renderer_render_empty_html(self):
        body = render('pdf', {'html': ''})
        assert body

    def test_pdf_renderer_is_succesful(self):
        body = render('pdf', {'html': 'aasd'})
        assert body

    def test_wrong_html_raises_pdf_error(self):
        self.assertRaises(SethRendererException, lambda: render('pdf', {'html': 123123123123}))