from seth.tests import UnitTestBase
from seth.helpers.unicodecsv import _stringify, _stringify_list,\
    _unicodify


class BaseUnicodeCsvTestCase(UnitTestBase):

    def test_unicodify(self):
        class A(object):

            def __str__(self):
                return 'd'

        a = A()

        self.assertEqual(_unicodify(None, 'utf-8'), None)
        self.assertEqual(_unicodify(u'', 'utf-8'), u'')
        self.assertEqual(_unicodify(1.0, 'utf-8'), 1.0)
        self.assertEqual(_unicodify(1, 'utf-8'), 1)
        self.assertEqual(_unicodify('d', 'utf-8'), u'd')
        self.assertEqual(_unicodify(a, 'utf-8'), a)

    def test_stringify(self):
        class A(object):

            def __str__(self):
                return 'd'

        self.assertEqual(_stringify(None, 'utf-8', 'strict'), '')
        self.assertEqual(_stringify('', 'utf-8', 'strict'), '')
        self.assertEqual(_stringify(u'', 'utf-8', 'strict'), '')
        self.assertEqual(_stringify(1.0, 'utf-8', 'strict'), 1.0)
        self.assertEqual(_stringify(1, 'utf-8', 'strict'), 1)
        self.assertEqual(_stringify(A(), 'utf-8', 'strict'), 'd')

    def test_stringify_list(self):
        self.assertRaises(Exception, lambda: _stringify_list(1, 'utf-8'))