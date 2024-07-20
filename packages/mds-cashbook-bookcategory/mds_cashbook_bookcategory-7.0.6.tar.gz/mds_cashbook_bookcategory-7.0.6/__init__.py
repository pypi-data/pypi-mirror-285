# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.pool import Pool
from .category import Category
from .book import CategoryCashbookRel, Cashbook
from .ir import Rule


def register():
    Pool.register(
        Category,
        Cashbook,
        CategoryCashbookRel,
        Rule,
        module='cashbook_bookcategory', type_='model')
