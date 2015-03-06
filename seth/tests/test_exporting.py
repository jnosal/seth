import types

from seth.tests import UnitTestBase
from seth.tests.models import SampleModel
from seth import exporting


class ExporterTestCase(UnitTestBase):

    def test_exporter_model_is_not_defined(self):
        class SampleExporter(exporting.ExportFactory):
            model = None

        self.assertRaises(AssertionError, lambda: SampleExporter([]))

    def test_exporter_no_items(self):
        class SampleExporter(exporting.ExportFactory):
            model = SampleModel

        data = SampleExporter([]).get_export_data()
        self.assertIn('title', data)
        self.assertIn('header', data)
        self.assertIn('rows', data)
        self.assertEqual(data['title'], None)
        self.assertEqual(data['rows'], [])
        self.assertEqual(data['header'], [])

    def test_exporter_header_does_not_match_properties(self):
        class SampleExporter(exporting.ExportFactory):
            model = SampleModel
            header = ['smth']

        self.assertRaises(exporting.SethExportException, lambda: SampleExporter([]))

    def test_exporter_model_does_not_have_certain_attribute(self):
        class SampleExporter(exporting.ExportFactory):
            model = SampleModel
            header = ['smth']
            properties = [exporting.Field('smth')]

        self.assertRaises(exporting.SethExportException, lambda: SampleExporter([]))

    def test_property_is_not_instance_of_Field(self):
        class SampleExporter(exporting.ExportFactory):
            model = SampleModel
            header = ['smth']
            properties = ['int_col']

        self.assertRaises(exporting.SethExportException, lambda: SampleExporter([]))

    def test_generate_model_export_no_items(self):
        class SampleExporter(exporting.ExportFactory):
            title = 'abc'
            model = SampleModel
            header = ['smth']
            properties = [exporting.Field('int_col')]

        exporter = SampleExporter([])
        data = exporter.get_export_data()
        self.assertEqual(data['header'], ['smth'])
        self.assertEqual(data['rows'], [])
        self.assertEqual(data['title'], 'abc')

    def test_generate_model_entry_exists_from_query(self):
        SampleModel.manager.create(int_col=1)
        SampleModel.manager.create(int_col=1)

        class SampleExporter(exporting.ExportFactory):
            title = 'abc'
            model = SampleModel
            header = ['smth']
            properties = [exporting.Field('int_col')]

        exporter = SampleExporter([i for i in SampleModel.query.all()])
        data = exporter.get_export_data()
        self.assertEqual(data['header'], ['smth'])
        self.assertEqual(data['rows'], [[1], [1]])
        self.assertEqual(data['title'], 'abc')

        SampleModel.manager.create(int_col=1)

    def test_generate_model_entry_exists_from_list(self):
        SampleModel.manager.create(int_col=1)
        SampleModel.manager.create(int_col=1)

        class SampleExporter(exporting.ExportFactory):
            title = 'abc'
            model = SampleModel
            header = ['smth']
            properties = [exporting.Field('int_col')]

        exporter = SampleExporter(SampleModel.query)
        data = exporter.get_export_data()
        self.assertEqual(data['header'], ['smth'])
        self.assertEqual(data['rows'], [[1], [1]])
        self.assertEqual(data['title'], 'abc')