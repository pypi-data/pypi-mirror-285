# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from datetime import date
from decimal import Decimal
from trytond.tests.test_tryton import with_transaction, activate_module
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from trytond.i18n import gettext
from trytond.modules.cashbook_investment.tests.test_module import \
    CashbookInvestmentTestCase
from trytond.modules.cashbook_report.templates import (
    cashbook_types, category_types, booktype_types, currency_types)


class ReportTestCase(CashbookInvestmentTestCase):
    'Test cashbook book report module'
    module = 'cashbook_report'

    @classmethod
    def setUpClass(cls):
        """ add modelues
        """
        super(ReportTestCase, cls).setUpClass()
        activate_module(['dashboard', 'cashbook_investment'])

    def prep_report_3books(self):
        """ create 3x cashbooks, add bookings,
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')
        ResUser = pool.get('res.user')

        user_admin, = ResUser.search([])

        company = self.prep_company()
        type_cash = self.prep_type()
        type_bank = self.prep_type(name='Bank', short='BK')

        ResUser.write(*[
            [user_admin],
            {
                'companies': [('add', [company.id])],
                'company': company.id,
            }])
        self.assertEqual(user_admin.company.id, company.id)

        sequ_id = self.prep_sequence().id
        category = self.prep_category(cattype='in')
        (usd, euro) = self.prep_2nd_currency(company)

        party = self.prep_party()
        books = Book.create([{
            'name': 'Book 1',
            'btype': type_cash.id,
            'company': company.id,
            'currency': usd.id,
            'number_sequ': sequ_id,
            'start_date': date(2022, 4, 1),
            'lines': [('create', [{
                    'date': date(2022, 5, 5),
                    'description': 'Income 1a',
                    'bookingtype': 'in',
                    'amount': Decimal('10.0'),
                    'category': category.id,
                    'party': party.id,
                }, {
                    'date': date(2022, 5, 5),
                    'description': 'Income 1b',
                    'bookingtype': 'in',
                    'amount': Decimal('15.0'),
                    'category': category.id,
                    'party': party.id,
                }])],
            }, {
            'name': 'Book 2',
            'btype': type_cash.id,
            'company': company.id,
            'currency': usd.id,
            'number_sequ': sequ_id,
            'start_date': date(2022, 4, 1),
            'lines': [('create', [{
                    'date': date(2022, 5, 5),
                    'description': 'Income 2a',
                    'bookingtype': 'in',
                    'amount': Decimal('5.0'),
                    'category': category.id,
                    'party': party.id,
                }, {
                    'date': date(2022, 5, 5),
                    'description': 'Income 2b',
                    'bookingtype': 'in',
                    'amount': Decimal('7.5'),
                    'category': category.id,
                    'party': party.id,
                }])],
            }, {
            'name': 'Book 3',
            'btype': type_bank.id,
            'company': company.id,
            'currency': euro.id,
            'number_sequ': sequ_id,
            'start_date': date(2022, 4, 1),
            'lines': [('create', [{
                    'date': date(2022, 5, 5),
                    'description': 'Income 3a',
                    'bookingtype': 'in',
                    'amount': Decimal('12.5'),
                    'category': category.id,
                    'party': party.id,
                }, {
                    'date': date(2022, 5, 5),
                    'description': 'Income 3b',
                    'bookingtype': 'in',
                    'amount': Decimal('10.5'),
                    'category': category.id,
                    'party': party.id,
                }])],
            }])
        Line.wfcheck([line for book in books for line in book.lines])
        self.assertEqual(len(books), 3)
        self.assertEqual(books[0].name, 'Book 1')
        self.assertEqual(books[0].btype.rec_name, 'CAS - Cash')
        self.assertEqual(len(books[0].lines), 2)
        self.assertEqual(books[0].balance, Decimal('25.0'))

        self.assertEqual(books[1].name, 'Book 2')
        self.assertEqual(books[1].btype.rec_name, 'CAS - Cash')
        self.assertEqual(len(books[1].lines), 2)
        self.assertEqual(books[1].balance, Decimal('12.5'))

        self.assertEqual(books[2].name, 'Book 3')
        self.assertEqual(books[2].btype.rec_name, 'BK - Bank')
        self.assertEqual(len(books[2].lines), 2)
        self.assertEqual(books[2].balance, Decimal('23.0'))
        return books

    @with_transaction()
    def test_report_check_dtype_messages_functions(self):
        """ check access to messages and functions for 'dtypes'
        """
        Line = Pool().get('cashbook_report.eval_line')

        dtypes = []
        dtypes.extend(currency_types)
        dtypes.extend(cashbook_types)
        dtypes.extend(category_types)
        dtypes.extend(booktype_types)
        for x in dtypes:
            gettext('cashbook_report.msg_dtype_%s' % x)
            getattr(Line, 'get_value_%s' % x)

    @with_transaction()
    def test_report_currency_hasbookings(self):
        """ check detectpn of bookings @ currency
        """
        pool = Pool()
        Currency = pool.get('currency.currency')
        Lines = pool.get('cashbook.line')

        books = self.prep_report_3books()

        company = self.prep_company()
        with Transaction().set_context({
                'company': company.id}):
            self.assertEqual(len(books[0].lines), 2)
            self.assertEqual(books[0].currency.code, 'usd')
            self.assertEqual(len(books[1].lines), 2)
            self.assertEqual(books[1].currency.code, 'usd')
            self.assertEqual(len(books[2].lines), 2)
            self.assertEqual(books[2].currency.code, 'EUR')

            euro, = Currency.search([('code', '=', 'EUR')])
            self.assertEqual(euro.cashbook_hasbookings, True)
            self.assertEqual(Currency.search_count([
                ('cashbook_hasbookings', '=', True)
                ]), 2)

            Lines.wfedit(books[2].lines)
            Lines.delete(books[2].lines)
            self.assertEqual(euro.cashbook_hasbookings, False)

            self.assertEqual(Currency.search_count([
                ('cashbook_hasbookings', '=', True)
                ]), 1)

            usd, = Currency.search([('code', '=', 'usd')])
            self.assertEqual(usd.cashbook_hasbookings, True)

            Lines.wfedit(books[0].lines)
            Lines.delete(books[0].lines)
            self.assertEqual(usd.cashbook_hasbookings, True)
            Lines.wfedit(books[1].lines)
            Lines.delete(books[1].lines)
            self.assertEqual(usd.cashbook_hasbookings, False)

            self.assertEqual(Currency.search_count([
                ('cashbook_hasbookings', '=', True)
                ]), 0)

    @with_transaction()
    def test_report_check_limited_access(self):
        """ check query of cashbook-lines selected by
            cashbook-type, limited by user-permissions
        """
        pool = Pool()
        ResUser = pool.get('res.user')
        ResGroup = pool.get('res.group')
        ModelData = pool.get('ir.model.data')
        Currency = pool.get('currency.currency')
        Evaluation = pool.get('cashbook_report.evaluation')
        Type = pool.get('cashbook.type')
        Cashbook = pool.get('cashbook.book')

        books = self.prep_report_3books()
        company = self.prep_company()

        # add 2x user, set owner of cashbooks to them
        group_cashbook = ResGroup(ModelData.get_id(
            'cashbook', 'group_cashbook'))
        users = ResUser.create([{
            'name': 'User 1',
            'login': 'user1',
            'password': 'test1234',
            'groups': [('add', [group_cashbook.id])],
            'company': company.id,
            'companies': [('add', [company.id])],
            }, {
            'name': 'User 2',
            'login': 'user2',
            'password': 'test1234',
            'groups': [('add', [group_cashbook.id])],
            'company': company.id,
            'companies': [('add', [company.id])],
            }])

        Cashbook.write(*[
            [books[0], books[1]],
            {
                'owner': users[0].id,
            },
            [books[2]],
            {
                'owner': users[1].id,
            },
            ])

        # check access to data
        with Transaction().set_user(users[0].id):
            with Transaction().set_context({
                    '_check_access': True,
                    'company': company.id}):
                books_owner1 = Cashbook.search([])
                self.assertEqual(len(books_owner1), 2)
                self.assertEqual(books_owner1[0].name, 'Book 1')
                self.assertEqual(books_owner1[0].balance, Decimal('25.0'))
                self.assertEqual(books_owner1[1].name, 'Book 2')
                self.assertEqual(books_owner1[1].balance, Decimal('12.5'))

                # add category to cashbook
                Cashbook.write(*[
                    [books_owner1[0]],
                    {
                        'categories': [('create', [{
                            'name': 'Book 1, User 1'
                            }])],
                    }])

                evaluation1, = Evaluation.create([{
                    'name': 'Evaluation User 1 - Cashbooks',
                    'dtype1': 'cashbooks',
                    'cashbooks': [('add', [x.id for x in books_owner1])],
                    }])
                self.assertEqual(len(evaluation1.cashbooks), 2)
                self.assertEqual(evaluation1.currency.rec_name, 'Euro')
                self.assertEqual(len(evaluation1.line_values), 2)
                self.assertEqual(
                    evaluation1.line_values[0].name,
                    'Book 1 | 25.00 usd | Open')
                self.assertEqual(
                    evaluation1.line_values[0].value1, Decimal('23.81'))
                self.assertEqual(
                    evaluation1.line_values[1].name,
                    'Book 2 | 12.50 usd | Open')
                self.assertEqual(
                    evaluation1.line_values[1].value1, Decimal('11.9'))

                evaluation2, = Evaluation.create([{
                    'name': 'Evaluation User 1 - Types',
                    'dtype1': 'types',
                    'types': [('add', [x.id for x in Type.search([])])],
                    }])
                self.assertEqual(len(evaluation2.types), 2)
                self.assertEqual(evaluation2.currency.rec_name, 'Euro')
                self.assertEqual(len(evaluation2.line_values), 2)
                self.assertEqual(evaluation2.line_values[0].name, 'BK - Bank')
                self.assertEqual(
                    evaluation2.line_values[0].value1, Decimal('0.0'))
                self.assertEqual(evaluation2.line_values[1].name, 'CAS - Cash')
                self.assertEqual(
                    evaluation2.line_values[1].value1, Decimal('35.71'))

                evaluation3, = Evaluation.create([{
                    'name': 'Evaluation User 1 - Currencies',
                    'dtype1': 'currencies',
                    'currencies': [('add', [
                        x.id for x in Currency.search([])])],
                    }])
                self.assertEqual(len(evaluation3.currencies), 2)
                self.assertEqual(evaluation3.currency.rec_name, 'Euro')
                self.assertEqual(len(evaluation3.line_values), 2)
                self.assertEqual(evaluation3.line_values[0].name, 'Euro')
                self.assertEqual(
                    evaluation3.line_values[0].value1, Decimal('0.0'))
                self.assertEqual(evaluation3.line_values[1].name, 'usd')
                self.assertEqual(
                    evaluation3.line_values[1].value1, Decimal('35.71'))

                evaluation4, = Evaluation.create([{
                    'name': 'Evaluation User 1 - Categories',
                    'dtype1': 'categories',
                    'categories': [('add', [
                        x.id for x in books_owner1[0].categories])],
                    }])
                self.assertEqual(len(evaluation4.categories), 1)
                self.assertEqual(evaluation4.currency.rec_name, 'Euro')
                self.assertEqual(len(evaluation4.line_values), 1)
                self.assertEqual(
                    evaluation4.line_values[0].name, 'Book 1, User 1')
                self.assertEqual(
                    evaluation4.line_values[0].value1, Decimal('23.81'))

                self.assertEqual(Evaluation.search_count([]), 4)

        with Transaction().set_user(users[1].id):
            with Transaction().set_context({
                    '_check_access': True,
                    'company': company.id}):
                books_owner2 = Cashbook.search([])
                self.assertEqual(len(books_owner2), 1)
                self.assertEqual(books_owner2[0].name, 'Book 3')

                # add category to cashbook
                Cashbook.write(*[
                    [books_owner2[0]],
                    {
                        'categories': [('create', [{
                            'name': 'Book 3, User 2'
                            }])],
                    }])

                evaluation1, = Evaluation.create([{
                    'name': 'Evaluation User 2 - Cashbooks',
                    'dtype1': 'cashbooks',
                    'cashbooks': [('add', [x.id for x in books_owner2])],
                    }])
                self.assertEqual(len(evaluation1.cashbooks), 1)
                self.assertEqual(evaluation1.currency.rec_name, 'Euro')
                self.assertEqual(len(evaluation1.line_values), 1)
                self.assertEqual(
                    evaluation1.line_values[0].name, 'Book 3 | 23.00 € | Open')
                self.assertEqual(
                    evaluation1.line_values[0].value1, Decimal('23.0'))

                evaluation2, = Evaluation.create([{
                    'name': 'Evaluation User 2 - Types',
                    'dtype1': 'types',
                    'types': [('add', [x.id for x in Type.search([])])],
                    }])
                self.assertEqual(len(evaluation2.types), 2)
                self.assertEqual(evaluation2.currency.rec_name, 'Euro')
                self.assertEqual(len(evaluation2.line_values), 2)
                self.assertEqual(evaluation2.line_values[0].name, 'BK - Bank')
                self.assertEqual(
                    evaluation2.line_values[0].value1, Decimal('23.0'))
                self.assertEqual(evaluation2.line_values[1].name, 'CAS - Cash')
                self.assertEqual(
                    evaluation2.line_values[1].value1, Decimal('0.0'))

                evaluation3, = Evaluation.create([{
                    'name': 'Evaluation User 2 - Currencies',
                    'dtype1': 'currencies',
                    'currencies': [('add', [
                        x.id for x in Currency.search([])])],
                    }])
                self.assertEqual(len(evaluation3.currencies), 2)
                self.assertEqual(evaluation3.currency.rec_name, 'Euro')
                self.assertEqual(len(evaluation3.line_values), 2)
                self.assertEqual(evaluation3.line_values[0].name, 'Euro')
                self.assertEqual(
                    evaluation3.line_values[0].value1, Decimal('23.0'))
                self.assertEqual(evaluation3.line_values[1].name, 'usd')
                self.assertEqual(
                    evaluation3.line_values[1].value1, Decimal('0.0'))

                evaluation4, = Evaluation.create([{
                    'name': 'Evaluation User 2 - Categories',
                    'dtype1': 'categories',
                    'categories': [('add', [
                        x.id for x in books_owner2[0].categories])],
                    }])
                self.assertEqual(len(evaluation4.categories), 1)
                self.assertEqual(evaluation4.currency.rec_name, 'Euro')
                self.assertEqual(len(evaluation4.line_values), 1)
                self.assertEqual(
                    evaluation4.line_values[0].name, 'Book 3, User 2')
                self.assertEqual(
                    evaluation4.line_values[0].value1, Decimal('23.0'))

                self.assertEqual(Evaluation.search_count([]), 4)

        # outside of context
        # we should have access to all 8 evaluations
        evaluations = Evaluation.search([], order=[('name', 'ASC')])
        self.assertEqual(len(evaluations), 8)

        self.assertEqual(evaluations[0].name, 'Evaluation User 1 - Cashbooks')
        self.assertEqual(len(evaluations[0].cashbooks), 2)
        self.assertEqual(evaluations[0].currency.rec_name, 'Euro')
        self.assertEqual(len(evaluations[0].line_values), 2)
        self.assertEqual(
            evaluations[0].line_values[0].name, 'Book 1 | 25.00 usd | Open')
        self.assertEqual(
            evaluations[0].line_values[0].value1, Decimal('23.81'))
        self.assertEqual(
            evaluations[0].line_values[1].name, 'Book 2 | 12.50 usd | Open')
        self.assertEqual(
            evaluations[0].line_values[1].value1, Decimal('11.9'))

        self.assertEqual(evaluations[1].name, 'Evaluation User 1 - Categories')
        self.assertEqual(len(evaluations[1].categories), 1)
        self.assertEqual(evaluations[1].currency.rec_name, 'Euro')
        self.assertEqual(len(evaluations[1].line_values), 1)
        self.assertEqual(evaluations[1].line_values[0].name, 'Book 1, User 1')
        self.assertEqual(
            evaluations[1].line_values[0].value1, Decimal('23.81'))

        self.assertEqual(evaluations[2].name, 'Evaluation User 1 - Currencies')
        self.assertEqual(len(evaluations[2].currencies), 2)
        self.assertEqual(evaluations[2].currency.rec_name, 'Euro')
        self.assertEqual(len(evaluations[2].line_values), 2)
        self.assertEqual(evaluations[2].line_values[0].name, 'Euro')
        self.assertEqual(
            evaluations[2].line_values[0].value1, Decimal('23.0'))
        self.assertEqual(evaluations[2].line_values[1].name, 'usd')
        self.assertEqual(
            evaluations[2].line_values[1].value1, Decimal('35.71'))

        self.assertEqual(evaluations[3].name, 'Evaluation User 1 - Types')
        self.assertEqual(len(evaluations[3].types), 2)
        self.assertEqual(evaluations[3].currency.rec_name, 'Euro')
        self.assertEqual(len(evaluations[3].line_values), 2)
        self.assertEqual(evaluations[3].line_values[0].name, 'BK - Bank')
        self.assertEqual(
            evaluations[3].line_values[0].value1, Decimal('23.0'))
        self.assertEqual(evaluations[3].line_values[1].name, 'CAS - Cash')
        self.assertEqual(
            evaluations[3].line_values[1].value1, Decimal('35.71'))

        self.assertEqual(evaluations[4].name, 'Evaluation User 2 - Cashbooks')
        self.assertEqual(len(evaluations[4].cashbooks), 1)
        self.assertEqual(evaluations[4].currency.rec_name, 'Euro')
        self.assertEqual(len(evaluations[4].line_values), 1)
        self.assertEqual(
            evaluations[4].line_values[0].name, 'Book 3 | 23.00 € | Open')
        self.assertEqual(
            evaluations[4].line_values[0].value1, Decimal('23.0'))

        self.assertEqual(evaluations[5].name, 'Evaluation User 2 - Categories')
        self.assertEqual(len(evaluations[5].categories), 1)
        self.assertEqual(evaluations[5].currency.rec_name, 'Euro')
        self.assertEqual(len(evaluations[5].line_values), 1)
        self.assertEqual(evaluations[5].line_values[0].name, 'Book 3, User 2')
        self.assertEqual(
            evaluations[5].line_values[0].value1, Decimal('23.0'))

        self.assertEqual(evaluations[6].name, 'Evaluation User 2 - Currencies')
        self.assertEqual(len(evaluations[6].currencies), 2)
        self.assertEqual(evaluations[6].currency.rec_name, 'Euro')
        self.assertEqual(len(evaluations[6].line_values), 2)
        self.assertEqual(evaluations[6].line_values[0].name, 'Euro')
        self.assertEqual(
            evaluations[6].line_values[0].value1, Decimal('23.0'))
        self.assertEqual(evaluations[6].line_values[1].name, 'usd')
        self.assertEqual(
            evaluations[6].line_values[1].value1, Decimal('35.71'))

        self.assertEqual(evaluations[7].name, 'Evaluation User 2 - Types')
        self.assertEqual(len(evaluations[7].types), 2)
        self.assertEqual(evaluations[7].currency.rec_name, 'Euro')
        self.assertEqual(len(evaluations[7].line_values), 2)
        self.assertEqual(evaluations[7].line_values[0].name, 'BK - Bank')
        self.assertEqual(
            evaluations[7].line_values[0].value1, Decimal('23.0'))
        self.assertEqual(evaluations[7].line_values[1].name, 'CAS - Cash')
        self.assertEqual(
            evaluations[7].line_values[1].value1, Decimal('35.71'))

    @with_transaction()
    def test_report_check_allowed_dtypes(self):
        """ check allowed dtypes for dtype2...5 in depency of value in dtype
        """
        pool = Pool()
        Evaluation = pool.get('cashbook_report.evaluation')

        self.prep_report_3books()

        company = self.prep_company()
        with Transaction().set_context({
                'company': company.id}):
            evaluation, = Evaluation.create([{
                'name': 'Evaluation 1',
                'dtype1': 'cashbooks',
                }])
            self.assertEqual(len(evaluation.cashbooks), 0)
            self.assertEqual([
                x[0] for x in evaluation.get_sel_etype2()], [
                '', 'cashbooks', 'cashbooks_gldiff', 'cashbooks_glperc',
                'cashbooks_glvalue', 'cashbooks_glyield'])
            self.assertRaisesRegex(
                UserError,
                'The value "types" for field "Data type 2" in ' +
                '"Evaluation 1" of "Evaluation" is not one of the ' +
                'allowed options.',
                Evaluation.write,
                *[
                    [evaluation],
                    {
                        'dtype2': 'types',
                    }
                ])

            self.assertRaisesRegex(
                UserError,
                "The pie display cannot be used by multiple data sources" +
                " in the evaluation 'Evaluation 1'.",
                Evaluation.write,
                *[[evaluation], {'dtype2': 'cashbooks_glyield'}])

            Evaluation.write(*[
                [evaluation],
                {
                    'chart': 'line',
                    'dtype2': 'cashbooks_glyield',
                    'dtype3': 'cashbooks_glvalue',
                }])
            self.assertEqual(evaluation.dtype1, 'cashbooks')
            self.assertEqual(evaluation.dtype2, 'cashbooks_glyield')
            self.assertEqual(evaluation.dtype3, 'cashbooks_glvalue')

            # run on-cchange
            evaluation.dtype1 = 'types'
            evaluation.on_change_dtype1()
            evaluation.save()
            self.assertEqual(evaluation.dtype1, 'types')
            self.assertEqual(evaluation.dtype2, None)
            self.assertEqual(evaluation.dtype3, None)

            Evaluation.write(*[
                [evaluation],
                {
                    'dtype1': 'categories_gldiff',
                }])
            self.assertEqual([
                x[0] for x in evaluation.get_sel_etype2()], [
                '', 'categories', 'categories_gldiff', 'categories_glvalue',
                'categories_glperc', 'categories_glyield'])

            Evaluation.write(*[
                [evaluation],
                {
                    'dtype1': 'currencies',
                }])
            self.assertEqual([
                x[0] for x in evaluation.get_sel_etype2()], [
                '', 'currencies'])

            Evaluation.write(*[
                [evaluation],
                {
                    'dtype1': 'types_glperc',
                }])
            self.assertEqual([
                x[0] for x in evaluation.get_sel_etype2()], [
                '', 'types', 'types_gldiff', 'types_glvalue',
                'types_glperc', 'types_glyield'])

    @with_transaction()
    def test_report_update_name_of_line(self):
        """ check replace rec_name-value on line with
            manually  updates value
        """
        pool = Pool()
        Evaluation = pool.get('cashbook_report.evaluation')
        Line = pool.get('cashbook_report.eval_line')

        books = self.prep_report_3books()

        company = self.prep_company()
        with Transaction().set_context({
                'company': company.id}):
            evaluation, = Evaluation.create([{
                'name': 'Evaluation 1',
                'dtype1': 'cashbooks',
                'cashbooks': [('add', [x.id for x in books])],
                }])
            self.assertEqual(len(evaluation.cashbooks), 3)
            self.assertEqual(len(evaluation.line_values), 3)

            self.assertEqual(
                evaluation.line_values[0].name,
                'Book 1 | 25.00 usd | Open')
            self.assertEqual(evaluation.line_values[0].name_line, None)

            # update 'name'
            Line.write(*[
                [evaluation.line_values[0]],
                {
                    'name': 'Book updated',
                }])
            self.assertEqual(
                evaluation.line_values[0].name,
                'Book updated')
            self.assertEqual(
                evaluation.line_values[0].name_line,
                'Book updated')

            # delete 'name' value to reset to origin
            Line.write(*[
                [evaluation.line_values[0]],
                {
                    'name': None,
                }])
            self.assertEqual(
                evaluation.line_values[0].name,
                'Book 1 | 25.00 usd | Open')
            self.assertEqual(evaluation.line_values[0].name_line, None)

    @with_transaction()
    def test_report_dtype_update(self):
        """ check unlink of cashbooks/types/currencies
        """
        pool = Pool()
        Evaluation = pool.get('cashbook_report.evaluation')
        Types = pool.get('cashbook.type')
        Currency = pool.get('currency.currency')
        Category = pool.get('cashbook.bookcategory')

        books = self.prep_report_3books()

        company = self.prep_company()
        with Transaction().set_context({
                'company': company.id}):

            Category.create([{
                    'name': 'Cat 1',
                }, {
                    'name': 'Cat 2',
                }, {
                    'name': 'Cat 3',
                }])

            # valid
            evaluation, = Evaluation.create([{
                'name': 'Evaluation 1',
                'dtype1': 'cashbooks',
                'cashbooks': [('add', [x.id for x in books])],
                }])
            self.assertEqual(len(evaluation.cashbooks), 3)
            self.assertEqual(len(evaluation.types), 0)
            self.assertEqual(len(evaluation.currencies), 0)
            self.assertEqual(len(evaluation.categories), 0)

            # investment - profit/loss amount
            if 'cashbooks_gldiff' in [
                    x[0] for x in Evaluation.get_sel_etype()]:
                # no change if switch between cashbook-types
                Evaluation.write(*[
                    [evaluation],
                    {
                        'dtype1': 'cashbooks_gldiff',
                    }])
                self.assertEqual(len(evaluation.cashbooks), 3)
                self.assertEqual(len(evaluation.types), 0)
                self.assertEqual(len(evaluation.currencies), 0)
                self.assertEqual(len(evaluation.categories), 0)

                Evaluation.write(*[
                    [evaluation],
                    {
                        'dtype1': 'cashbooks_glperc',
                    }])
                self.assertEqual(len(evaluation.cashbooks), 3)
                self.assertEqual(len(evaluation.types), 0)
                self.assertEqual(len(evaluation.currencies), 0)
                self.assertEqual(len(evaluation.categories), 0)
            else:
                print('\n--== Module "cashbook_investment" not installed ==--')

            Evaluation.write(*[
                [evaluation],
                {
                    'dtype1': 'types',
                    'types': [('add', [x.id for x in Types.search([])])],
                }])
            self.assertEqual(len(evaluation.cashbooks), 0)
            self.assertEqual(len(evaluation.types), 2)
            self.assertEqual(len(evaluation.currencies), 0)
            self.assertEqual(len(evaluation.categories), 0)

            # write same dtype again - no change
            Evaluation.write(*[
                [evaluation],
                {
                    'dtype1': 'types',
                }])
            self.assertEqual(len(evaluation.cashbooks), 0)
            self.assertEqual(len(evaluation.types), 2)
            self.assertEqual(len(evaluation.currencies), 0)
            self.assertEqual(len(evaluation.categories), 0)

            Evaluation.write(*[
                [evaluation],
                {
                    'dtype1': 'currencies',
                    'currencies': [('add', [
                        x.id for x in Currency.search([])])],
                }])
            self.assertEqual(len(evaluation.cashbooks), 0)
            self.assertEqual(len(evaluation.types), 0)
            self.assertEqual(len(evaluation.currencies), 2)
            self.assertEqual(len(evaluation.categories), 0)

            Evaluation.write(*[
                [evaluation],
                {
                    'dtype1': 'categories',
                    'categories': [('add', [
                        x.id for x in Category.search([])])],
                }])
            self.assertEqual(len(evaluation.cashbooks), 0)
            self.assertEqual(len(evaluation.types), 0)
            self.assertEqual(len(evaluation.currencies), 0)
            self.assertEqual(len(evaluation.categories), 3)

            Evaluation.write(*[
                [evaluation],
                {
                    'dtype1': 'cashbooks',
                }])
            self.assertEqual(len(evaluation.cashbooks), 0)
            self.assertEqual(len(evaluation.types), 0)
            self.assertEqual(len(evaluation.currencies), 0)
            self.assertEqual(len(evaluation.categories), 0)

    @with_transaction()
    def test_report_dtype_validation(self):
        """ check validation of dtype
        """
        pool = Pool()
        Evaluation = pool.get('cashbook_report.evaluation')
        Types = pool.get('cashbook.type')

        books = self.prep_report_3books()

        company = self.prep_company()
        with Transaction().set_context({
                'company': company.id}):
            # valid
            evaluation, = Evaluation.create([{
                'name': 'Evaluation 1',
                'dtype1': 'cashbooks',
                'cashbooks': [('add', [x.id for x in books])],
                }])

            # must fail
            self.assertRaisesRegex(
                UserError,
                'A value is required for field "Data type" in "None" ' +
                'of "Evaluation Line Relation".',
                Evaluation.create,
                [{
                    'name': 'Evaluation 1',
                    'dtype1': 'types',   # wrong dtype
                    'cashbooks': [('add', [x.id for x in books])],
                }])

            evaluation, = Evaluation.create([{
                'name': 'Evaluation 2',
                'dtype1': 'types',
                'types': [('add', [x.id for x in Types.search([])])],
                }])

            # must fail
            self.assertRaisesRegex(
                UserError,
                'A value is required for field "Cashbook" in "None" ' +
                'of "Evaluation Line Relation".',
                Evaluation.create,
                [{
                    'name': 'Evaluation 3',
                    'dtype1': 'cashbooks',
                    'types': [('add', [x.id for x in Types.search([])])],
                }])

    @with_transaction()
    def test_report_check_update_of_actionviews(self):
        """ create 3x cashbooks, add evaluation, check created
            form + actionview
        """
        pool = Pool()
        Evaluation = pool.get('cashbook_report.evaluation')
        DashboardAction = pool.get('dashboard.action')

        books = self.prep_report_3books()

        company = self.prep_company()
        with Transaction().set_context({
                'company': company.id}):
            evaluation, = Evaluation.create([{
                'name': 'Evaluation 1',
                'cashbooks': [('add', [x.id for x in books])],
                }])

            # add dashboard-action
            dbaction, = DashboardAction.create([{
                'user': Transaction().user,
                'act_window': evaluation.dashb_actwin.id,
                }])
            self.assertEqual(dbaction.user.rec_name, 'Administrator')
            self.assertEqual(dbaction.act_window.name, 'Evaluation 1')

            self.assertEqual(evaluation.dtype1, 'cashbooks')
            self.assertEqual(evaluation.chart, 'pie')
            self.assertEqual(evaluation.legend, True)
            self.assertEqual(evaluation.maincolor, 'default')
            self.assertEqual(evaluation.bgcolor, '#ffffc0')
            self.assertEqual(evaluation.currency.code, 'EUR')

            # check uiview
            self.assertEqual(
                evaluation.ui_view_chart.model,
                'cashbook_report.eval_line')
            self.assertEqual(
                evaluation.ui_view_chart.module,
                'cashbook_report')
            self.assertEqual(evaluation.ui_view_chart.priority, 10)
            self.assertEqual(evaluation.ui_view_chart.type, 'graph')
            # action-window for dashbord
            self.assertEqual(evaluation.dashb_actwin.name, 'Evaluation 1')
            self.assertEqual(
                evaluation.dashb_actwin.res_model,
                'cashbook_report.eval_line')
            self.assertEqual(
                evaluation.dashb_actwin.usage,
                'dashboard')
            self.assertEqual(evaluation.dashb_actwin.domain, None)
            self.assertEqual(
                evaluation.dashb_actwin.context_domain,
                '[["evaluation", "=", %d]]' % evaluation.id)
            # action-view
            self.assertEqual(evaluation.dashb_actview.sequence, 10)
            self.assertEqual(
                evaluation.dashb_actview.view.id,
                evaluation.ui_view_chart.id)
            self.assertEqual(
                evaluation.dashb_actview.act_window.id,
                evaluation.dashb_actwin.id)

            # update evaluation, this wil re-create the view/act-window
            # and update the dashboard-view, without removing it
            old_win_id = evaluation.dashb_actwin.id
            Evaluation.write(*[
                [evaluation],
                {
                    'name': 'Evaluation 1a',
                }])
            self.assertTrue(old_win_id != evaluation.dashb_actwin.id)
            self.assertEqual(DashboardAction.search_count([]), 1)

    @with_transaction()
    def test_report_cashbook_yield(self):
        """ create 3x cashbooks, add bookings, rates
            create yield-reports
        """
        pool = Pool()
        Evaluation = pool.get('cashbook_report.evaluation')
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')
        BType = pool.get('cashbook.type')
        Asset = pool.get('investment.asset')
        CbCategory = pool.get('cashbook.bookcategory')

        company = self.prep_company()
        with Transaction().set_context({
                'company': company.id}):
            asset_cfg = self.prep_yield_config(
                fee='Fee',
                dividend='Dividend',
                gainloss='Gain-Loss',
                company=company)

            cb_cat, = CbCategory.create([{'name': 'CB Category'}])
            category_in = self.prep_category(cattype='in')
            type_depot = self.prep_type('Depot', 'D')
            BType.write(*[
                [type_depot],
                {
                    'feature': 'asset',
                }])
            asset = self.prep_asset_item(
                company=company,
                product=self.prep_asset_product(name='Product 1'))
            self.assertEqual(asset.symbol, 'usd/u')

            Asset.write(*[
                [asset],
                {
                    'rates': [('create', [{
                        'date': date(2022, 5, 1),
                        'rate': Decimal('102.0'),
                        }, {
                        'date': date(2022, 5, 2),
                        'rate': Decimal('105.5'),
                        }])],
                }])
            self.assertEqual(
                asset.rec_name,
                'Product 1 | 105.5000 usd/u | 05/02/2022')

            book_asset, = Book.create([{
                'name': 'Depot',
                'btype': type_depot.id,
                'company': company.id,
                'currency': company.currency.id,
                'number_sequ': self.prep_sequence().id,
                'asset': asset.id,
                'quantity_uom': asset.uom.id,
                'categories': [('add', [cb_cat.id])],
                'start_date': date(2022, 5, 1),
                'lines': [('create', [{
                    'bookingtype': 'in',
                    'date': date(2022, 5, 2),
                    'amount': Decimal('100.0'),
                    'quantity': Decimal('1.0'),
                    'category': category_in.id,
                    'description': 'Init',
                    }, {
                    'bookingtype': 'in',
                    'date': date(2022, 5, 3),
                    'amount': Decimal('5.0'),
                    'quantity': Decimal('0.0'),
                    'category': asset_cfg.dividend_category.id,
                    'description': 'Dividend',
                    }, {
                    'bookingtype': 'out',
                    'date': date(2022, 5, 4),
                    'amount': Decimal('2.0'),
                    'quantity': Decimal('0.0'),
                    'category': asset_cfg.fee_category.id,
                    'description': 'Fee',
                    }, {
                    'bookingtype': 'mvin',
                    'date': date(2022, 5, 5),
                    'amount': Decimal('15.0'),
                    'quantity': Decimal('0.0'),
                    'booktransf': asset_cfg.gainloss_book.id,
                    'description': 'Gain',
                    }])],
                }])
            Line.wfcheck(book_asset.lines)
            self.prep_valstore_run_worker()

            self.assertEqual(
                book_asset.rec_name,
                'Depot | 118.00 usd | Open | 1.0000 u')
            self.assertEqual(book_asset.balance, Decimal('118.0'))
            self.assertEqual(book_asset.current_value, Decimal('105.5'))
            self.assertEqual(book_asset.diff_amount, Decimal('-14.5'))
            self.assertEqual(book_asset.yield_dividend_total, Decimal('5.0'))
            self.assertEqual(book_asset.yield_fee_total, Decimal('2.0'))
            self.assertEqual(book_asset.yield_sales, Decimal('15.0'))
            self.assertEqual(book_asset.yield_balance, Decimal('5.5'))

            # evaluation: cashbooks - total yield
            evaluation1, = Evaluation.create([{
                'name': 'Evaluation 1',
                'dtype1': 'cashbooks_glyield',
                'chart': 'hbar',
                'cashbooks': [('add', [book_asset.id])],
                }])
            self.assertEqual(evaluation1.dtype1, 'cashbooks_glyield')
            self.assertEqual(evaluation1.currency.code, 'usd')
            self.assertEqual(len(evaluation1.line_values), 1)
            self.assertEqual(
                evaluation1.line_values[0].value1, Decimal('5.5'))

            # evaluation: categories - total yield
            evaluation2, = Evaluation.create([{
                'name': 'Evaluation 2',
                'dtype1': 'categories_glyield',
                'chart': 'hbar',
                'categories': [('add', [book_asset.categories[0].id])],
                }])
            self.assertEqual(evaluation2.dtype1, 'categories_glyield')
            self.assertEqual(evaluation2.currency.code, 'usd')
            self.assertEqual(len(evaluation2.line_values), 1)
            self.assertEqual(
                evaluation2.line_values[0].value1, Decimal('5.5'))

            # evaluation: types - total yield
            evaluation3, = Evaluation.create([{
                'name': 'Evaluation 3',
                'dtype1': 'types_glyield',
                'chart': 'hbar',
                'types': [('add', [book_asset.btype.id])],
                }])
            self.assertEqual(evaluation3.dtype1, 'types_glyield')
            self.assertEqual(evaluation3.currency.code, 'usd')
            self.assertEqual(len(evaluation3.line_values), 1)
            self.assertEqual(
                evaluation3.line_values[0].value1, Decimal('5.5'))

    @with_transaction()
    def test_report_chart_hbar_book_investment(self):
        """ create 3x cashbooks, add bookings, rates
            create report with cashbooks, check
        """
        pool = Pool()
        Evaluation = pool.get('cashbook_report.evaluation')
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')

        company = self.prep_company()
        with Transaction().set_context({
                'company': company.id}):
            AccType = pool.get('cashbook.type')
            Asset = pool.get('investment.asset')
            Product = pool.get('product.template')
            Uom = pool.get('product.uom')
            CbCategory = pool.get('cashbook.bookcategory')

            at, = AccType.create([{
                'name': 'depot',
                'short': 'D',
                'feature': 'asset',
                'company': company.id,
                }])

            prod_templ, = Product.create([{
                'name': 'Aurum',
                'type': 'assets',
                'list_price': Decimal('1.0'),
                'default_uom': Uom.search([('symbol', '=', 'u')])[0].id,
                'products': [('create', [{
                    'description': 'Au',
                    }])],
                }])

            asset, = Asset.create([{
                'company': company.id,
                'product': prod_templ.products[0].id,
                'currency': company.currency.id,
                'currency_digits': 4,
                'uom': prod_templ.default_uom.id,
                'rates': [('create', [{
                    'date': date(2022, 5, 1),
                    'rate': Decimal('1750.0'),
                    }, ])],
                }])
            self.assertEqual(
                asset.rec_name,
                'Aurum | 1,750.0000 usd/u | 05/01/2022')

            books = self.prep_report_3books()
            self.assertEqual(books[0].rec_name, 'Book 1 | 25.00 usd | Open')
            self.assertEqual(books[1].rec_name, 'Book 2 | 12.50 usd | Open')
            self.assertEqual(books[2].rec_name, 'Book 3 | 23.00 € | Open')

            cb_cat, = CbCategory.create([{'name': 'CB Category'}])
            Line.wfedit([line for book in books for line in book.lines])
            Book.write(*[
                books,
                {
                    'btype': at.id,
                    'asset': asset.id,
                    'categories': [('add', [cb_cat.id])],
                    'quantity_uom': asset.uom.id,
                    'quantity_digits': 3,
                },
            ])
            Line.write(*[
                [books[0].lines[0]],    # usd
                {'quantity': Decimal('2.0'), 'amount': Decimal('3000.0')},
                [books[0].lines[1]],
                {'quantity': Decimal('2.0'), 'amount': Decimal('3100.0')},
                [books[1].lines[0]],    # usd
                {'quantity': Decimal('2.0'), 'amount': Decimal('3200.0')},
                [books[1].lines[1]],
                {'quantity': Decimal('2.0'), 'amount': Decimal('3300.0')},
                [books[2].lines[0]],    # euro
                {'quantity': Decimal('2.0'), 'amount': Decimal('3300.0')},
                [books[2].lines[1]],
                {'quantity': Decimal('2.0'), 'amount': Decimal('3400.0')},
            ])
            self.prep_valstore_run_worker()

            self.assertEqual(
                books[0].rec_name,
                'Book 1 | 6,100.00 usd | Open | 4.000 u')
            self.assertEqual(books[0].current_value, Decimal('7000.0'))
            self.assertEqual(books[0].diff_amount, Decimal('900.0'))
            self.assertEqual(books[0].diff_percent, Decimal('14.75'))

            self.assertEqual(
                books[1].rec_name,
                'Book 2 | 6,500.00 usd | Open | 4.000 u')
            self.assertEqual(books[1].current_value, Decimal('7000.0'))
            self.assertEqual(books[1].diff_amount, Decimal('500.0'))
            self.assertEqual(books[1].diff_percent, Decimal('7.69'))

            self.assertEqual(
                books[2].rec_name,
                'Book 3 | 6,700.00 € | Open | 4.000 u')
            self.assertEqual(books[2].current_value, Decimal('6666.67'))
            self.assertEqual(books[2].diff_amount, Decimal('-33.33'))
            self.assertEqual(books[2].diff_percent, Decimal('-0.5'))

            # evaluation: amount-difference
            evaluation, = Evaluation.create([{
                'name': 'Evaluation 1',
                'dtype1': 'cashbooks_gldiff',
                'dtype2': 'cashbooks_glvalue',
                'dtype3': 'cashbooks_glyield',
                'dtype4': 'cashbooks_glperc',
                'dtype5': 'cashbooks',
                'chart': 'hbar',
                'cashbooks': [('add', [x.id for x in books])],
                }])
            self.assertEqual(evaluation.dtype1, 'cashbooks_gldiff')
            self.assertEqual(evaluation.dtype2, 'cashbooks_glvalue')
            self.assertEqual(evaluation.dtype3, 'cashbooks_glyield')
            self.assertEqual(evaluation.dtype4, 'cashbooks_glperc')
            self.assertEqual(evaluation.dtype5, 'cashbooks')
            self.assertEqual(evaluation.chart, 'hbar')
            self.assertEqual(evaluation.legend, True)
            self.assertEqual(evaluation.maincolor, 'default')
            self.assertEqual(evaluation.bgcolor, '#ffffc0')
            self.assertEqual(evaluation.currency.code, 'EUR')

            self.assertEqual(
                evaluation.line_values[0].value1, Decimal('857.14'))
            self.assertEqual(
                evaluation.line_values[0].value2, Decimal('6666.67'))
            self.assertEqual(
                evaluation.line_values[0].value3, Decimal('6666.67'))
            self.assertEqual(
                evaluation.line_values[0].value4, Decimal('14.75'))
            self.assertEqual(
                evaluation.line_values[0].value5, Decimal('5809.52'))

            self.assertEqual(
                evaluation.line_values[1].value1, Decimal('476.19'))
            self.assertEqual(
                evaluation.line_values[1].value2, Decimal('6666.67'))
            self.assertEqual(
                evaluation.line_values[1].value3, Decimal('6666.67'))
            self.assertEqual(
                evaluation.line_values[1].value4, Decimal('7.69'))
            self.assertEqual(
                evaluation.line_values[1].value5, Decimal('6190.48'))

            self.assertEqual(
                evaluation.line_values[2].value1, Decimal('-33.33'))
            self.assertEqual(
                evaluation.line_values[2].value2, Decimal('6666.67'))
            self.assertEqual(
                evaluation.line_values[2].value3, Decimal('6666.67'))
            self.assertEqual(
                evaluation.line_values[2].value4, Decimal('-0.50'))
            self.assertEqual(
                evaluation.line_values[2].value5, Decimal('6700.00'))

            # evaluation: percent-difference
            evaluation2, = Evaluation.create([{
                'name': 'Evaluation 2',
                'dtype1': 'cashbooks_glperc',
                'chart': 'hbar',
                'cashbooks': [('add', [x.id for x in books])],
                }])
            self.assertEqual(evaluation2.dtype1, 'cashbooks_glperc')
            self.assertEqual(evaluation2.dtype2, None)
            self.assertEqual(evaluation2.dtype3, None)
            self.assertEqual(evaluation2.dtype4, None)
            self.assertEqual(evaluation2.dtype5, None)

            self.assertEqual(evaluation2.chart, 'hbar')
            self.assertEqual(evaluation2.legend, True)
            self.assertEqual(evaluation2.maincolor, 'default')
            self.assertEqual(evaluation2.bgcolor, '#ffffc0')
            self.assertEqual(evaluation2.currency.code, 'EUR')

            self.assertEqual(
                evaluation2.line_values[0].value1, Decimal('14.75'))
            self.assertEqual(
                evaluation2.line_values[1].value1, Decimal('7.69'))
            self.assertEqual(
                evaluation2.line_values[2].value1, Decimal('-0.5'))

            # evaluation: percent-difference
            evaluation3, = Evaluation.create([{
                'name': 'Evaluation 3',
                'dtype1': 'cashbooks_glvalue',
                'chart': 'hbar',
                'cashbooks': [('add', [x.id for x in books])],
                }])
            self.assertEqual(evaluation3.dtype1, 'cashbooks_glvalue')
            self.assertEqual(evaluation3.chart, 'hbar')
            self.assertEqual(evaluation3.legend, True)
            self.assertEqual(evaluation3.maincolor, 'default')
            self.assertEqual(evaluation3.bgcolor, '#ffffc0')
            self.assertEqual(evaluation3.currency.code, 'EUR')

            self.assertEqual(
                evaluation3.line_values[0].value1, Decimal('6666.67'))
            self.assertEqual(
                evaluation3.line_values[1].value1, Decimal('6666.67'))
            self.assertEqual(
                evaluation3.line_values[2].value1, Decimal('6666.67'))

            # evaluation: category-current value
            evaluation4, = Evaluation.create([{
                'name': 'Evaluation 4',
                'dtype1': 'categories_glvalue',
                'chart': 'hbar',
                'categories': [('add', [cb_cat.id])],
                }])
            self.assertEqual(evaluation4.dtype1, 'categories_glvalue')
            self.assertEqual(evaluation4.chart, 'hbar')
            self.assertEqual(evaluation4.legend, True)
            self.assertEqual(evaluation4.maincolor, 'default')
            self.assertEqual(evaluation4.bgcolor, '#ffffc0')
            self.assertEqual(evaluation4.currency.code, 'EUR')

            self.assertEqual(len(evaluation4.line_values), 1)
            self.assertEqual(
                evaluation4.line_values[0].value1, Decimal('20000.01'))

            # evaluation: category- difference amount
            evaluation5, = Evaluation.create([{
                'name': 'Evaluation 5',
                'dtype1': 'categories_gldiff',
                'chart': 'hbar',
                'categories': [('add', [cb_cat.id])],
                }])
            self.assertEqual(evaluation5.dtype1, 'categories_gldiff')
            self.assertEqual(evaluation5.chart, 'hbar')
            self.assertEqual(evaluation5.legend, True)
            self.assertEqual(evaluation5.maincolor, 'default')
            self.assertEqual(evaluation5.bgcolor, '#ffffc0')
            self.assertEqual(evaluation5.currency.code, 'EUR')

            self.assertEqual(len(evaluation5.line_values), 1)
            self.assertEqual(
                evaluation5.line_values[0].value1, Decimal('1300.01'))

            # evaluation: category- difference amount
            evaluation6, = Evaluation.create([{
                'name': 'Evaluation 6',
                'dtype1': 'categories_glperc',
                'chart': 'hbar',
                'categories': [('add', [cb_cat.id])],
                }])
            self.assertEqual(evaluation6.dtype1, 'categories_glperc')
            self.assertEqual(evaluation6.chart, 'hbar')
            self.assertEqual(evaluation6.legend, True)
            self.assertEqual(evaluation6.maincolor, 'default')
            self.assertEqual(evaluation6.bgcolor, '#ffffc0')
            self.assertEqual(evaluation6.currency.code, 'EUR')

            self.assertEqual(len(evaluation6.line_values), 1)
            self.assertEqual(
                evaluation6.line_values[0].value1, Decimal('6.95'))

    @with_transaction()
    def test_report_chart_pie_book_red(self):
        """ create 3x cashbooks, add bookings,
            create report with cashbooks, check
        """
        Evaluation = Pool().get('cashbook_report.evaluation')

        books = self.prep_report_3books()

        company = self.prep_company()
        with Transaction().set_context({
                'company': company.id}):
            evaluation, = Evaluation.create([{
                'name': 'Evaluation 1',
                'cashbooks': [('add', [x.id for x in books])],
                }])
            self.assertEqual(evaluation.dtype1, 'cashbooks')
            self.assertEqual(evaluation.chart, 'pie')
            self.assertEqual(evaluation.legend, True)
            self.assertEqual(evaluation.maincolor, 'default')
            self.assertEqual(evaluation.bgcolor, '#ffffc0')
            self.assertEqual(evaluation.currency.code, 'EUR')

            # check uiview
            self.assertEqual(
                evaluation.ui_view_chart.model,
                'cashbook_report.eval_line')
            self.assertEqual(
                evaluation.ui_view_chart.module, 'cashbook_report')
            self.assertEqual(evaluation.ui_view_chart.priority, 10)
            self.assertEqual(evaluation.ui_view_chart.type, 'graph')
            self.assertEqual(
                evaluation.ui_view_chart.data,
                """<?xml version="1.0"?>
