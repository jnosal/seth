from seth.tests import UnitTestBase
from seth.tests.models import SampleModel
from seth.paginator import PaginationException


class PaginationTestCase(UnitTestBase):

    def test_paginate_no_records_in_db(self):
        paginator = SampleModel.manager.paginate()
        self.assertEqual(paginator.has_next, False)
        self.assertEqual(paginator.has_prev, False)
        self.assertEqual(paginator.page, 1)
        self.assertEqual(paginator.prev_num, 0)
        self.assertEqual(paginator.next_num, 2)
        self.assertEqual(paginator.pages, 0)
        self.assertEqual(paginator.total, 0)

    def test_paginatore_two_records_in_db_default_settings(self):
        model1 = SampleModel()
        model2 = SampleModel()
        self.session.add(model1)
        self.session.add(model2)
        paginator = SampleModel.manager.paginate()
        self.assertEqual(paginator.has_next, False)
        self.assertEqual(paginator.has_prev, False)
        self.assertEqual(paginator.page, 1)
        self.assertEqual(paginator.prev_num, 0)
        self.assertEqual(paginator.next_num, 2)
        self.assertEqual(paginator.pages, 1)
        self.assertEqual(paginator.total, 2)

    def test_paginatore_two_records_in_db_default_two_pages(self):
        model1 = SampleModel()
        model2 = SampleModel()
        self.session.add(model1)
        self.session.add(model2)
        paginator = SampleModel.manager.paginate(page=1, per_page=1)
        self.assertEqual(paginator.has_next, True)
        self.assertEqual(paginator.has_prev, False)
        self.assertEqual(paginator.page, 1)
        self.assertEqual(paginator.prev_num, 0)
        self.assertEqual(paginator.next_num, 2)
        self.assertEqual(paginator.pages, 2)
        self.assertEqual(paginator.total, 2)
        paginator = SampleModel.manager.paginate(page=2, per_page=1)
        self.assertEqual(paginator.has_next, False)
        self.assertEqual(paginator.has_prev, True)
        self.assertEqual(paginator.page, 2)
        self.assertEqual(paginator.prev_num, 1)
        self.assertEqual(paginator.next_num, 3)
        self.assertEqual(paginator.pages, 2)
        self.assertEqual(paginator.total, 2)

    def test_pagination_raises_pagination_exception_where_page_is_zero(self):
        self.assertRaises(
            PaginationException,
            lambda: SampleModel.manager.paginate(page=0, per_page=1)
        )

    def test_pagination_raises_pagination_exception_where_page_is_lower_than_zero(self):
        self.assertRaises(
            PaginationException,
            lambda: SampleModel.manager.paginate(page=-1, per_page=1)
        )

    def test_pagination_raises_pagination_exception_where_per_page_is_lower_than_zero(self):
        self.assertRaises(
            PaginationException,
            lambda: SampleModel.manager.paginate(page=1, per_page=-1)
        )