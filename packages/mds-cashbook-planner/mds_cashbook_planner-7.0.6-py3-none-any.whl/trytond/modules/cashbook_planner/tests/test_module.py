# -*- coding: utf-8 -*-
# This file is part of the cashbook-planner from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.tests.test_tryton import activate_module
from trytond.modules.cashbook_investment.tests.test_module import \
    CashbookInvestmentTestCase
from .planner import PlannerTestCase


class CashbookPlannerTestCase(
        PlannerTestCase,
        CashbookInvestmentTestCase):
    """ run all test from 'cashbook_investment', add test for planner
    """
    module = 'cashbook_planner'

    @classmethod
    def setUpClass(cls):
        """ activate modules
        """
        super(CashbookPlannerTestCase, cls).setUpClass()
        activate_module(['cashbook_investment'])

# end CashbookPlannerTestCase


del CashbookInvestmentTestCase
