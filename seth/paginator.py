#!/usr/bin/python
# -*- coding: utf-8 -*-
from math import ceil


class PaginationException(Exception):
    """Basic Pagination Exception"""""


class Pagination(object):

    def __init__(self, query, page, per_page, total, items, **kwargs):
        self.query = query
        self.page = page
        self.per_page = per_page
        self.total = total
        self.items = items
        self.extra = kwargs

    def _jsonify_items(self):
        if not self.items:
            return []

        return self.items

    @property
    def pages(self):
        if self.per_page == 0:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    @property
    def prev_num(self):
        return self.page - 1

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def next_num(self):
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

    def __json__(self, request=None):
        return {
            'meta': {
                'previous': self.prev_num if self.has_prev else None,
                'next': self.next_num if self.has_next else None,
                'per_page': self.per_page,
                'total_entries': self.total,
                'page': self.page,
                'total_pages': self.pages
            },
            'items': self._jsonify_items(),
            'extra': self.extra
        }


def paginate(qs, page=1, per_page=20, **kwargs):
    if page < 1:
        raise PaginationException(u"Page has to be grater or equal 1")

    if per_page < 0:
        raise PaginationException(u"Page has to be grater than 0")

    total = int(qs.count())

    if total < (page-1) * per_page:
        page, per_page = 1, 20

    items = qs.limit(per_page).offset((page - 1) * per_page).all()

    if not items and page != 1:
        return False

    return Pagination(qs, page, per_page, total, items, **kwargs)
