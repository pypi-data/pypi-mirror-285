# -*- coding: utf-8 -*-
# This file is part of the cashbook-planner from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.model import ModelSQL, ModelView, fields
from trytond.report import Report


class NextRun(ModelSQL, ModelView):
    'Next Execution Date'
    __name__ = 'cashbook.planner.nextrun'

    planner = fields.Many2One(
        string='Planner', required=True, ondelete='CASCADE',
        model_name='cashbook.planner', readonly=True)
    date = fields.Date(string='Date', required=True, readonly=True)

    def get_rec_name(self, name):
        """ get date for record name

        Args:
            name (string): name of field

        Returns:
            string: formatted date
        """
        return Report.format_date(self.date) if self.date is not None else '-'

# end NextRun
