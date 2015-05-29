from decimal import Decimal

from pyramid.httpexceptions import HTTPNotFound

from seth import db
from seth.tests import UnitTestBase
from seth.db.managers import BaseManager, SoloManager
from seth.tests.models import SampleModel, PredefinedModel


class ManagerTestCase(UnitTestBase):

    def test_assert_raises_not_initialized_exception_when_db_is_not_initialized(self):
        old_maker = db.Meta.maker
        db.Meta.maker = None
        self.assertRaises(db.SessionNotInitializedException, lambda: db.get_session())
        db.Meta.maker = old_maker

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

    def test_predefined_model_json_included(self):
        self.assertIn('sth', PredefinedModel().__json__())

    def test_predefined_model_nested_json(self):
        one = PredefinedModel()
        PredefinedModel.manager.save(one)
        one = PredefinedModel.manager.first()
        two = PredefinedModel()
        one.nested = two
        self.assertIn('nested', one.__json__())

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

    def test_persistence_get_or_404_method(self):
        self.assertRaises(HTTPNotFound, lambda: SampleModel.manager.get_or_404(id=11231))
        SampleModel.manager.create(**{})
        model = self.session.query(SampleModel).first()
        self.assertEqual(model, SampleModel.manager.get_or_404(id=model.id))

    def test_persistence_get_or_create_method(self):
        self.assertEqual(SampleModel.query.count(), 0)
        m1, created = SampleModel.manager.get_or_create(id=123123)
        self.assertEqual(SampleModel.query.count(), 1)
        self.assertEqual(created, True)
        m2, created = SampleModel.manager.get_or_create(id=123123)
        self.assertEqual(created, False)
        self.assertEqual(SampleModel.query.count(), 1)
        self.assertEqual(m1, m2)

    def test_persistence_isinstance_raises_ValueError_if_wrong_model_is_provided(self):
        model = SampleModel()

        class AnotherModelClass(object):
            pass

        dummy = AnotherModelClass()
        self.assertEqual(True, SampleModel.manager._isinstance(model))
        self.assertEqual(
            False,
            SampleModel.manager._isinstance(dummy, raise_error=False)
        )
        self.assertRaises(
            ValueError, lambda: SampleModel.manager._isinstance(dummy, raise_error=True)
        )


class IndependantManagerTestCase(UnitTestBase):

    def test_define_manager(self):
        class FancyManager(BaseManager):
            pass

        manager = FancyManager(model_class=SampleModel)
        self.assertEqual(manager.query.count(), 0)
        manager.create(**{})
        self.assertEqual(manager.query.count(), 1)


class SoloManagerTestCase(UnitTestBase):

    def test_solo_manager(self):
        manager = SoloManager(model_class=SampleModel)
        self.assertEqual(manager.query.count(), 0)
        manager.create(**{})
        self.assertEqual(manager.query.count(), 1)
        manager.create(**{})
        self.assertEqual(manager.query.count(), 1)
        self.assertNotEqual(manager.get_solo(), None)

    def test_get_solo_nothing_exist(self):
        manager = SoloManager(model_class=SampleModel)
        self.assertEqual(manager.query.count(), 0)
        self.assertNotEqual(manager.get_solo(), None)
        self.assertEqual(manager.query.count(), 1)

    def test_get_raises_ValueError_for_solo_manager(self):
        manager = SoloManager(model_class=SampleModel)
        self.assertRaises(ValueError, lambda: manager.get(id=1))