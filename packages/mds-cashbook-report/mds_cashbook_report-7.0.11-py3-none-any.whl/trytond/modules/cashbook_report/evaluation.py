# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from sql.conditionals import Case
from trytond.model import ModelView, ModelSQL, fields, sequence_ordered
from trytond.pyson import Eval, Bool
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.i18n import gettext
from trytond.exceptions import UserError
from .colors import sel_color as sel_bgcolor
from .templates import (
    template_view_graph, template_view_line, cashbook_types,
    category_types, booktype_types, currency_types)


sel_chart = [
    ('vbar', 'Vertical Bars'),
    ('hbar', 'Horizontal Bars'),
    ('pie', 'Pie'),
    ('line', 'Line'),
    ]


sel_maincolor = [
    ('default', 'Default'),
    ('red', 'Red'),
    ('green', 'Green'),
    ('grey', 'Grey'),
    ('black', 'Black'),
    ('darkcyan', 'Dark Cyan'),
]


class Evaluation(sequence_ordered(), ModelSQL, ModelView):
    'Evaluation'
    __name__ = 'cashbook_report.evaluation'

    company = fields.Many2One(
        string='Company', model_name='company.company',
        required=True, ondelete="RESTRICT")
    name = fields.Char(string='Name', required=True)

    # max. 5x data tyypes to show
    dtype1 = fields.Selection(
        string='Data type 1', required=True, sort=True,
        selection='get_sel_etype', help='Type of data displayed')
    dtype1_string = dtype1.translated('dtype1')
    dtype2 = fields.Selection(
        string='Data type 2', sort=True,
        selection='get_sel_etype2', help='Type of data displayed',
        states={
            'invisible': ~Bool(Eval('dtype1', '')),
        }, depends=['dtype1'])
    dtype2_string = dtype2.translated('dtype2')
    dtype3 = fields.Selection(
        string='Data type 3', sort=True,
        selection='get_sel_etype2', help='Type of data displayed',
        states={
            'invisible': ~Bool(Eval('dtype2', '')),
        }, depends=['dtype2'])
    dtype3_string = dtype3.translated('dtype3')
    dtype4 = fields.Selection(
        string='Data type 4', sort=True,
        selection='get_sel_etype2', help='Type of data displayed',
        states={
            'invisible': ~Bool(Eval('dtype3', '')),
        }, depends=['dtype3'])
    dtype4_string = dtype4.translated('dtype4')
    dtype5 = fields.Selection(
        string='Data type 5', sort=True,
        selection='get_sel_etype2', help='Type of data displayed',
        states={
            'invisible': ~Bool(Eval('dtype4', '')),
        }, depends=['dtype4'])
    dtype5_string = dtype5.translated('dtype5')

    chart = fields.Selection(
        string='Chart type', required=True, sort=False,
        selection=sel_chart, help='Type of graphical presentation.')
    legend = fields.Boolean(string='Legend')
    maincolor = fields.Selection(
        string='Color scheme', required=True,
        help='The color scheme determines the hue of all ' +
        'components of the chart.', selection=sel_maincolor, sort=False)
    bgcolor = fields.Selection(
        string='Background Color', required=True,
        help='Background color of the chart area.', sort=False,
        selection=sel_bgcolor)
    currency = fields.Many2One(
        string='Currency', ondelete='RESTRICT',
        model_name='currency.currency')

    cashbooks = fields.Many2Many(
        string='Cashbooks', relation_name='cashbook_report.eval_line',
        origin='evaluation', target='cashbook',
        states={'invisible': ~Eval('dtype1', '').in_(cashbook_types)},
        depends=['dtype1'])
    types = fields.Many2Many(
        string='Types', relation_name='cashbook_report.eval_line',
        origin='evaluation', target='dtype',
        states={'invisible': ~Eval('dtype1', '').in_(booktype_types)},
        depends=['dtype1'])
    currencies = fields.Many2Many(
        string='Currencies', relation_name='cashbook_report.eval_line',
        origin='evaluation', target='currency',
        filter=[('cashbook_hasbookings', '=', True)],
        states={'invisible': Eval('dtype1', '') != 'currencies'},
        depends=['dtype1'])
    categories = fields.Many2Many(
        string='Categories', relation_name='cashbook_report.eval_line',
        origin='evaluation', target='category',
        states={'invisible': ~Eval('dtype1', '').in_(category_types)},
        depends=['dtype1'])

    line_values = fields.One2Many(
        string='Line Values', field='evaluation', readonly=True,
        model_name='cashbook_report.eval_line')

    ui_view_chart = fields.Many2One(
        string='UI View Chart', model_name='ir.ui.view', ondelete='SET NULL')
    dashb_actwin = fields.Many2One(
        string='Dashboard Window', model_name='ir.action.act_window',
        ondelete='SET NULL')
    dashb_actview = fields.Many2One(
        string='Dashboard View', model_name='ir.action.act_window.view',
        ondelete='SET NULL')

    @classmethod
    def __register__(cls, module_name):
        super(Evaluation, cls).__register__(module_name)

        table = cls.__table_handler__(module_name)
        tav_eval = cls.__table__()
        cursor = Transaction().connection.cursor()

        # x.0.9 --> x.0.10
        if table.column_exist('dtype'):
            query = tav_eval.update(
                columns=[tav_eval.dtype1],
                values=[Case(
                    (tav_eval.dtype == 'category_gldiff',
                        'categories_gldiff'),
                    (tav_eval.dtype == 'category_glvalue',
                        'categories_glvalue'),
                    (tav_eval.dtype == 'category_glperc',
                        'categories_glperc'),
                    (tav_eval.dtype == 'category_glyield',
                        'categories_glyield'),
                    else_=tav_eval.dtype)
                    ])
            cursor.execute(*query)
            table.drop_column('dtype')

    @classmethod
    def default_currency(cls):
        """ currency of company
        """
        Company = Pool().get('company.company')

        company = cls.default_company()
        if company:
            company = Company(company)
            if company.currency:
                return company.currency.id

    @staticmethod
    def default_company():
        return Transaction().context.get('company') or None

    @classmethod
    def default_bgcolor(cls):
        """ default: Yellow 5
        """
        return '#ffffc0'

    @classmethod
    def default_maincolor(cls):
        """ default: 'default'
        """
        return 'default'

    @classmethod
    def default_legend(cls):
        """ default True
        """
        return True

    @classmethod
    def default_dtype1(cls):
        """ default 'book'
        """
        return 'cashbooks'

    @classmethod
    def default_dtype2(cls):
        """ default None
        """
        return None

    @classmethod
    def default_dtype3(cls):
        """ default None
        """
        return None

    @classmethod
    def default_dtype4(cls):
        """ default None
        """
        return None

    @classmethod
    def default_dtype5(cls):
        """ default None
        """
        return None

    @fields.depends('dtype1', 'dtype2', 'dtype3', 'dtype4', 'dtype5')
    def on_change_dtype1(self):
        """ update other dtype-fields
        """
        self.get_onchange_dtypes()

    @fields.depends('dtype1', 'dtype2', 'dtype3', 'dtype4', 'dtype5')
    def on_change_dtype2(self):
        """ update other dtype-fields
        """
        self.get_onchange_dtypes()

    @fields.depends('dtype1', 'dtype2', 'dtype3', 'dtype4', 'dtype5')
    def on_change_dtype3(self):
        """ update other dtype-fields
        """
        self.get_onchange_dtypes()

    @fields.depends('dtype1', 'dtype2', 'dtype3', 'dtype4', 'dtype5')
    def on_change_dtype4(self):
        """ update other dtype-fields
        """
        self.get_onchange_dtypes()

    @fields.depends('dtype1', 'dtype2', 'dtype3', 'dtype4', 'dtype5')
    def on_change_dtype5(self):
        """ update other dtype-fields
        """
        self.get_onchange_dtypes()

    def get_onchange_dtypes(self):
        """ update other dtype-fields
        """
        dtypes = [x[0] for x in self.get_sel_etype2()]

        if not self.dtype1:
            self.dtype2 = None

        if self.dtype2 and (self.dtype2 not in dtypes):
            self.dtype2 = None

        if not self.dtype2:
            self.dtype3 = None

        if self.dtype3 and (self.dtype3 not in dtypes):
            self.dtype3 = None

        if not self.dtype3:
            self.dtype4 = None

        if self.dtype4 and (self.dtype4 not in dtypes):
            self.dtype4 = None

        if not self.dtype4:
            self.dtype5 = None

        if self.dtype5 and (self.dtype5 not in dtypes):
            self.dtype5 = None

    @classmethod
    def default_chart(cls):
        """ default 'pie'
        """
        return 'pie'

    @classmethod
    def get_sel_etype(cls):
        """ get list of evaluation-types
        """
        result = [('', '-/-')]
        result.extend([
            (x, gettext('cashbook_report.msg_dtype_%s' % x))
            for x in ['cashbooks', 'types', 'currencies', 'categories']])
        return result

    @fields.depends('dtype1')
    def get_sel_etype2(self):
        """ get list of allowed evaluation-types for dtype2
        """
        Eval2 = Pool().get('cashbook_report.evaluation')

        result = [('', '-/-')]

        dtype1 = getattr(self, 'dtype1', None)
        if not dtype1:
            return result

        dtype = dtype1.split('_')[0]
        result.extend([
            x
            for x in Eval2.get_sel_etype()
            if x[0].startswith(dtype)])
        return result

    @classmethod
    def get_create_view_data(cls, evaluation):
        """ generate dictionary to create view-xml
        """
        dtypes = [{
                'name': getattr(evaluation, 'dtype%d_string' % x),
                'fname': 'value%d' % x}
                for x in range(1, 6)
                if getattr(evaluation, 'dtype%d' % x, None) is not None]

        result = {
            'model': 'cashbook_report.eval_line',
            'module': 'cashbook_report',
            'priority': 10,
            'type': 'graph',
            'data': template_view_graph % {
                'bgcol': '' if evaluation.bgcolor == 'default'
                    else 'background="%s"' % evaluation.bgcolor,
                'legend': '1' if evaluation.legend is True else '0',
                'type': evaluation.chart,
                'colscheme': '' if evaluation.maincolor == 'default'
                    else 'color="%s"' % evaluation.maincolor,
                'lines': '\n'.join([
                        template_view_line % {
                            'fill': '1',
                            'fname': x['fname'],
                            'string': x['name']}
                        for x in dtypes])}}
        return result

    @classmethod
    def uiview_delete(cls, evaluations):
        """ delete action view from evalualtion
        """
        pool = Pool()
        UiView = pool.get('ir.ui.view')
        ActWin = pool.get('ir.action.act_window')

        to_delete_uiview = []
        to_delete_window = []
        for evaluation in evaluations:
            if evaluation.ui_view_chart:
                to_delete_uiview.append(evaluation.ui_view_chart)
            if evaluation.dashb_actwin:
                to_delete_window.append(evaluation.dashb_actwin)

        with Transaction().set_context({
                '_check_access': False}):
            if len(to_delete_uiview) > 0:
                UiView.delete(to_delete_uiview)
            if len(to_delete_window) > 0:
                ActWin.delete(to_delete_window)

    @classmethod
    def uiview_create(cls, evaluations):
        """ create ui view for current setup of evaluation
        """
        pool = Pool()
        UiView = pool.get('ir.ui.view')
        ActWin = pool.get('ir.action.act_window')
        ActView = pool.get('ir.action.act_window.view')
        Evaluation2 = pool.get('cashbook_report.evaluation')
        try:
            DashboardAction = pool.get('dashboard.action')
        except Exception:
            DashboardAction = None

        to_write_eval = []
        to_write_dbaction = []
        for evaluation in evaluations:
            with Transaction().set_context({
                    '_check_access': False}):
                view_graph, = UiView.create([
                    cls.get_create_view_data(evaluation),
                    ])

                dashb_actwin, = ActWin.create([{
                    'name': evaluation.name,
                    'res_model': 'cashbook_report.eval_line',
                    'usage': 'dashboard',
                    'context_domain': '[["evaluation", "=", %d]]' % (
                        evaluation.id),
                    }])

                dashb_actview, = ActView.create([{
                    'sequence': 10,
                    'view': view_graph.id,
                    'act_window': dashb_actwin.id,
                    }])

            to_write_eval.extend([
                [evaluation],
                {
                    'ui_view_chart': view_graph.id,
                    'dashb_actwin': dashb_actwin.id,
                    'dashb_actview': dashb_actview.id,
                }])

            # prepare update dasboard-action
            if DashboardAction is not None:
                if evaluation.dashb_actwin:
                    db_actions = DashboardAction.search([
                        ('act_window.id', '=', evaluation.dashb_actwin.id),
                        ])
                    if len(db_actions) > 0:
                        to_write_dbaction.extend([
                            db_actions,
                            {
                                'act_window': dashb_actwin.id,
                            }])

        if len(to_write_dbaction) > 0:
            DashboardAction.write(*to_write_dbaction)
        cls.uiview_delete(evaluations)
        if len(to_write_eval) > 0:
            Evaluation2.write(*to_write_eval)

    @classmethod
    def validate(cls, records):
        """ check dtype_x
        """
        dtypes = []
        dtypes.extend(cashbook_types)
        dtypes.extend(category_types)
        dtypes.extend(booktype_types)
        dtypes.extend(currency_types)

        for record in records:
            if record.dtype1 not in dtypes:
                raise UserError(gettext(
                    'cashbook_report.msg_invalid_dtype',
                    typename='one of: %(names)s' % {
                        'names': ', '.join(dtypes)}))

            # dtype2...5 must be of same range
            dt1 = record.dtype1.split('_')[0]
            for x in range(2, 6):
                dt_val = getattr(record, 'dtype%d' % x, None)
                if dt_val:

                    if record.chart == 'pie':
                        raise UserError(gettext(
                            'cashbook_report.msg_no_pie_with_dtype2',
                            evalname=record.rec_name))

                    if dt_val not in dtypes:
                        raise UserError(gettext(
                            'cashbook_report.msg_invalid_dtype',
                            typename='one of: %(names)s' % {
                                'names': ', '.join(dtypes)}))

                    if not dt_val.startswith(dt1):
                        raise UserError(gettext(
                            'cashbook_report.msg_not_same_basetype',
                            typename=gettext(
                                'cashbook_report.msg_dtype_%s' % record.dtype1)
                            ))

    @classmethod
    def create(cls, vlist):
        """ add chart
        """
        records = super(Evaluation, cls).create(vlist)
        cls.uiview_create(records)
        return records

    @classmethod
    def write(cls, *args):
        """ unlink records if dtypex changes
        """
        to_write = []
        to_update_uiview = []

        dtypes = {'dtype1', 'dtype2', 'dtype3', 'dtype4', 'dtype5'}

        actions = iter(args)
        for evaluations, values in zip(actions, actions):
            # update ui-view if related fields change
            uiview_fields = {
                'name', 'bgcolor', 'maincolor', 'legend', 'chart'}
            uiview_fields.update(dtypes)
            if uiview_fields.intersection(values.keys()):
                to_update_uiview.extend(evaluations)

            # unlink records if dtype(x) changes
            if set(values.keys()).intersection(dtypes):
                for evaluation in evaluations:
                    dt_value = {x: values.get(x, None) for x in dtypes}
                    dt_eval = {x: getattr(evaluation, x, None) for x in dtypes}

                    # skip un-link if same values are to write
                    if dt_value == dt_eval:
                        continue

                    dtype1 = values.get('dtype1', evaluation.dtype1)
                    for dt in [
                            'cashbooks', 'types', 'currencies',
                            'categories']:
                        if dtype1.startswith(dt):
                            continue

                        lines = getattr(evaluation, dt)
                        if not lines:
                            continue

                        to_write.extend([
                            [evaluation],
                            {
                                dt: [('remove', [x.id for x in lines])],
                            }])

        args = list(args)
        args.extend(to_write)
        super(Evaluation, cls).write(*args)

        if len(to_update_uiview) > 0:
            cls.uiview_create(to_update_uiview)

    @classmethod
    def delete(cls, evaluations):
        """ delete views
        """
        cls.uiview_delete(evaluations)
        super(Evaluation, cls).delete(evaluations)

# end Evaluation
