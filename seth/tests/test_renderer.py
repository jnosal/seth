from pyramid.renderers import render

from seth.tests import IntegrationTestBase
from seth.renderers import SethRendererException


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
