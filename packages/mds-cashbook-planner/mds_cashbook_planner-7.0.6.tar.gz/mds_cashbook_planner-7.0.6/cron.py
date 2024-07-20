# -*- coding: utf-8 -*-
# This file is part of the cashbook-planner from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.pool import PoolMeta


class Cron(metaclass=PoolMeta):
    __name__ = 'ir.cron'

    @classmethod
    def __setup__(cls):
        super(Cron, cls).__setup__()
        cls.method.selection.append(
            ('cashbook.planner|cronjob', "Execute scheduled bookings"))

# end Cron
