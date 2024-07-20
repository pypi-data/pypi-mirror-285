# -*- coding: utf-8 -*-
# This file is part of the diagram-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.model import ModelView, fields
from trytond.transaction import Transaction


class EvaluationContext(ModelView):
    'Evaluation Context'
    __name__ = 'cashbook_report.evaluation.context'

    evaluation = fields.Many2One(
        string='Evaluation', readonly=True,
        model_name='cashbook_report.evaluation')

    @classmethod
    def default_evaluation(cls):
        """ get default from context
        """
        context = Transaction().context
        return context.get('evaluation', None)

# end EvaluationContext
