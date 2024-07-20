# -*- coding: utf-8 -*-
# This file is part of the cashbook-planner from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.


from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Eval, Bool


class Cashbook(metaclass=PoolMeta):
    __name__ = 'cashbook.book'

    planner = fields.One2Many(
        string='Scheduled Bookings', model_name='cashbook.planner',
        field='cashbook', depends=['btype'],
        states={'invisible': ~Bool(Eval('btype'))})

# end Cashbook


class CashbookLine(metaclass=PoolMeta):
    __name__ = 'cashbook.line'

    planners = fields.Many2Many(
        string='Scheduled Bookings', relation_name='cashbook.planner_rel',
        origin='line', target='planner')

# end CashbookLine
