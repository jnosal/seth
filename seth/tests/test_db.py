from decimal import Decimal

from seth.tests import UnitTestBase
from seth.tests.models import SampleModel, PredefinedModel


class ManagerTestCase(UnitTestBase):

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

    def test_persistence_save_method(self):
        model = SampleModel()
        self.assertEqual(SampleModel.query.count(), 0)
        SampleModel.manager.save(model)
        self.assertEqual(SampleModel.query.count(), 1)

    def test_persistence_all_method(self):
        model = SampleModel()
        self.assertEqual(len(SampleModel.manager.all()), 0)
        SampleModel.manager.save(model)
        self.assertIn(model, SampleModel.manager.all())

    def test_persistence_get_method(self):
        self.assertEqual(None, SampleModel.manager.get(123123123))
        SampleModel.manager.save(SampleModel())
        model = self.session.query(SampleModel).first()
        self.assertNotEqual(None, SampleModel.manager.get(model.id))

    def test_persistence_get_all_method(self):
        self.assertEqual([], SampleModel.manager.get_all(*[1, 2]))
        SampleModel.manager.save(SampleModel())
        model = self.session.query(SampleModel).first()
        self.assertIn(model, SampleModel.manager.get_all(*[model.id]))

    def test_persistence_find_method(self):
        SampleModel.manager.save(SampleModel())
        model = self.session.query(SampleModel).first()
        self.assertIn(model, SampleModel.manager.find(id=model.id))

    def test_persistence_first_method(self):
        model = SampleModel()
        self.assertEqual(None, SampleModel.manager.first())
        SampleModel.manager.save(model)
        self.assertEqual(model, SampleModel.manager.first())

    def test_persistence_new_method(self):
        self.assertTrue(isinstance(SampleModel.manager.new(), SampleModel))

    def tet_persistence_create_method(self):
        self.assertEqual(SampleModel.query.count(), 0)
        SampleModel.manager.create(**{})
        self.assertEqual(SampleModel.query.count(), 1)

    def test_persistence_update_method(self):
        SampleModel.manager.create(**{})
        model = self.session.query(SampleModel).first()
        self.assertNotEqual(model.int_col, 66)
        self.assertNotEqual(model.dec_col, Decimal('55.0'))
        SampleModel.manager.update(model, int_col=66, dec_col=55)
        model = self.session.query(SampleModel).first()
        self.assertEqual(model.int_col, 66)
        self.assertEqual(model.dec_col, Decimal('55.0'))

    def test_persistence_delete_method(self):
        SampleModel.manager.create(**{})
        model = self.session.query(SampleModel).first()
        self.assertEqual(SampleModel.query.count(), 1)
        SampleModel.manager.delete(model)
        self.assertEqual(SampleModel.query.count(), 0)