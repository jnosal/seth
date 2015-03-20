import logging
from time import time
from cStringIO import StringIO

from pyramid.renderers import render

from seth.helpers.unicodecsv import UnicodeWriter

logger = logging.getLogger('seth')


class SethRendererException(Exception):
    """"""


class BaseSethRenderer(object):

    def render_template(self, template_name, context, request):
        return render(template_name, context, request)

    def prepare_response(self, request, content_type, file_name, value=None):
        value = value if value else {}
        logger.debug(u'Generating File: {0}'.format(file_name))
        logger.debug(u'Generation Context: {0}'.format(value))

        if request:
            response = request.response
            disposition = 'attachment;filename="{0}"'.format(file_name)
            response.content_disposition = disposition
            response.content_type = content_type
            response.charset = 'utf-8'


class PdfRenderer(BaseSethRenderer):
    # Requires xhtml2pdf to be installed

    def __init__(self, info):
        self.info = info

    def get_filename(self, context):
        return u"attachment-{0}.pdf".format(int(time()))

    def __call__(self, value, system):
        from xhtml2pdf import pisa

        request = system['request']
        buff = StringIO()

        if not 'template' in value and not 'html' in value:
            raise SethRendererException(u"No template nor html provided")

        if not 'html' in value:
            try:
                html = self.render_template(value['template'], value, request)
            except ValueError:
                raise SethRendererException(u"Wrong renderer factory conf")
        else:
            html = value['html']

        try:
            pdf = pisa.CreatePDF(
                StringIO(html.encode('utf-8')), buff, encoding='utf-8'
            )
        except AttributeError:
            raise SethRendererException(u"Error generating PDF file.")

        if pdf.err:
            raise SethRendererException(u"Error generating PDF file.")

        file_name = value.pop('file_name', self.get_filename(value))
        self.prepare_response(request, 'application/pdf', file_name, value)
        result = buff.getvalue()
        buff.close()
        return result


class CsvRenderer(BaseSethRenderer):

    def __init__(self, info):
        self.info = info

    def __call__(self, value, system):
        request = system['request']
        if not 'rows' in value:
            raise SethRendererException(u"No rows provided")

        buff = StringIO()
        writer = UnicodeWriter(buff, encoding='utf-8')

        if value.get('header', None):
            writer.writerow(value['header'])

        writer.writerows(value['rows'])

        file_name = value.pop('file_name', 'raport.csv')
        self.prepare_response(request, 'text/csv', file_name, value)
        result = buff.getvalue()
        buff.close()
        return result