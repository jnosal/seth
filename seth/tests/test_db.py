from seth.tests import UnitTestBase
from seth.tests.models import SampleModel, PredefinedModel


class ManageTestCase(UnitTestBase):

    def test_basic_manager(self):
        model = SampleModel()
        self.session.add(model)
        self.assertEqual(self.session.query(SampleModel).count(), 1)
        self.assertEqual(SampleModel.query.count(), 1)
        self.assertEqual(SampleModel.manager.query.count(), 1)

        qs = self.session.query(SampleModel).filter(SampleModel.is_deleted)
        self.assertEqual(qs.count(), 0)

    def test_predefined_manager(self):
        self.assertRaises(AttributeError, lambda: SampleModel.manager.non_existant())
        self.assertEqual(PredefinedModel.manager.non_existant(), 1)

    def test_model_to_json(self):
        self.session.add(SampleModel(int_col=1, dec_col=3))
        self.session.flush()
        inst = SampleModel.query.first()
        data = inst.to_dict()
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
        self.assertIn('id', data)
        self.assertIn('int_col', data)
        self.assertIn('dec_col', data)