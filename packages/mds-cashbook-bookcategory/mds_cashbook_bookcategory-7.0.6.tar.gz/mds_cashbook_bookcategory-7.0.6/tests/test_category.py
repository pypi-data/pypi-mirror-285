# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.tests.test_tryton import with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.modules.cashbook.tests.test_module import CashbookTestCase


class CategoryTestCase(CashbookTestCase):
    'Test cashbook category module'
    module = 'cashbook_bookcategory'

    @with_transaction()
    def test_bookcategory_create(self):
        """ add categories
        """
        BookCategory = Pool().get('cashbook.bookcategory')

        company = self.prep_company()
        with Transaction().set_context({
                'company': company.id}):
            categories, = BookCategory.create([{
                'name': 'Cat 0',
                'childs': [('create', [{
                    'name': 'Cat 1'
                    }, {
                    'name': 'Cat 2'
                    }])],
                }])

            cat2 = BookCategory.search([])
            self.assertEqual(len(cat2), 3)
            self.assertEqual(cat2[0].rec_name, 'Cat 0')
            self.assertEqual(cat2[1].rec_name, 'Cat 0 / Cat 1')
            self.assertEqual(cat2[2].rec_name, 'Cat 0 / Cat 2')

            # delete single category
            BookCategory.delete([cat2[2]])

            # delete tree
            BookCategory.delete([cat2[0]])

    @with_transaction()
    def test_bookcategory_add_to_cashbook(self):
        """ add categories, link to cashbook
        """
        pool = Pool()
        BookCategory = pool.get('cashbook.bookcategory')
        Book = pool.get('cashbook.book')

        types = self.prep_type()
        company = self.prep_company()
        with Transaction().set_context({
                'company': company.id}):
            category, = BookCategory.create([{
                'name': 'Cat 0',
                'childs': [('create', [{
                    'name': 'Cat 1'
                    }, {
                    'name': 'Cat 2'
                    }])],
                }])

            book, = Book.create([{
                'name': 'Book 1',
                'btype': types.id,
                'currency': company.currency.id,
                'number_sequ': self.prep_sequence().id,
                'categories': [('add', [category.id])],
                }])
            self.assertEqual(book.rec_name, 'Book 1 | 0.00 usd | Open')
            self.assertEqual(len(book.categories), 1)
            self.assertEqual(book.categories[0].rec_name, 'Cat 0')

            self.assertEqual(len(category.cashbooks), 1)
            self.assertEqual(
                category.cashbooks[0].rec_name,
                'Book 1 | 0.00 usd | Open')

            # replace category
            Book.write(*[
                [book],
                {
                    'categories': [
                        ('remove', [category.id]),
                        ('add', [category.childs[0].id]),
                        ],
                }])
            self.assertEqual(len(book.categories), 1)
            self.assertEqual(book.categories[0].rec_name, 'Cat 0 / Cat 1')

            # delete all categories, this will unlink it from cashbook
            BookCategory.delete([category])

            self.assertEqual(len(book.categories), 0)

# end CategoryTestCase


del CashbookTestCase
