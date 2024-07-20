# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.pool import Pool
from .evaluation import Evaluation
from .line import EvaluationLine
from .currency import Currency
from .evaluation_context import EvaluationContext
from .evaluation_wizard import OpenChartWizard
from .investment import InvestmentEvaluation, InvestmentLine
from .ir import Rule, IrActWindow


def register():
    Pool.register(
        Currency,
        Evaluation,
        EvaluationLine,
        EvaluationContext,
        Rule,
        IrActWindow,
        module='cashbook_report', type_='model')
    Pool.register(
        OpenChartWizard,
        module='cashbook_report', type_='wizard')
    Pool.register(
        InvestmentEvaluation,
        InvestmentLine,
        module='cashbook_report',
        type_='model',
        depends=['cashbook_investment'])
