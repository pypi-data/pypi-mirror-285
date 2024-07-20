# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.pool import PoolMeta, Pool
from trytond.i18n import gettext
from decimal import Decimal


class InvestmentEvaluation(metaclass=PoolMeta):
    __name__ = 'cashbook_report.evaluation'

    @classmethod
    def get_sel_etype(cls):
        """ get list of evaluation-types
        """
        result = super(InvestmentEvaluation, cls).get_sel_etype()
        result.extend([
            ('cashbooks_gldiff', gettext(
                'cashbook_report.msg_dtype_cashbooks_gldiff')),
            ('cashbooks_glperc', gettext(
                'cashbook_report.msg_dtype_cashbooks_glperc')),
            ('cashbooks_glvalue', gettext(
                'cashbook_report.msg_dtype_cashbooks_glvalue')),
            ('cashbooks_glyield', gettext(
                'cashbook_report.msg_dtype_cashbooks_glyield')),
            ('categories_gldiff', gettext(
                'cashbook_report.msg_dtype_categories_gldiff')),
            ('categories_glvalue', gettext(
                'cashbook_report.msg_dtype_categories_glvalue')),
            ('categories_glperc',  gettext(
                'cashbook_report.msg_dtype_categories_glperc')),
            ('categories_glyield',  gettext(
                'cashbook_report.msg_dtype_categories_glyield')),
            ('types_gldiff', gettext(
                'cashbook_report.msg_dtype_types_gldiff')),
            ('types_glvalue', gettext(
                'cashbook_report.msg_dtype_types_glvalue')),
            ('types_glperc',  gettext(
                'cashbook_report.msg_dtype_types_glperc')),
            ('types_glyield',  gettext(
                'cashbook_report.msg_dtype_types_glyield')),
            ])
        return result

# end InvestmentEvaluation


class InvestmentLine(metaclass=PoolMeta):
    __name__ = 'cashbook_report.eval_line'

    def get_percent_by_query(self, query):
        """ get percentual difference of bookings in categories
            converted to currency of evaluation
        """
        Book = Pool().get('cashbook.book')

        query2 = [('state', '=', 'open')]
        query2.extend(query)
        books = Book.search(query2)

        value = Decimal('0.0')
        amount = Decimal('0.0')

        if len(books) > 0:
            value = sum([
                x.current_value_ref for x in books
                if (x.current_value_ref is not None)
                and (x.feature == 'asset')])
            amount = sum([
                x.balance_ref for x in books
                if (x.balance_ref is not None) and (x.feature == 'asset')])
            if amount != Decimal('0.0'):
                return self.convert_to_evalcurrency(
                    books[0].company.currency,
                    Decimal('100.0') * value / amount - Decimal('100.0'))
        return Decimal('0.0')

    def get_difference_by_query(self, query):
        """ get difference amount of bookings in categories
            converted to currency of evaluation
        """
        Book = Pool().get('cashbook.book')

        query2 = [('state', '=', 'open')]
        query2.extend(query)
        books = Book.search(query2)

        result = Decimal('0.0')
        if len(books) > 0:
            result = sum([
                x.current_value_ref - x.balance_ref for x in books
                if (x.current_value_ref is not None) and
                (x.balance_ref is not None) and
                (x.feature == 'asset')])
            result = self.convert_to_evalcurrency(
                    books[0].company.currency, result)
        return result

    def get_currentvalue_by_query(self, query):
        """ get current value of bookings in categories
            converted to currency of evaluation
        """
        Book = Pool().get('cashbook.book')

        query2 = [('state', '=', 'open')]
        query2.extend(query)
        books = Book.search(query2)

        result = Decimal('0.0')
        if len(books) > 0:
            for book in books:
                if (book.feature == 'asset') or \
                        ((book.feature is None) and
                            (book.current_value_ref is not None)):
                    if book.current_value_ref is not None:
                        result += book.current_value_ref
                else:
                    if book.balance_ref is not None:
                        result += book.balance_ref
            return self.convert_to_evalcurrency(
                    books[0].company.currency, result)
        return result

    def get_totalyield_by_query(self, query):
        """ get total yield of cashbookings
            converted to currency of evaluation
        """
        Book = Pool().get('cashbook.book')

        query2 = [('state', '=', 'open')]
        query2.extend(query)
        books = Book.search(query2)

        result = Decimal('0.0')
        if len(books) > 0:
            for book in books:
                if (book.feature == 'asset') and \
                        (book.yield_balance is not None):
                    result += self.convert_to_evalcurrency(
                        books[0].currency, book.yield_balance)
        return result

    def get_value_categories_glperc(self):
        """ get percent of profit/loss by category
        """
        if self.category is None:
            return None

        return self.get_percent_by_query([
            ('categories.id', '=', self.category.id)])

    def get_value_categories_gldiff(self):
        """ get difference amount by category
        """
        if self.category is None:
            return None

        return self.get_difference_by_query([
            ('categories.id', '=', self.category.id)])

    def get_value_categories_glvalue(self):
        """ get current value by category
        """
        if self.category is None:
            return None

        return self.get_currentvalue_by_query([
            ('categories.id', '=', self.category.id)])

    def get_value_categories_glyield(self):
        """ get total yield by type
        """
        if self.category is None:
            return None

        return self.get_totalyield_by_query([
            ('categories.id', '=', self.category.id),
            ])

    def get_value_types_glperc(self):
        """ get percent of profit/loss by type
        """
        if self.dtype is None:
            return None

        return self.get_percent_by_query([('btype.id', '=', self.dtype.id)])

    def get_value_types_gldiff(self):
        """ get difference amount by type
        """
        if self.dtype is None:
            return None

        return self.get_difference_by_query([
            ('btype.id', '=', self.dtype.id)])

    def get_value_types_glvalue(self):
        """ get current value by type
        """
        if self.dtype is None:
            return None

        return self.get_currentvalue_by_query([
            ('btype.id', '=', self.dtype.id)])

    def get_value_types_glyield(self):
        """ get total yield by type
        """
        if self.dtype is None:
            return None

        return self.get_totalyield_by_query([
            ('btype.id', '=', self.dtype.id)])

    def get_value_cashbooks_glperc(self):
        """ percent of profit/loss of cashbooks
        """
        if self.cashbook:
            if self.cashbook.feature == 'asset':
                return self.cashbook.diff_percent
            else:
                return Decimal('0.0')

    def get_value_cashbooks_gldiff(self):
        """ amount of profit/loss of cashbooks
        """
        if self.cashbook:
            if self.cashbook.feature == 'asset':
                return self.convert_to_evalcurrency(
                        self.cashbook.currency,
                        self.cashbook.diff_amount)
            else:
                return Decimal('0.0')

    def get_value_cashbooks_glvalue(self):
        """ current value of cashbooks
        """
        if self.cashbook:
            if (self.cashbook.feature == 'asset') or \
                    ((self.cashbook.feature is None) and
                        (self.cashbook.current_value is not None)):
                return self.convert_to_evalcurrency(
                        self.cashbook.currency,
                        self.cashbook.current_value)
            else:
                return self.convert_to_evalcurrency(
                        self.cashbook.currency,
                        self.cashbook.balance)

    def get_value_cashbooks_glyield(self):
        """ total yield of investment
        """
        if self.cashbook:
            return self.get_totalyield_by_query([
                    ('id', '=', self.cashbook.id)])

# end InvestmentLine
