# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelSQL, fields
from trytond.pool import PoolMeta


class Cashbook(metaclass=PoolMeta):
    __name__ = 'cashbook.book'

    categories = fields.Many2Many(
        string='Categories',
        relation_name='cashbook.bookcategory-rel',
        origin='cashbook', target='category')

# end Cashbook


class CategoryCashbookRel(ModelSQL):
    'Category Cashbook Relation'
    __name__ = 'cashbook.bookcategory-rel'

    category = fields.Many2One(
        string='Category', required=True,
        model_name='cashbook.bookcategory', ondelete='CASCADE')
    cashbook = fields.Many2One(
        string='Cashbook', required=True,
        model_name='cashbook.book', ondelete='CASCADE')

# end CategoryCashbookRel
