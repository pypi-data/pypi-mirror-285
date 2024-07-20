# -*- coding: utf-8 -*-
# This file is part of the cashbook-planner from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from decimal import Decimal
from datetime import date, timedelta
from string import Template
from dateutil.rrule import (
    rrule, YEARLY, MONTHLY, WEEKLY, DAILY, MO, TU, WE, TH, FR, SA, SU)
from trytond.model import ModelSQL, ModelView, fields, Index, DeactivableMixin
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.report import Report
from trytond.i18n import gettext
from trytond.pyson import Eval, Bool, If, And
from trytond.modules.currency.fields import Monetary
from trytond.modules.cashbook.book import sel_state_book
from trytond.modules.cashbook.line import sel_bookingtype as sel_bookingtype_cb


sel_bookingtype = [
    x for x in sel_bookingtype_cb if x[0]
    in ['in', 'out', 'mvin', 'mvout']]

DEF_NONE = None
SEL_FREQU = [
    ('year', 'Yearly'),
    ('month', 'Monthly'),
    ('week', 'Weekly'),
    ('day', 'Daily')]
SEL_WEEKDAY = [
    ('99', '-'),
    ('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'),
    ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'),
    ('6', 'Sunday')]
SEL_MOVE_EVENT = [
    ('nop', 'unchanged'),
    ('before', 'Business day before original date'),
    ('after', 'Business day after original date')
]


