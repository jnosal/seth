from seth.tests import UnitTestBase
from seth.tests.models import SampleModel, PredefinedModel


class ManageTestCase(UnitTestBase):

    def test_basic_manager(self):
        model = SampleModel()
        self.session.add(model)
        self.assertEqual(self.session.query(SampleModel).count(), 1)
        self.assertEqual(SampleModel.manager.count(), 1)
        self.assertEqual(SampleModel.manager.get_query().count(), 1)

        qs = self.session.query(SampleModel).filter(SampleModel.is_deleted)
        self.assertEqual(qs.count(), 0)
        self.assertEqual(SampleModel.manager.from_query(qs).count(), 0)
        self.assertEqual(SampleModel.manager.from_query(qs).clear_query().count(), 1)

    def test_predefined_manager(self):
        self.assertRaises(AttributeError, lambda: SampleModel.manager.non_existant())
        self.assertEqual(PredefinedModel.manager.non_existant(), 1)

    def test_is_deleted_query(self):
        model = SampleModel()
        self.session.add(model)
        self.session.flush()
        self.assertEqual(SampleModel.manager.count(), 1)
        model.is_deleted = True
        self.session.flush()
        self.session.refresh(model)
        self.assertEqual(SampleModel.manager.count(), 0)