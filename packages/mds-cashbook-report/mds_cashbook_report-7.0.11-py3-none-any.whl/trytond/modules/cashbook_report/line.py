# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from decimal import Decimal
from sql.aggregate import Sum
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Bool
from trytond.transaction import Transaction
from trytond.i18n import gettext
from trytond.exceptions import UserError
from trytond.pool import Pool
from .templates import cashbook_types, category_types, booktype_types


class EvaluationLine(ModelSQL, ModelView):
    'Evaluation Line Relation'
    __name__ = 'cashbook_report.eval_line'

    evaluation = fields.Many2One(
        string='Evaluation', required=True, ondelete='CASCADE',
        model_name='cashbook_report.evaluation')
    cashbook = fields.Many2One(
        string='Cashbook', ondelete='CASCADE', model_name='cashbook.book',
        states={
            'required': Eval('eval_dtype1', '').in_(cashbook_types),
        }, depends=['eval_dtype1'])
    dtype = fields.Many2One(
        string='Type', ondelete='CASCADE', model_name='cashbook.type',
        states={
            'required': Eval('eval_dtype1', '').in_(booktype_types),
        }, depends=['eval_dtype1'])
    currency = fields.Many2One(
        string='Currency', ondelete='CASCADE', model_name='currency.currency',
        states={
            'required': Eval('eval_dtype1', '') == 'currencies',
        }, depends=['eval_dtype1'])
    category = fields.Many2One(
        string='Category', ondelete='CASCADE',
        model_name='cashbook.bookcategory',
        states={
            'required': Eval('eval_dtype1', '').in_(category_types),
        }, depends=['eval_dtype1'])

    # dtypes + currency of evaluation
    eval_dtype1 = fields.Function(fields.Char(
        string='Data type 1', readonly=True), 'on_change_with_eval_dtype1')
    eval_dtype2 = fields.Function(fields.Char(
        string='Data type 2', readonly=True), 'on_change_with_eval_dtype2')
    eval_dtype3 = fields.Function(fields.Char(
        string='Data type 3', readonly=True), 'on_change_with_eval_dtype3')
    eval_dtype4 = fields.Function(fields.Char(
        string='Data type 4', readonly=True), 'on_change_with_eval_dtype4')
    eval_dtype5 = fields.Function(fields.Char(
        string='Data type 5', readonly=True), 'on_change_with_eval_dtype5')
    eval_currency = fields.Function(fields.Many2One(
        model_name='currency.currency',
        string="Currency", readonly=True), 'on_change_with_eval_currency')
    currency_digits = fields.Function(fields.Integer(
        string='Currency Digits', readonly=True),
        'on_change_with_currency_digits')

    name = fields.Function(fields.Char(
        string='Name'), 'on_change_with_name', setter='set_name_data')
    name_line = fields.Char(string='Name', states={'invisible': True})
    value1 = fields.Function(fields.Numeric(
        string='Value 1',
        readonly=True, digits=(16, Eval('currency_digits', 2)),
        depends=['currency_digits']),
        'on_change_with_value1')
    value2 = fields.Function(fields.Numeric(
        string='Value 2',
        readonly=True, digits=(16, Eval('currency_digits', 2)),
        states={'invisible': ~Bool(Eval('eval_dtype2', ''))},
        depends=['currency_digits', 'eval_dtype2']),
        'on_change_with_value2')
    value3 = fields.Function(fields.Numeric(
        string='Value 3',
        readonly=True, digits=(16, Eval('currency_digits', 2)),
        states={'invisible': ~Bool(Eval('eval_dtype3', ''))},
        depends=['currency_digits', 'eval_dtype3']),
        'on_change_with_value3')
    value4 = fields.Function(fields.Numeric(
        string='Value 4',
        readonly=True, digits=(16, Eval('currency_digits', 2)),
        states={'invisible': ~Bool(Eval('eval_dtype4', ''))},
        depends=['currency_digits', 'eval_dtype4']),
        'on_change_with_value4')
    value5 = fields.Function(fields.Numeric(
        string='Value 5',
        readonly=True, digits=(16, Eval('currency_digits', 2)),
        states={'invisible': ~Bool(Eval('eval_dtype5', ''))},
        depends=['currency_digits', 'eval_dtype5']),
        'on_change_with_value5')

    @classmethod
    def set_name_data(cls, lines, name, value):
        """ store updated name
        """
        cls.write(*[lines, {'name_line': value}])

    @classmethod
    def fields_view_get(cls, view_id, view_type='form'):
        """ replace form-view-id
        """
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        Evaluation = pool.get('cashbook_report.evaluation')
        context = Transaction().context

        # get id of origin chart-form
        form_id = ModelData.get_id('cashbook_report', 'evalline_view_graph')

        # active_evaluation was added by tree_open-action
        active_evaluation = context.get('active_evaluation', None)

        # check if we are requested for our default form...
        if (view_type == 'graph') and (view_id == form_id) and \
                (active_evaluation is not None):
            evaluation, = Evaluation.browse([active_evaluation])
            if evaluation.ui_view_chart:
                # ... switch to view, created by evaluation-config
                view_id = evaluation.ui_view_chart.id

        return super(EvaluationLine, cls).fields_view_get(
                    view_id=view_id, view_type=view_type)

    @fields.depends('evaluation', '_parent_evaluation.dtype1')
    def on_change_with_eval_dtype1(self, name=None):
        """ get dtype1 from parent
        """
        if self.evaluation:
            return self.evaluation.dtype1

    @fields.depends('evaluation', '_parent_evaluation.dtype2')
    def on_change_with_eval_dtype2(self, name=None):
        """ get dtype2 from parent
        """
        if self.evaluation:
            return self.evaluation.dtype2

    @fields.depends('evaluation', '_parent_evaluation.dtype3')
    def on_change_with_eval_dtype3(self, name=None):
        """ get dtype3 from parent
        """
        if self.evaluation:
            return self.evaluation.dtype3

    @fields.depends('evaluation', '_parent_evaluation.dtype4')
    def on_change_with_eval_dtype4(self, name=None):
        """ get dtype4 from parent
        """
        if self.evaluation:
            return self.evaluation.dtype4

    @fields.depends('evaluation', '_parent_evaluation.dtype5')
    def on_change_with_eval_dtype5(self, name=None):
        """ get dtype5 from parent
        """
        if self.evaluation:
            return self.evaluation.dtype5

    @fields.depends('evaluation', '_parent_evaluation.currency')
    def on_change_with_eval_currency(self, name=None):
        """ currency of evaluation
        """
        if self.evaluation:
            return self.evaluation.currency.id

    @fields.depends('evaluation', '_parent_evaluation.currency')
    def on_change_with_currency_digits(self, name=None):
        """ currency-digits of evaluation
        """
        if self.evaluation:
            return self.evaluation.currency.digits
        else:
            return 2

    @fields.depends(
        'eval_dtype1', 'category', 'cashbook', 'dtype', 'currency',
        'name_line')
    def on_change_with_name(self, name=None):
        """ get name of Type
        """
        # prefer to use local stored name of line
        if self.name_line:
            if len(self.name_line) > 0:
                return self.name_line

        # otherwise use rec_name of linked record
        if self.eval_dtype1:
            dtype_sel = {'currencies': 'currency'}
            dtype_sel.update({x: 'cashbook' for x in cashbook_types})
            dtype_sel.update({x: 'category' for x in category_types})
            dtype_sel.update({x: 'dtype' for x in booktype_types})

            return getattr(
                getattr(self, dtype_sel[self.eval_dtype1], None),
                'rec_name', None)

    def convert_to_evalcurrency(self, from_currency, amount):
        """ convert amount to current evaluation-currency
        """
        Currency = Pool().get('currency.currency')

        exp = Decimal(Decimal(1) / 10 ** self.currency_digits)
        if amount is None:
            return Decimal('0.0')
        return Currency.compute(
            from_currency, amount, self.eval_currency).quantize(exp)

    @classmethod
    def validate(cls, records):
        """ check parent record
        """
        super(EvaluationLine, cls).validate(records)
        for record in records:
            if (record.evaluation.dtype1 not in cashbook_types) and \
                    (record.cashbook is not None):
                raise UserError(gettext(
                    'cashbook_report.msg_invalid_dtype',
                    typename=gettext('cashbook_report.msg_dtype_cashbooks')))
            if (record.evaluation.dtype1 not in booktype_types) and \
                    (record.dtype is not None):
                raise UserError(gettext(
                    'cashbook_report.msg_invalid_dtype',
                    typename=gettext('cashbook_report.msg_dtype_types')))
            if (record.evaluation.dtype1 != 'currencies') and \
                    (record.currency is not None):
                raise UserError(gettext(
                    'cashbook_report.msg_invalid_dtype',
                    typename=gettext('cashbook_report.msg_dtype_currencies')))
            if (record.evaluation.dtype1 not in category_types) and \
                    (record.category is not None):
                raise UserError(gettext(
                    'cashbook_report.msg_invalid_dtype',
                    typename=gettext('cashbook_report.msg_dtype_categories')))

    def get_value_by_query(self, query):
        """ run 'query' on Lines, convert used
            currencies to evaluation-currency
        """
        pool = Pool()
        Lines = pool.get('cashbook.line')
        Cashbook = pool.get('cashbook.book')
        Currency = pool.get('currency.currency')
        tab_line = Lines.__table__()
        tab_book = Cashbook.__table__()
        cursor = Transaction().connection.cursor()

        total_amount = Decimal('0.0')
        with Transaction().set_context({
                '_check_access': True}):
            lines = Lines.search(query, query=True)

            query = lines.join(
                    tab_line,
                    condition=lines.id == tab_line.id,
                ).join(
                    tab_book,
                    condition=tab_book.id == tab_line.cashbook,
                ).select(
                    tab_book.currency,
                    Sum(tab_line.credit - tab_line.debit).as_('balance'),
                    group_by=[tab_book.currency])
            cursor.execute(*query)
            records = cursor.fetchall()

            for record in records:
                (id_currency, bal1) = record

                if bal1 is not None:
                    total_amount += self.convert_to_evalcurrency(
                            Currency(id_currency), bal1)
        return total_amount

    def get_value_cashbooks(self):
        """ balance of cashbooks
        """
        if self.cashbook:
            return self.convert_to_evalcurrency(
                    self.cashbook.currency, self.cashbook.balance)

    def get_value_categories(self):
        """ get balance of bookings in categories
            converted to currency of evaluation
        """
        IrDate = Pool().get('ir.date')

        if self.category is None:
            return None

        return self.get_value_by_query([
                ('cashbook.categories.id', '=', self.category.id),
                ('cashbook.state', '=', 'open'),
                ('date', '<=', IrDate.today())])

    def get_value_types(self):
        """ get balance of bookings in cashbooks by 'type',
            converted to currency of evaluation
        """
        IrDate = Pool().get('ir.date')

        if self.dtype is None:
            return None

        return self.get_value_by_query([
                ('cashbook.btype.id', '=', self.dtype.id),
                ('cashbook.state', '=', 'open'),
                ('date', '<=', IrDate.today())])

    def get_value_currencies(self):
        """ get balance of bookings in cashbooks by 'currency',
            converted to currency of evaluation
        """
        IrDate = Pool().get('ir.date')

        if self.currency is None:
            return None

        return self.get_value_by_query([
                ('cashbook.currency.id', '=', self.currency.id),
                ('cashbook.state', '=', 'open'),
                ('date', '<=', IrDate.today())])

    @fields.depends(
        'eval_dtype1', 'eval_currency', 'currency_digits',
        'cashbook', '_parent_cashbook.currency', '_parent_cashbook.balance',
        'category', '_parent_category.id',
        'evaluation', '_parent_evaluation.id', 'dtype', 'currency')
    def on_change_with_value1(self, name=None):
        """ balance of value1
        """
        if (self.evaluation is None) or (self.eval_currency is None) or \
                (self.currency_digits is None) or (self.eval_dtype1 is None):
            return None
        return getattr(self, 'get_value_%s' % self.eval_dtype1)()

    @fields.depends(
        'eval_dtype2', 'eval_currency', 'currency_digits',
        'cashbook', '_parent_cashbook.currency', '_parent_cashbook.balance',
        'category', '_parent_category.id',
        'evaluation', '_parent_evaluation.id', 'dtype', 'currency')
    def on_change_with_value2(self, name=None):
        """ balance of value2
        """
        if (self.evaluation is None) or (self.eval_currency is None) or \
                (self.currency_digits is None) or (self.eval_dtype2 is None):
            return None
        return getattr(self, 'get_value_%s' % self.eval_dtype2)()

    @fields.depends(
        'eval_dtype3', 'eval_currency', 'currency_digits',
        'cashbook', '_parent_cashbook.currency', '_parent_cashbook.balance',
        'category', '_parent_category.id',
        'evaluation', '_parent_evaluation.id', 'dtype', 'currency')
    def on_change_with_value3(self, name=None):
        """ balance of value3
        """
        if (self.evaluation is None) or (self.eval_currency is None) or \
                (self.currency_digits is None) or (self.eval_dtype3 is None):
            return None
        return getattr(self, 'get_value_%s' % self.eval_dtype3)()

    @fields.depends(
        'eval_dtype4', 'eval_currency', 'currency_digits',
        'cashbook', '_parent_cashbook.currency', '_parent_cashbook.balance',
        'category', '_parent_category.id',
        'evaluation', '_parent_evaluation.id', 'dtype', 'currency')
    def on_change_with_value4(self, name=None):
        """ balance of value4
        """
        if (self.evaluation is None) or (self.eval_currency is None) or \
                (self.currency_digits is None) or (self.eval_dtype4 is None):
            return None
        return getattr(self, 'get_value_%s' % self.eval_dtype4)()

    @fields.depends(
        'eval_dtype5', 'eval_currency', 'currency_digits',
        'cashbook', '_parent_cashbook.currency', '_parent_cashbook.balance',
        'category', '_parent_category.id',
        'evaluation', '_parent_evaluation.id', 'dtype', 'currency')
    def on_change_with_value5(self, name=None):
        """ balance of cashbook
        """
        if (self.evaluation is None) or (self.eval_currency is None) or \
                (self.currency_digits is None) or (self.eval_dtype5 is None):
            return None
        return getattr(self, 'get_value_%s' % self.eval_dtype5)()

# end EvaluationLine
