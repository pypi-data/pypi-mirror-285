# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.model import fields
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from sql.aggregate import Count
from sql.conditionals import Case


class Currency(metaclass=PoolMeta):
    __name__ = 'currency.currency'

    cashbook_hasbookings = fields.Function(fields.Boolean(
        string='Has Bookings', readonly=True),
        'on_change_with_cashbook_hasbookings',
        searcher='search_cashbook_hasbookings')

    @fields.depends('id')
    def on_change_with_cashbook_hasbookings(self, name=None):
        """ result: True if there are bookings
        """
        Lines = Pool().get('cashbook.line')

        with Transaction().set_context({
                '_check_access': True}):
            if Lines.search_count([
                    ('cashbook.currency.id', '=', self.id)]) > 0:
                return True
        return False

    @classmethod
    def search_cashbook_hasbookings(cls, name, clause):
        """ indicate existing bookings
        """
        pool = Pool()
        Currency2 = pool.get('currency.currency')
        Cashbook = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')
        tab_cur = Currency2.__table__()
        tab_book = Cashbook.__table__()
        tab_line = Line.__table__()
        Operator = fields.SQL_OPERATORS[clause[1]]

        query = tab_book.join(
                tab_line,
                condition=tab_book.id == tab_line.cashbook,
            ).join(
                tab_cur,
                condition=tab_cur.id == tab_book.currency,
            ).select(
                tab_cur.id,
                having=Operator(Case(
                        (Count(tab_line.id) > 0, True),
                        else_=False,
                    ), clause[2]),
                group_by=[tab_cur.id])
        return [('id', 'in', query)]

# end Currency
