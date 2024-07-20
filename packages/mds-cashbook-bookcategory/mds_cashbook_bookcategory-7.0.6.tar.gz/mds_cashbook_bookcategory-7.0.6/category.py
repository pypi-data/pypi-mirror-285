# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields, tree
from trytond.modules.cashbook.model import order_name_hierarchical
from trytond.transaction import Transaction


class Category(tree(separator=' / '), ModelSQL, ModelView):
    "Cashbook Category"
    __name__ = "cashbook.bookcategory"

    company = fields.Many2One(
        string='Company', model_name='company.company',
        required=True, ondelete="RESTRICT")
    name = fields.Char(string='Name', required=True, translate=True)

    parent = fields.Many2One(
        string='Parent',
        model_name='cashbook.bookcategory', ondelete='CASCADE')
    childs = fields.One2Many(
        string='Children', field='parent',
        model_name='cashbook.bookcategory')

    cashbooks = fields.Many2Many(
        string='Cashbooks',
        relation_name='cashbook.bookcategory-rel',
        origin='category', target='cashbook')

    @classmethod
    def __register__(cls, module_name):
        super(Category, cls).__register__(module_name)
        table = cls.__table_handler__(module_name)
        table.drop_column('left')
        table.drop_column('right')

    @classmethod
    def __setup__(cls):
        super(Category, cls).__setup__()
        cls._order.insert(0, ('rec_name', 'ASC'))

    @staticmethod
    def default_company():
        return Transaction().context.get('company') or None

    @staticmethod
    def order_rec_name(tables):
        """ order by pos
            a recursive sorting
        """
        return order_name_hierarchical('cashbook.bookcategory', tables)

# ende Category