<graph type="pie" legend="1"  background="#ffffc0">
    <x>
        <field name="name"/>
    </x>
    <y>
        <field name="value1" fill="1" empty="0" string="Cashbooks [Amount]"/>
    </y>
</graph>
""")

            self.assertEqual(len(evaluation.cashbooks), 3)
            self.assertEqual(
                evaluation.cashbooks[0].rec_name, 'Book 1 | 25.00 usd | Open')
            self.assertEqual(
                evaluation.cashbooks[1].rec_name, 'Book 2 | 12.50 usd | Open')
            self.assertEqual(
                evaluation.cashbooks[2].rec_name, 'Book 3 | 23.00 € | Open')
            self.assertEqual(evaluation.cashbooks[0].currency.code, 'usd')
            self.assertEqual(evaluation.cashbooks[1].currency.code, 'usd')
            self.assertEqual(evaluation.cashbooks[2].currency.code, 'EUR')

            self.assertEqual(len(evaluation.line_values), 3)
            self.assertEqual(
                evaluation.line_values[0].name, 'Book 1 | 25.00 usd | Open')
            self.assertEqual(
                evaluation.line_values[1].name, 'Book 2 | 12.50 usd | Open')
            self.assertEqual(
                evaluation.line_values[2].name, 'Book 3 | 23.00 € | Open')

            self.assertEqual(
                evaluation.line_values[0].eval_currency.code, 'EUR')
            self.assertEqual(
                evaluation.line_values[1].eval_currency.code, 'EUR')
            self.assertEqual(
                evaluation.line_values[2].eval_currency.code, 'EUR')

            self.assertEqual(
                evaluation.line_values[0].value1, Decimal('23.81'))
            self.assertEqual(
                evaluation.line_values[1].value1, Decimal('11.90'))
            self.assertEqual(
                evaluation.line_values[2].value1, Decimal('23.00'))

    @with_transaction()
    def test_report_chart_pie_type_red(self):
        """ create 3x cashbooks, add bookings,
            create report with types of cashbooks, check
        """
        pool = Pool()
        Evaluation = pool.get('cashbook_report.evaluation')
        Types = pool.get('cashbook.type')

        self.prep_report_3books()

        company = self.prep_company()
        with Transaction().set_context({
                'company': company.id,  # company-currency: EUR
                'date': date(2022, 5, 15)}):
            evaluation, = Evaluation.create([{
                'name': 'Evaluation 1',
                'dtype1': 'types',
                'types': [('add', [x.id for x in Types.search([])])],
                }])
            self.assertEqual(evaluation.dtype1, 'types')
            self.assertEqual(evaluation.chart, 'pie')
            self.assertEqual(evaluation.legend, True)
            self.assertEqual(evaluation.maincolor, 'default')
            self.assertEqual(evaluation.bgcolor, '#ffffc0')
            self.assertEqual(evaluation.currency.code, 'EUR')

            # 37.50 USD, Cash
            # 23.00 EUR, Bank
            self.assertEqual(len(evaluation.types), 2)
            self.assertEqual(evaluation.types[0].rec_name, 'BK - Bank')
            self.assertEqual(evaluation.types[1].rec_name, 'CAS - Cash')

            self.assertEqual(len(evaluation.line_values), 2)

            # 23.00 EUR
            self.assertEqual(
                evaluation.line_values[0].eval_currency.code, 'EUR')
            self.assertEqual(evaluation.line_values[0].name, 'BK - Bank')
            self.assertEqual(
                evaluation.line_values[0].value1, Decimal('23.0'))

            # 37.50 USD --> EUR
            self.assertEqual(evaluation.line_values[1].name, 'CAS - Cash')
            self.assertEqual(
                evaluation.line_values[1].eval_currency.code, 'EUR')
            self.assertEqual(
                evaluation.line_values[1].value1, Decimal('35.71'))

    @with_transaction()
    def test_report_chart_pie_currency_red(self):
        """ create 3x cashbooks, add bookings,
            create report with types of cashbooks, check
        """
        pool = Pool()
        Evaluation = pool.get('cashbook_report.evaluation')
        Currency = pool.get('currency.currency')

        self.prep_report_3books()

        company = self.prep_company()
        with Transaction().set_context({
                'company': company.id}):
            evaluation, = Evaluation.create([{
                'name': 'Evaluation 1',
                'dtype1': 'currencies',
                'currencies': [('add', [x.id for x in Currency.search([])])],
                }])
            self.assertEqual(evaluation.dtype1, 'currencies')
            self.assertEqual(evaluation.chart, 'pie')
            self.assertEqual(evaluation.legend, True)
            self.assertEqual(evaluation.maincolor, 'default')
            self.assertEqual(evaluation.bgcolor, '#ffffc0')
            self.assertEqual(evaluation.currency.code, 'EUR')

            self.assertEqual(len(evaluation.currencies), 2)
            self.assertEqual(evaluation.currencies[0].code, 'EUR')
            self.assertEqual(evaluation.currencies[1].code, 'usd')

            self.assertEqual(len(evaluation.line_values), 2)
            self.assertEqual(evaluation.line_values[0].name, 'Euro')
            self.assertEqual(
                evaluation.line_values[0].value1, Decimal('23.0'))
            self.assertEqual(evaluation.line_values[1].name, 'usd')
            self.assertEqual(
                evaluation.line_values[1].value1, Decimal('35.71'))

            self.assertEqual(evaluation.line_values[0].value2, None)
            self.assertEqual(evaluation.line_values[0].value3, None)
            self.assertEqual(evaluation.line_values[0].value4, None)
            self.assertEqual(evaluation.line_values[0].value5, None)

# end ReportTestCase


del CashbookInvestmentTestCase
