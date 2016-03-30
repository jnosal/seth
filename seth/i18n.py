import codecs
import json
import logging

from pyramid.paster import bootstrap

logger = logging.getLogger('seth')
DEFAULT_VARIABLE_NAME = 'translations'


class JSTranslationsHandler(object):

    def pofile_to_dict(self, stream, locale):
        from babel.messages.pofile import read_po
        catalog = read_po(stream, locale)
        messages = [m for m in catalog if m.string]
        messages[1:] = [m for m in messages[1:] if not m.fuzzy]
        messages.sort()
        return dict((message.id, message.string) for message in messages)

    def pofile_to_js(self, source, locale, variable_name=DEFAULT_VARIABLE_NAME):
        if isinstance(source, (str, unicode)):
            with open(source) as f:
                dict_ = self.pofile_to_dict(f, locale)
        else:
            dict_ = self.pofile_to_dict(source, locale)

        try:
            del dict_['']
        except KeyError:
            pass

        s = json.dumps(dict_, indent=1).replace('/', '\/')
        return "{0} = {1};\n".format(variable_name, s) if variable_name else s

    def generate_file(self, locale, source, out):
        logger.info(u"Generating json translations for {0} locale".format(locale))
        contents = self.pofile_to_js(source, locale)

        with codecs.open(out, 'w', encoding='utf-8') as writer:
            writer.write(contents)
