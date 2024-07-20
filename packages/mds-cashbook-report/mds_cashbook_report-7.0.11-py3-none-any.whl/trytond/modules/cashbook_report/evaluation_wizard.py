# -*- coding: utf-8 -*-
# This file is part of the diagram-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.wizard import Wizard, StateAction
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.i18n import gettext
from trytond.pyson import PYSONEncoder


class OpenChartWizard(Wizard):
    'Open Chart'
    __name__ = 'cashbook_report.wizchart'

    start_state = 'open_'
    open_ = StateAction('cashbook_report.act_evaluation_graph_view')

    def do_open_(self, action):
        """ open view from doubleclick
        """
        Evaluation = Pool().get('cashbook_report.evaluation')
        context = Transaction().context

        # add info to enable replace of ui-view
        evaluation, = Evaluation.browse([context['active_id']])
        if evaluation.ui_view_chart:
            action['pyson_context'] = PYSONEncoder().encode({
                'active_evaluation': evaluation.id,
                'evaluation': evaluation.id})
            action['name'] = gettext(
                'cashbook_report.msg_name_graph',
                gname=evaluation.rec_name)
        return action, {}

# end OpenChartWizard