class ScheduledBooking(DeactivableMixin, ModelSQL, ModelView):
    'Scheduled Booking'
    __name__ = 'cashbook.planner'

    company = fields.Many2One(
        string='Company', model_name='company.company',
        required=True, ondelete="RESTRICT")
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    cashbook = fields.Many2One(
        string='Cashbook', required=True,
        help='Cash book for which the planned posting is to be executed.',
        model_name='cashbook.book', ondelete='CASCADE',
        domain=[('btype', '!=', None)])
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(
        string='End Date', depends=['start_date'],
        states={'readonly': ~Bool(Eval('start_date'))},
        domain=[
            'OR',
            ('end_date', '>', Eval('start_date')),
            ('end_date', '=', DEF_NONE)])
    frequ = fields.Selection(
        string='Frequency', required=True, selection=SEL_FREQU, sort=False)
    weekday = fields.Selection(
        string='Weekday', required=True, selection=SEL_WEEKDAY, sort=False,
        help='Select a day of the week if you want the rule to ' +
        'run on that day.',
        depends=['frequ'],
        states={'invisible': Eval('frequ') != 'month'})
    COND_SETPOS = And(Eval('weekday', '') != '99', Eval('frequ') == 'month')
    setpos = fields.Integer(
        string='Occurrence', depends=['weekday', 'frequ'],
        domain=[
            If(COND_SETPOS,
               [('setpos', '<=', 4), ('setpos', '>=', 1)],
               ('setpos', '=', None))],
        help='For example, if you want to run the rule on the second ' +
        'Wednesday of the month, enter 2 here.',
        states={'required': COND_SETPOS, 'invisible': ~COND_SETPOS})
    COND_MONTHDAY = And(Eval('weekday', '') == '99', Eval('frequ') == 'month')
    monthday = fields.Integer(
        string='Day of month',
        help='If you want the rule to run on a specific day of the month, ' +
        'select the day here.',
        domain=[
            If(COND_MONTHDAY,
                [('monthday', '>=', 1), ('monthday', '<=', 31)],
                ('monthday', '=', None))],
        depends=['weekday', 'frequ'],
        states={'required': COND_MONTHDAY, 'invisible': ~COND_MONTHDAY})
    interval = fields.Integer(
        string='Interval', required=True,
        help='Select an interval to run the rule on every n-th date.',
        domain=[('interval', '>=', 1), ('interval', '<=', 10)])
    nextdates = fields.Function(fields.Char(
        string='Next Dates', readonly=True,
        help='the next 5 appointments based on the configured rule'),
        'on_change_with_nextdates')
    nextrun = fields.One2Many(
        string='Next Execution Date', size=1, field='planner',
        model_name='cashbook.planner.nextrun')
    nextrun_date = fields.Function(fields.Date(
        string='Next Execution Date', readonly=True),
        'on_change_with_nextrun_date', searcher='search_nextrun_date')
    move_event = fields.Selection(
        string='If no business day', required=True, selection=SEL_MOVE_EVENT,
        help='If the date of execution falls on a weekend or holiday, ' +
        'it can be moved to a business day.')

    bookingtype = fields.Selection(
        string='Type', selection=sel_bookingtype, required=True,
        help='Type of Booking')
    currency_cashbook = fields.Function(fields.Many2One(
        string='Currency', help='Currency of Cashbook',
        model_name='currency.currency'), 'on_change_with_currency_cashbook')
    amount = Monetary(
        string='Amount', currency='currency_cashbook',
        digits='currency_cashbook', required=True)
    category = fields.Many2One(
        string='Category', model_name='cashbook.category',
        help='Category for the planned booking', depends=['bookingtype'],
        states={
            'required': Eval('bookingtype', '').in_(['in', 'out']),
            'invisible': ~Eval('bookingtype', '').in_(['in', 'out'])})
    party = fields.Many2One(
        string='Party', model_name='party.party', depends=['bookingtype'],
        states={
            'required': Eval('bookingtype', '').in_(['in', 'out']),
            'invisible': ~Eval('bookingtype', '').in_(['in', 'out'])})
    booktransf = fields.Many2One(
        string='Source/Dest',
        ondelete='RESTRICT', model_name='cashbook.book',
        domain=[
            ('owner.id', '=', Eval('owner_cashbook', -1)),
            ('id', '!=', Eval('cashbook', -1)),
            ('btype', '!=', None)],
        states={
            'readonly': Eval('state_cashbook', '') != 'open',
            'invisible': ~Eval('bookingtype', '').in_(['mvin', 'mvout']),
            'required': Eval('bookingtype', '').in_(['mvin', 'mvout'])},
        depends=[
            'state_cashbook', 'bookingtype', 'owner_cashbook', 'cashbook'])
    owner_cashbook = fields.Function(fields.Many2One(
        string='Owner', readonly=True,
        states={'invisible': True}, model_name='res.user'),
        'on_change_with_owner_cashbook')
    state_cashbook = fields.Function(fields.Selection(
        string='State of Cashbook',
        readonly=True, states={'invisible': True}, selection=sel_state_book),
        'on_change_with_state_cashbook')
    subject = fields.Text(string='Booking text', required=True)
    wfcheck = fields.Boolean(
        string="Set to 'Checked'",
        help="Switches the booking to the 'Verified' state.")
    booking_target = fields.Function(fields.Reference(
        string='Target', selection='get_booking_modelnames', readonly=True),
        'on_change_with_booking_target')
    cashbook_lines = fields.Many2Many(
        string='Cashbook lines', relation_name='cashbook.planner_rel',
        help='This cash book lines was generated by the current ' +
        'scheduled booking.', origin='planner', target='line')

    @classmethod
    def __setup__(cls):
        super(ScheduledBooking, cls).__setup__()
        cls._order.insert(0, ('name', 'ASC'))
        cls._order.insert(0, ('nextrun_date', 'ASC'))
        t = cls.__table__()
        cls._sql_indexes.update({
            Index(
                t,
                (t.company, Index.Equality())),
            Index(
                t,
                (t.start_date, Index.Range(order='ASC'))),
            Index(
                t,
                (t.end_date, Index.Range(order='ASC')),
                where=t.end_date != DEF_NONE),
        })

    def get_rec_name(self, name=None):
        """ get formatted name of record

        Args:
            name (str, optional): name of field. Defaults to None.

        Returns:
            str: formatted description of record
        """
        return '|'.join([
            self.name,
            self.cashbook.name,
            gettext('cashbook.msg_line_bookingtype_%s' % self.bookingtype),
            self.booktransf.name
            if self.booktransf
            else self.category.rec_name if self.category else '-',
            Report.format_date(self.nextrun_date, lang=None)
            if self.nextrun_date else '-',
            Report.format_currency(
                self.amount, lang=None, currency=self.cashbook.currency)
            ])

    def _compute_dates_by_rrule(self, query_date=None, count=5, params={}):
        """ run rrule with values from record or from 'params'

        Args:
            query_date (date, optional): Start date as a filter for
                recurrences. Defaults to None.
            count (int, optional): number of recurrences in result.
                Defaults to 5. max value = 100
            params (dict, optional): Values in the dictionary are
                used instead of the stored values, Defaults to {},
                allowed: frequ, weekday, start_date,
                end_date (preferred over 'count'),
                monthday, interval, setpos, move_event

        Returns:
            list: date values, result of rrlue
        """
        def get_moved_date(xdate, m_mode):
            """ re-arrange xdate to a working day

            Args:
                xdate (date): date to move to a working day
                move_mode (str): move mode:
                    nop - no operation
                    after/before - move date to after/before input date

            Returns:
                date: re-arranged date
            """
            Config = Pool().get('cashbook.configuration')
            config = Config.get_singleton()

            assert m_mode in ['nop', 'after', 'before'], 'invalid move_mode'

            if (not config) or (m_mode == 'nop'):
                return xdate

            holidays = config.holiday_dates([xdate.year, xdate.year + 1])
            day_cnt = (
                1 if m_mode == 'after'
                else -1 if m_mode == 'before' else 0)

            if day_cnt != 0:
                while (xdate in holidays) or (xdate.weekday() in [5, 6]):
                    # re-arrange
                    xdate = xdate + timedelta(days=day_cnt)
            return xdate

        pfrequ = {
            'year': YEARLY, 'month': MONTHLY, 'week': WEEKLY, 'day': DAILY}
        pweekday = {
            '0': MO, '1': TU, '2': WE, '3': TH, '4': FR, '5': SA, '6': SU,
            '99': None}.get(params.get('weekday', self.weekday), None)

        if count is None:
            count = 5
        count = 1 if count < 1 else 100 if count > 100 else count

        end_date = params.get('end_date', self.end_date)
        frequ = pfrequ[params.get('frequ', self.frequ)]

        move_event = params.get('move_event', self.move_event)
        if move_event not in ['nop', 'before', 'after']:
            move_event = 'nop'

        setpos = params.get('setpos', self.setpos)
        if setpos is not None:
            setpos = 1 if setpos < 1 else 4 if setpos > 4 else setpos

        monthday = params.get('monthday', self.monthday)
        if monthday is not None:
            monthday = 1 if monthday < 1 else 31 if monthday > 31 else monthday

        interval = params.get('interval', self.interval)
        if interval is None:
            interval = 1
        interval = 1 if interval < 1 else 10 if interval > 10 else interval

        assert (monthday is None) or (pweekday is None), \
            "weekday and monthday cannot be used together"

        dtrule = rrule(
            freq=frequ, byweekday=pweekday,
            dtstart=params.get('start_date', self.start_date),
            until=end_date,
            bysetpos=setpos if frequ == MONTHLY else None,
            bymonthday=monthday, interval=interval)

        result = []
        for x in dtrule:
            if (query_date and (x.date() >= query_date)) or \
                    (query_date is None):
                x_date = get_moved_date(x.date(), move_event)

                # if date was re-arranged backwards and we are before
                # query_date - skip it
                if x_date >= query_date:
                    result.append(x_date)
            if len(result) >= count:
                break
        return result

    @classmethod
    def get_booking_modelnames(cls):
        """ get list of model for field 'booking_target

        Returns:
            list: list of tuple: (model_name, Description)
        """
        Model = Pool().get('ir.model')
        return [
            (x.model, x.name)
            for x in Model.search([
                ('model', 'in', ['cashbook.book', 'cashbook.category'])])]

    @fields.depends('bookingtype', 'category', 'booktransf')
    def on_change_with_booking_target(self, name=None):
        """ get category of target-cashbook

        Args:
            name (str, optional): name of field. Defaults to None.

        Returns:
            tuple: tuple with model-name and id of booking-target
        """
        if self.bookingtype in ['in', 'out']:
            if self.category:
                return '%s,%d' % (
                    self.category.__name__, self.category.id)
        elif self.bookingtype in ['mvin', 'mvout']:
            if self.booktransf:
                return '%s,%d' % (
                    self.booktransf.__name__, self.booktransf.id)

    @fields.depends('cashbook', '_parent_cashbook.currency')
    def on_change_with_currency_cashbook(self, name=None):
        """ get currency of selected cashbook

        Args:
            name (str, optional): name of field. Defaults to None.

        Returns:
            int: id of cashbook currency
        """
        if self.cashbook:
            return self.cashbook.currency.id

    @fields.depends('nextrun')
    def on_change_with_nextrun_date(self, name=None):
        """ get nextrun-record if exist

        Args:
            name (str, optional): field name. Defaults to None.

        Returns:
            date: date of nextrun or None
        """
        if self.nextrun:
            return self.nextrun[0].date
        return None

    @fields.depends(
            'start_date', 'end_date', 'frequ', 'weekday', 'monthday',
            'interval', 'setpos', 'move_event')
    def on_change_with_nextdates(self, name=None):
        """ Calculates the next 5 appointments based on the configured rule,
            returns a formatted date list

        Args:
            name (string, optional): name of field. Defaults to None.

        context:
            nextrun_querydate (date, optional): start date for dates in result,
                defaults to today if not set or None

        Returns:
            string: formatted list of dates
        """
        IrDate = Pool().get('ir.date')
        context = Transaction().context

        query_date = context.get('nextrun_querydate', None)
        if not isinstance(query_date, date):
            query_date = IrDate.today()

        return ' | '.join([
            Report.format_date(x)
            for x in self._compute_dates_by_rrule(
                query_date=query_date,
                params={
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'frequ': self.frequ,
                    'weekday': self.weekday,
                    'monthday': self.monthday,
                    'interval': self.interval,
                    'setpos': self.setpos}
            )])

    @fields.depends('cashbook', '_parent_cashbook.owner')
    def on_change_with_owner_cashbook(self, name=None):
        """ get current owner
        """
        if self.cashbook:
            return self.cashbook.owner.id

    @fields.depends('cashbook', '_parent_cashbook.state')
    def on_change_with_state_cashbook(self, name=None):
        """ get state of cashbook
        """
        if self.cashbook:
            return self.cashbook.state

    @fields.depends('bookingtype', 'category', 'booktransf')
    def on_change_bookingtype(self):
        """ reset category/booktransf on change of bookingtype
        """
        if self.bookingtype:
            if self.bookingtype in ['in', 'out']:
                self.booktransf = None
            elif self.bookingtype in ['mvin', 'mvout']:
                self.category = None

    @fields.depends('frequ', 'setpos', 'weekday', 'monthday')
    def on_change_frequ(self):
        """ update fields
        """
        if self.frequ and self.frequ == 'month':
            if self.weekday:
                if self.weekday == '99':
                    if self.monthday is None:
                        self.monthday = 1
                    self.setpos = None
                else:
                    if self.setpos is None:
                        self.setpos = 1
                    self.monthday = None
        else:
            self.setpos = None
            self.monthday = None
            self.weekday = '99'

    @fields.depends('frequ', 'setpos', 'weekday', 'monthday')
    def on_change_weekday(self):
        """ clear day-of-month if weekday is used
        """
        self.on_change_frequ()

    @staticmethod
    def order_nextrun_date(tables):
        """ get query to sort by date of next execution

        Args:
            tables (list): tables

        Returns:
            list of query: sort-query
        """
        pool = Pool()
        Nextrun = pool.get('cashbook.planner.nextrun')
        Planner2 = pool.get('cashbook.planner')
        tab_nxrun = Nextrun.__table__()
        tab_plan = Planner2.__table__()
        table, _ = tables[None]

        query = tab_plan.join(
                tab_nxrun,
                condition=tab_nxrun.planner == tab_plan.id
            ).select(
                tab_nxrun.date,
                where=tab_plan.id == table.id)
        return [query]

    @classmethod
    def search_nextrun_date(cls, name, clause):
        """ get query for search on 'nextrun_date'

        Args:
            name (str): name of field to search on
            clause (dict): search clause

        Returns:
            list of dict: search clause
        """
        return [('nextrun.date',) + tuple(clause[1:])]

    @classmethod
    def default_move_event(cls):
        """ 'no operation' as default for
            business-day occurence

        Returns:
            str: nop
        """
        return 'nop'

    @classmethod
    def default_wfcheck(cls):
        """ False as default for wf-state 'checked'

        Returns:
            bool: False
        """
        return False

    @classmethod
    def default_amount(cls):
        """ default for amount

        Returns:
            Decimal: 0.00
        """
        return Decimal('0.0')

    @classmethod
    def default_interval(cls):
        """ get default for interval

        Returns:
            int: 1 = each occurence
        """
        return 1

    @classmethod
    def default_weekday(cls):
        """ get default for weekday-rule

        Returns:
            string: '99' = not set
        """
        return '99'

    @classmethod
    def default_monthday(cls):
        """ get default for day-of-month

        Returns:
            int: 1
        """
        return 1

    @classmethod
    def default_frequ(cls):
        """ get default for frequency

        Returns:
            string: 'month'
        """
        return 'month'

    @staticmethod
    def default_company():
        return Transaction().context.get('company') or None

    @classmethod
    def default_start_date(cls):
        """ get today as start-date

        Returns:
            date: date of today
        """
        IrDate = Pool().get('ir.date')
        return IrDate.today()

    @classmethod
    def fill_placeholder(cls, linedata):
        """ replace placeholder in description

        Args:
            description (str): booking text of planned booking
        allowed substitution strings:
            ${date}, ${month}, ${year}, ${amount}, ${quantity}

        Returns:
            str: booking text
        """
        pool = Pool()
        IrDate = pool.get('ir.date')
        Cashbook = pool.get('cashbook.book')

        line_date = linedata.get('date', IrDate.today())
        amount = linedata.get('amount', None)
        from_book = linedata.get('cashbook', None)
        if from_book:
            from_book = Cashbook(from_book)
        to_book = linedata.get('booktransf', None)
        if to_book:
            to_book = Cashbook(to_book)

        quantity_txt = '-'
        quantity = linedata.get('quantity', None)
        if quantity is not None:
            uom = (
                to_book.quantity_uom if to_book and to_book.quantity_uom
                else from_book.quantity_uom
                if from_book and from_book.quantity_uom else None)
            uom_digits = (
                to_book.quantity_digits
                if to_book and to_book.quantity_digits is not None
                else from_book.quantity_digits
                if from_book and from_book.quantity_digits is not None
                else 2)
            if uom:
                quantity_txt = Report.format_number_symbol(
                    quantity, lang=None, symbol=uom, digits=uom_digits)
            else:
                quantity_txt = Report.format_number(
                    quantity, lang=None, digits=uom_digits)

        asset_rate = '-'
        if quantity and amount is not None:
            asset_rate = '%(rate)s %(currency)s/%(uom)s' % {
                'rate': Report.format_number(
                    amount / quantity, lang=None,
                    digits=to_book.currency.digits),
                'currency': to_book.currency.symbol,
                'uom': to_book.quantity_uom.symbol}

        return Template(linedata.get('description')).safe_substitute({
            'date': Report.format_date(line_date, lang=None),
            'month': line_date.month,
            'year': line_date.year,
            'amount': Report.format_currency(
                amount, lang=None, currency=from_book.currency)
            if (amount is not None) and from_book else '-',
            'quantity': quantity_txt,
            'rate': asset_rate})

    @classmethod
    def update_next_occurence(cls, records, query_date=None):
        """ compute date of next execution, create/update nextrun-record,
            delete nextrun-record if scheduled booking is disabled

        Args:
            records (list): scheduled-booking records
            query_date (date): set date to compute next run,
                defaults to 'today+1'
        """
        pool = Pool()
        IrDate = pool.get('ir.date')
        NextRun = pool.get('cashbook.planner.nextrun')
        context = Transaction().context

        if not query_date:
            query_date = context.get(
                'nextrun_querydate',
                IrDate.today() + timedelta(days=1))

        to_create = []
        to_write = []
        to_delete = []
        for record in records:
            if not record.active:
                # delete nextrun-record if disabled
                if record.nextrun:
                    to_delete.extend(record.nextrun)
            elif record.active:
                # get next-run date
                next_date = record._compute_dates_by_rrule(
                    query_date=query_date, count=1)
                if next_date:
                    next_date = next_date[0]
                else:
                    if record.nextrun:
                        to_delete.extend(record.nextrun)
                    continue

                if not record.nextrun:
                    # add record if not exist
                    to_create.append({'planner': record.id, 'date': next_date})
                else:
                    # update existing records
                    for nxrun in record.nextrun:
                        if nxrun.date != next_date:
                            to_write.extend([[nxrun], {'date': next_date}])
        if to_create:
            NextRun.create(to_create)
        if to_delete:
            NextRun.delete(to_delete)
        if to_write:
            NextRun.write(*to_write)

    @classmethod
    def create(cls, vlist):
        """ update nextrun-records on create of planner-records

        Args:
            vlist (list of dict): values to create records

        Returns:
            list: created records
        """
        records = super(ScheduledBooking, cls).create(vlist)
        cls.update_next_occurence(records)
        return records

    @classmethod
    def write(cls, *args):
        """ update nextrun-records on create of planner-records
        """
        to_update = []
        actions = iter(args)
        for records, values in zip(actions, actions):
            to_update.extend(records)
        super(ScheduledBooking, cls).write(*args)
        cls.update_next_occurence(records)

    @classmethod
    def run_booking(cls, records):
        """ create planned bookings

        Args:
            records (list): list of planned bokings
        """
        pool = Pool()
        IrDate = pool.get('ir.date')
        Line = pool.get('cashbook.line')
        Currency = pool.get('currency.currency')

        def add_asset_values(aline, from_book, to_book):
            """ compute quantity from rate of asset and
                amount to invest

            Args:
                aline (dict): prepared dictionary to create
                    cashbook-line-record
                from_book (record): cashbook record,
                to_book (record): cashbook record

            Returns:
                dict: dictionary to create cashbook-line record
            """
            with Transaction().set_context({'date': aline['date']}):
                # convert amount to target-currency
                target_amount = Currency.compute(
                    from_book.currency, aline['amount'],
                    to_book.currency, round=False)
                # convert asset-rate of target-cashbook to target-currency
                asset_rate = (Currency.compute(
                    to_book.asset.currency, to_book.asset.rate,
                    to_book.currency, round=False) * Decimal(
                        to_book.asset.uom.factor /
                        to_book.quantity_uom.factor))

                aline['quantity'] = Decimal('0.0')
                if asset_rate:
                    aline['quantity'] = (target_amount / asset_rate).quantize(
                        Decimal(Decimal(1) / 10 ** to_book.quantity_digits))
            return aline

        to_create = []
        to_create_check = []
        for record in records:
            line = {
                'cashbook': record.cashbook.id,
                'bookingtype': record.bookingtype,
                'date': IrDate.today(),
                'amount': record.amount,
                'description': record.subject}

            if record.bookingtype in ['in', 'out']:
                if record.category:
                    line['category'] = record.category.id
                if record.party:
                    line['party'] = record.party.id
            elif record.bookingtype in ['mvin', 'mvout']:
                if record.booktransf:
                    line['booktransf'] = record.booktransf.id
                    if record.booktransf.feature == 'asset':
                        line.update(add_asset_values(
                            line, record.cashbook, record.booktransf))
            line['description'] = cls.fill_placeholder(line)
            line['planners'] = [('add', [record.id])]

            if record.wfcheck:
                to_create_check.append(line)
            else:
                to_create.append(line)

        if to_create_check:
            lines = Line.create(to_create_check)
            Line.wfcheck(lines)
        if to_create:
            Line.create(to_create)

    @classmethod
    def cronjob(cls):
        """ run planned booking for due jobs, re-schedule for next runs
        """
        IrDate = Pool().get('ir.date')
        context = Transaction().context

        query_date = context.get('nextrun_crondate', IrDate.today())
        records = cls.search([
            ('active', '=', True),
            ('nextrun.date', '<=', query_date)])

        if records:
            cls.run_booking(records)
            cls.update_next_occurence(
                records,
                query_date=query_date + timedelta(days=1))

# end ScheduledBooking


class ScheduledBookingCashbookRel(ModelSQL):
    'Scheduled Booking - Cashbook Line - Relation'
    __name__ = 'cashbook.planner_rel'

    planner = fields.Many2One(
        string='Scheduled Booking', required=True,
        model_name='cashbook.planner', ondelete='CASCADE')
    line = fields.Many2One(
        string='Cashbook Line', required=True,
        model_name='cashbook.line', ondelete='CASCADE')

# end ScheduledBookingCashbookRel
