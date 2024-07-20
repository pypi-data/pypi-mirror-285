# -*- coding: utf-8 -*-
# This file is part of the cashbook-planner from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from decimal import Decimal
from unittest.mock import MagicMock
from trytond.tests.test_tryton import with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError

from datetime import date


class PlannerTestCase(object):
    """ test planner
    """
    def prep_create_job(self, name='Job 1'):
        pool = Pool()
        Book = pool.get('cashbook.book')
        Planner = pool.get('cashbook.planner')
        Party = pool.get('party.party')

        types = self.prep_type()
        company = self.prep_company()
        job = None
        with Transaction().set_context({
                'company': company.id,
                'nextrun_querydate': date(2022, 5, 1)}):
            book, = Book.create([{
                'name': 'Book 1',
                'btype': types.id,
                'company': company.id,
                'currency': company.currency.id,
                'number_sequ': self.prep_sequence().id,
                'start_date': date(2022, 5, 1),
                }])
            self.assertEqual(
                book.rec_name,
                'Book 1 | 0.00 %s | Open' % company.currency.symbol)

            category = self.prep_category()
            party, = Party.create([{
                'name': 'Party',
                'addresses': [('create', [{}])]}])
            job, = Planner.create([{
                'cashbook': book.id,
                'name': name,
                'start_date': date(2022, 5, 1),
                'bookingtype': 'out',
                'category': category.id,
                'party': party.id,
                'subject': 'Booking text'}])
            # check applied defaults
            self.assertEqual(job.start_date, date(2022, 5, 1))
            self.assertEqual(job.end_date, None)
            self.assertEqual(job.frequ, 'month')
            self.assertEqual(job.weekday, '99')
            self.assertEqual(job.monthday, 1)
            self.assertEqual(job.interval, 1)
            self.assertEqual(job.setpos, None)
            self.assertEqual(job.move_event, 'nop')
            self.assertEqual(
                job.nextdates,
                '05/01/2022 | 06/01/2022 | 07/01/2022 | 08/01/2022 |' +
                ' 09/01/2022')
        return job

    def prep_planner_asset_book(self):
        """ prepare asset-cashbook
        """
        pool = Pool()
        Asset = pool.get('investment.asset')
        Book = pool.get('cashbook.book')
        BType = pool.get('cashbook.type')

        company = self.prep_company()
        with Transaction().set_context({'company': company.id}):
            type_depot = self.prep_type('Depot', 'D')
            BType.write(*[[type_depot], {'feature': 'asset'}])

            asset = self.prep_asset_item(
                company=company,
                product=self.prep_asset_product(name='Product 1'))
            self.assertEqual(asset.symbol, 'usd/u')
            self.assertEqual(company.currency.symbol, 'usd')

            Asset.write(*[
                [asset],
                {
                    'rates': [('create', [{
                        'date': date(2022, 5, 1),
                        'rate': Decimal('10.0'),
                        }, {
                        'date': date(2022, 5, 2),
                        'rate': Decimal('12.5'),
                        }])],
                }])
            self.assertEqual(
                asset.rec_name, 'Product 1 | 12.5000 usd/u | 05/02/2022')

            book, = Book.create([{
                'name': 'Depot',
                'btype': type_depot.id,
                'company': company.id,
                'currency': company.currency.id,
                'number_sequ': self.prep_sequence().id,
                'start_date': date(2022, 5, 1),
                'asset': asset.id,
                'quantity_uom': asset.uom.id,
                }])
            self.prep_valstore_run_worker()
            self.assertEqual(
                book.rec_name,
                'Depot | 0.00 usd | Open | 0.0000 u')
        return book

    @with_transaction()
    def test_func_holiday_parseconfig(self):
        """ check function holiday_parseconfig()
        """
        Config = Pool().get('cashbook.configuration')

        company = self.prep_company()
        with Transaction().set_context({'company': company.id}):
            # check valid data
            result = Config.holiday_parseconfig(
                '2022-05-01;12-25;12-25:+1;easter;easter:-2;easterjul;' +
                'ascension;whitsun;whitsun:+1;',
                [2022, 2023, 2024])
            self.assertEqual(result, {
                'definition': '2022-05-01;12-25;12-25:+1;easter;easter:-2;' +
                'easterjul;ascension;whitsun;whitsun:+1',
                'dates': [
                    date(2022, 5, 1), date(2022, 12, 25), date(2023, 12, 25),
                    date(2024, 12, 25), date(2022, 12, 26), date(2023, 12, 26),
                    date(2024, 12, 26), date(2022, 4, 17), date(2023, 4, 9),
                    date(2024, 3, 31), date(2022, 4, 15), date(2023, 4, 7),
                    date(2024, 3, 29), date(2022, 4, 11), date(2023, 4, 3),
                    date(2024, 4, 22), date(2022, 5, 26), date(2023, 5, 18),
                    date(2024, 5, 9), date(2022, 6, 5), date(2023, 5, 28),
                    date(2024, 5, 19), date(2022, 6, 6), date(2023, 5, 29),
                    date(2024, 5, 20)]})

            # check invalid data
            self.assertEqual(
                Config.holiday_parseconfig('not-a-value;'),
                {'definition': '', 'dates': []})

            # check no data
            self.assertEqual(
                Config.holiday_parseconfig(''),
                {'definition': '', 'dates': []})
            self.assertEqual(
                Config.holiday_parseconfig(None),
                {'definition': '', 'dates': []})

            with Transaction().set_context({'holiday_years': [2022]}):
                cfg1 = Config(holidays='2022-05-01;easter;whitsun')
                cfg1.save()
                self.assertEqual(
                    cfg1.holiday_dates([2022]),
                    [date(2022, 5, 1), date(2022, 4, 17), date(2022, 6, 5)])
                self.assertEqual(
                    cfg1.holidays_info,
                    '04/17/2022|05/01/2022|06/05/2022')

    @with_transaction()
    def test_planner_create_job(self):
        """ create job, check rule + constraints
        """
        pool = Pool()
        Planner = pool.get('cashbook.planner')
        Config = pool.get('cashbook.configuration')

        job = self.prep_create_job()
        self.assertEqual(
            job._compute_dates_by_rrule(
                query_date=date(2022, 5, 1), count=5), [
                date(2022, 5, 1), date(2022, 6, 1),
                date(2022, 7, 1), date(2022, 8, 1),
                date(2022, 9, 1)])

        self.assertRaisesRegex(
            UserError,
            r'The value "2022-05-01" for field "End Date" in ' +
            r'"Job 1|Book 1|Exp|Cat1|05/01/2022|usd0.00" of ' +
            r'"Scheduled Booking" is not valid according to its domain\.',
            Planner.write,
            *[[job],  {'end_date': date(2022, 5, 1)}])

        self.assertEqual(job.booking_target.name, 'Cat1')
        Planner.write(*[[job],  {
            'end_date': date(2022, 9, 15), 'monthday': 3}])
        self.assertEqual(
            job._compute_dates_by_rrule(query_date=date(2022, 5, 1)), [
                date(2022, 5, 3), date(2022, 6, 3),
                date(2022, 7, 3), date(2022, 8, 3),
                date(2022, 9, 3)])

        Planner.write(*[[job],  {
            'end_date': date(2022, 9, 15), 'monthday': 3, 'interval': 2}])
        self.assertEqual(
            job._compute_dates_by_rrule(query_date=date(2022, 5, 1)), [
                date(2022, 5, 3), date(2022, 7, 3),
                date(2022, 9, 3)])

        # 3rd of each 2nd month
        Planner.write(*[[job],  {
            'end_date': None, 'monthday': 1, 'interval': 1}])
        self.assertEqual(
            job._compute_dates_by_rrule(
                query_date=date(2022, 5, 1),
                params={
                    'end_date': date(2022, 9, 15), 'monthday': 3,
                    'interval': 2}),
            [date(2022, 5, 3), date(2022, 7, 3), date(2022, 9, 3)])

        # 1st wednesday of each 2nd month
        self.assertEqual(
            job._compute_dates_by_rrule(
                query_date=date(2022, 5, 1),
                params={
                    'end_date': date(2022, 9, 15), 'weekday': '2',
                    'interval': 2, 'setpos': 1, 'monthday': None}),
            [date(2022, 5, 4), date(2022, 7, 6), date(2022, 9, 7)])

        # 2nd wednesday of each 2nd month
        self.assertEqual(
            job._compute_dates_by_rrule(
                query_date=date(2022, 5, 1),
                params={
                    'end_date': date(2022, 9, 15), 'weekday': '2',
                    'interval': 2, 'setpos': 2, 'monthday': None}),
            [date(2022, 5, 11), date(2022, 7, 13), date(2022, 9, 14)])

        # 2nd wednesday of each month, 6x occurences
        self.assertEqual(
            job._compute_dates_by_rrule(
                query_date=date(2022, 5, 1), count=6,
                params={
                    'weekday': '2', 'end_date': None,
                    'interval': 1, 'setpos': 2, 'monthday': None}),
            [date(2022, 5, 11), date(2022, 6, 8), date(2022, 7, 13),
                date(2022, 8, 10), date(2022, 9, 14), date(2022, 10, 12)])

        # set up holidays
        cfg1 = Config(
            holidays='01-01;05-01;easter:+1;easter:-2;ascension;whitsun:+1')
        cfg1.save()
        # 1st of may, should be moved to 2nd of may
        self.assertEqual(
            job._compute_dates_by_rrule(
                query_date=date(2022, 4, 25), count=3,
                params={
                    'end_date': None, 'start_date': date(2022, 5, 1),
                    'move_event': 'after', 'weekday': None,
                    'setpos': None, 'interval': 1, 'frequ': 'year',
                    'monthday': None}),
            [date(2022, 5, 2), date(2023, 5, 2), date(2024, 5, 2)])
        # easter of 2022, occurence-date moved to tuesday after easter'22
        self.assertEqual(
            job._compute_dates_by_rrule(
                query_date=date(2022, 4, 10), count=3,
                params={
                    'end_date': None, 'start_date': date(2022, 4, 17),
                    'move_event': 'after', 'weekday': None,
                    'setpos': None,
                    'interval': 1, 'frequ': 'month', 'monthday': None}),
            [date(2022, 4, 19), date(2022, 5, 17), date(2022, 6, 17)])
        # easter of 2022, monthly, occurence-date moved to
        # thursday before easter'22
        self.assertEqual(
            job._compute_dates_by_rrule(
                query_date=date(2022, 4, 10), count=3,
                params={
                    'end_date': None, 'start_date': date(2022, 4, 17),
                    'move_event': 'before', 'weekday': None,
                    'setpos': None,
                    'interval': 1, 'frequ': 'month', 'monthday': None}),
            [date(2022, 4, 14), date(2022, 5, 17), date(2022, 6, 17)])
        # easter of 2022, monthly, check next occurence after easter
        # recompute date at moved occurence-date+1
        self.assertEqual(
            job._compute_dates_by_rrule(
                query_date=date(2022, 4, 15), count=3,
                params={
                    'end_date': None, 'start_date': date(2022, 4, 17),
                    'move_event': 'before', 'weekday': None,
                    'setpos': None,
                    'interval': 1, 'frequ': 'month', 'monthday': None}),
            [date(2022, 5, 17), date(2022, 6, 17), date(2022, 7, 15)])

        Planner.write(*[[job],  {
            'frequ': 'year', 'start_date': date(2022, 5, 1),
            'setpos': None, 'monthday': None, 'interval': 1,
            'weekday': '99'}])

        # invalid end_date
        self.assertRaisesRegex(
            UserError,
            'The value "2022-04-30" for field "End Date" in ' +
            '"Job 1|Book 1|Exp|Cat1|05/01/2024|usd0.00" of ' +
            '"Scheduled Booking" is not valid according to its domain.',
            Planner.write,
            *[[job],  {
                'frequ': 'year', 'start_date': date(2022, 5, 1),
                'end_date': date(2022, 4, 30)}])

        # monthday and weekday used together
        self.assertRaisesRegex(
            UserError,
            'The value "2" for field "Day of month" in ' +
            '"Job 1|Book 1|Exp|Cat1|05/01/2024|usd0.00" of ' +
            '"Scheduled Booking" is not valid according to its domain.',
            Planner.write,
            *[[job],  {
                'frequ': 'month', 'start_date': date(2022, 5, 1),
                'monthday': 2, 'weekday': '1', 'end_date': None}])

        # monthday out of range 1
        self.assertRaisesRegex(
            UserError,
            'The value "0" for field "Day of month" in ' +
            '"Job 1|Book 1|Exp|Cat1|05/01/2024|usd0.00" of ' +
            '"Scheduled Booking" is not valid according to its domain.',
            Planner.write,
            *[[job],  {
                'frequ': 'year', 'start_date': date(2022, 5, 1),
                'monthday': 0, 'weekday': '99', 'end_date': None}])

        # monthday out of range 2
        self.assertRaisesRegex(
            UserError,
            'The value "32" for field "Day of month" in ' +
            '"Job 1|Book 1|Exp|Cat1|05/01/2024|usd0.00" of ' +
            '"Scheduled Booking" is not valid according to its domain.',
            Planner.write,
            *[[job],  {
                'frequ': 'year', 'start_date': date(2022, 5, 1),
                'monthday': 32, 'weekday': '99', 'end_date': None}])

        # invalid usage of setpos
        self.assertRaisesRegex(
            UserError,
            'The value "1" for field "Occurrence" in ' +
            '"Job 1|Book 1|Exp|Cat1|05/01/2024|usd0.00" of ' +
            '"Scheduled Booking" is not valid according to its domain.',
            Planner.write,
            *[[job],  {
                'frequ': 'year', 'start_date': date(2022, 5, 1),
                'setpos': 1, 'monthday': None, 'weekday': '99',
                'end_date': None}])

        # setpos out of range 1
        self.assertRaisesRegex(
            UserError,
            'The value "0" for field "Occurrence" in ' +
            '"Job 1|Book 1|Exp|Cat1|05/01/2024|usd0.00" of ' +
            '"Scheduled Booking" is not valid according to its domain.',
            Planner.write,
            *[[job],  {
                'frequ': 'month', 'start_date': date(2022, 5, 1),
                'setpos': 0, 'monthday': None, 'weekday': '2',
                'end_date': None}])

        # setpos out of range 2
        self.assertRaisesRegex(
            UserError,
            'The value "5" for field "Occurrence" in ' +
            '"Job 1|Book 1|Exp|Cat1|05/01/2024|usd0.00" of ' +
            '"Scheduled Booking" is not valid according to its domain.',
            Planner.write,
            *[[job],  {
                'frequ': 'month', 'start_date': date(2022, 5, 1),
                'setpos': 5, 'monthday': None, 'weekday': '2',
                'end_date': None}])

    @with_transaction()
    def test_planner_create_update_nextrun(self):
        """ create job, check nextrun-record
        """
        Planner = Pool().get('cashbook.planner')

        job = self.prep_create_job()
        self.assertEqual(
            job._compute_dates_by_rrule(
                count=1, query_date=date(2022, 5, 1)), [
                date(2022, 5, 1)])

        Planner.update_next_occurence([job], query_date=date(2022, 5, 25))
        self.assertEqual(len(job.nextrun), 1)
        self.assertEqual(job.nextrun[0].date, date(2022, 6, 1))
        self.assertEqual(job.nextrun_date, date(2022, 6, 1))

        # check searcher + order
        self.assertEqual(
            Planner.search(
                [('nextrun_date', '=', date(2022, 6, 1))],
                order=[('nextrun_date', 'ASC')]),
            [job])
        self.assertEqual(
            Planner.search_count([('nextrun_date', '=', date(2022, 6, 1))]),
            1)
        self.assertEqual(
            Planner.search_count([('nextrun_date', '=', date(2022, 6, 2))]),
            0)

        Planner.update_next_occurence([job], query_date=date(2022, 5, 30))
        self.assertEqual(len(job.nextrun), 1)
        self.assertEqual(job.nextrun[0].date, date(2022, 6, 1))

        Planner.update_next_occurence([job], query_date=date(2022, 6, 1))
        self.assertEqual(len(job.nextrun), 1)
        self.assertEqual(job.nextrun[0].date, date(2022, 6, 1))

        # cron will use 'today+1' as query_date
        Planner.update_next_occurence([job], query_date=date(2022, 6, 2))
        self.assertEqual(len(job.nextrun), 1)
        self.assertEqual(job.nextrun[0].date, date(2022, 7, 1))

        with Transaction().set_context({
                'nextrun_querydate': date(2022, 6, 2)}):
            # set end-date to check delete of future runs
            Planner.write(*[[job], {'end_date': date(2022, 6, 20)}])
            # write to planner-record updates nextrun-records too
            self.assertEqual(len(job.nextrun), 0)

    @with_transaction()
    def test_planner_run_cronjobs(self):
        """ create job, check cron
        """
        pool = Pool()
        Planner = pool.get('cashbook.planner')
        IrDate = pool.get('ir.date')

        job = self.prep_create_job()
        self.assertEqual(
            job._compute_dates_by_rrule(
                count=1, query_date=date(2022, 5, 1)), [
                date(2022, 5, 1)])

        # job was not yet run after configure
        IrDate.today = MagicMock(return_value=date(2022, 5, 24))
        Planner.run_booking = MagicMock()
        job, = Planner.search([])
        self.assertEqual(job.nextrun[0].date, date(2022, 5, 1))
        Planner.cronjob()
        self.assertEqual(job.nextrun[0].date, date(2022, 6, 1))
        Planner.run_booking.assert_called_with([job])

        # next call before due date - nothing should happen
        IrDate.today = MagicMock(return_value=date(2022, 5, 30))
        Planner.run_booking = MagicMock()   # restart mock
        self.assertEqual(job.nextrun[0].date, date(2022, 6, 1))
        Planner.cronjob()
        self.assertEqual(job.nextrun[0].date, date(2022, 6, 1))
        Planner.run_booking.assert_not_called()

        # next call at due date - calls booking and set due date
        IrDate.today = MagicMock(return_value=date(2022, 6, 1))
        Planner.run_booking = MagicMock()   # restart mock
        self.assertEqual(job.nextrun[0].date, date(2022, 6, 1))
        Planner.cronjob()
        self.assertEqual(job.nextrun[0].date, date(2022, 7, 1))
        Planner.run_booking.assert_called_with([job])

        IrDate.today = MagicMock(return_value=date.today())

    @with_transaction()
    def test_planner_check_description_template(self):
        """ check replacement of template strings in description
        """
        pool = Pool()
        Planner = pool.get('cashbook.planner')

        asset_book = self.prep_planner_asset_book()
        self.assertEqual(Planner.fill_placeholder({
            'date': date(2022, 5, 2),
            'amount': Decimal('126.4567'),
            'quantity': Decimal('32.4423'),
            'cashbook': asset_book.id,
            'booktransf': asset_book.id,
            'description': '- ${amount} - ${date} - ${month} - ' +
            '${year} - ${quantity} - ${rate}'}),
            '- usd126.46 - 05/02/2022 - 5 - 2022 - 32.4423\xa0u - 3.90 usd/u')

    @with_transaction()
    def test_planner_cronjobs_booking_with_category(self):
        """ create job, configure booking with category, run job
        """
        pool = Pool()
        Planner = pool.get('cashbook.planner')
        IrDate = pool.get('ir.date')
        Category = pool.get('cashbook.category')
        Cashbook = pool.get('cashbook.book')

        job = self.prep_create_job()
        self.assertEqual(
            job._compute_dates_by_rrule(
                count=1, query_date=date(2022, 5, 1)), [
                date(2022, 5, 1)])

        IrDate.today = MagicMock(return_value=date(2022, 5, 24))

        category, = Category.search([('name', '=', 'Cat1')])
        Planner.write(*[
            [job],
            {
                'name': 'Booking to category',
                'amount': Decimal('10.0'),
                'bookingtype': 'out',
                'category': category.id,
                'subject': 'booking ${month}/${year}, ${date}',
                'wfcheck': True}])
        self.assertEqual(
            job.rec_name,
            'Booking to category|Book 1|Exp|Cat1|06/01/2022|usd10.00')
        self.assertEqual(job.cashbook.rec_name, 'Book 1 | 0.00 usd | Open')
        self.assertEqual(len(job.cashbook.lines), 0)

        job, = Planner.search([])
        self.assertEqual(job.nextrun[0].date, date(2022, 6, 1))
        self.assertEqual(len(job.cashbook_lines), 0)

        IrDate.today = MagicMock(return_value=date(2022, 6, 1))
        Planner.cronjob()
        self.assertEqual(job.nextrun[0].date, date(2022, 7, 1))
        self.assertEqual(len(job.cashbook_lines), 1)
        self.assertEqual(
            job.cashbook_lines[0].rec_name,
            '06/01/2022|Exp|-10.00 usd|booking 6/2022, 06/01/2022 [Cat1]')

        # check cashbook
        self.assertEqual(len(job.cashbook.lines), 1)
        self.assertEqual(len(job.cashbook.lines[0].planners), 1)
        self.assertEqual(job.cashbook.lines[0].planners[0].id, job.id)

        self.assertEqual(
            job.cashbook.lines[0].rec_name,
            "06/01/2022|Exp|-10.00 usd|booking 6/2022, 06/01/2022 [Cat1]")
        self.assertEqual(job.cashbook.lines[0].state, 'check')

        with Transaction().set_context({'date': date(2022, 6, 1)}):
            cashbook, = Cashbook.browse([job.cashbook])
            self.assertEqual(cashbook.rec_name, 'Book 1 | -10.00 usd | Open')

        IrDate.today = MagicMock(return_value=date.today())

    @with_transaction()
    def test_planner_cronjobs_booking_transfer_nonasset(self):
        """ create job, configure transfer-booking to non-asset-cashbook,
            run job
        """
        pool = Pool()
        Planner = pool.get('cashbook.planner')
        IrDate = pool.get('ir.date')
        Category = pool.get('cashbook.category')
        Cashbook = pool.get('cashbook.book')

        company = self.prep_company()
        with Transaction().set_context({'company': company.id}):
            job = self.prep_create_job()
            target_book, = Cashbook.create([{
                'name': 'Book 2',
                'btype': job.cashbook.btype.id,
                'company': company.id,
                'currency': company.currency.id,
                'number_sequ': self.prep_sequence().id,
                'start_date': date(2022, 5, 1)}])
            self.assertEqual(target_book.rec_name, 'Book 2 | 0.00 usd | Open')
            self.assertEqual(len(target_book.lines), 0)

        IrDate.today = MagicMock(return_value=date(2022, 5, 24))

        category, = Category.search([('name', '=', 'Cat1')])
        Planner.write(*[
            [job],
            {
                'name': 'Transfer to Book-2',
                'amount': Decimal('10.0'),
                'bookingtype': 'mvout',
                'category': category.id,
                'subject': 'booking ${month}/${year}, ${date}',
                'booktransf': target_book.id,
                'wfcheck': True}])
        self.assertEqual(
            job.rec_name,
            'Transfer to Book-2|Book 1|to|Book 2|06/01/2022|usd10.00')
        self.assertEqual(job.cashbook.rec_name, 'Book 1 | 0.00 usd | Open')
        self.assertEqual(job.booktransf.rec_name, 'Book 2 | 0.00 usd | Open')
        self.assertEqual(len(job.cashbook.lines), 0)
        self.assertEqual(job.booking_target.name, 'Book 2')

        job, = Planner.search([])
        self.assertEqual(job.nextrun[0].date, date(2022, 6, 1))
        IrDate.today = MagicMock(return_value=date(2022, 6, 1))
        Planner.cronjob()
        self.assertEqual(job.nextrun[0].date, date(2022, 7, 1))

        # check both cashbooks
        with Transaction().set_context({'date': date(2022, 6, 1)}):
            cashbook, = Cashbook.browse([job.cashbook])
            self.assertEqual(cashbook.rec_name, 'Book 1 | -10.00 usd | Open')
            self.assertEqual(len(cashbook.lines), 1)
            self.assertEqual(
                cashbook.lines[0].rec_name,
                "06/01/2022|to|-10.00 usd|booking 6/2022, 06/01/2022 " +
                "[Book 2 | 10.00 usd | Open]")
            self.assertEqual(cashbook.lines[0].state, 'check')

            target_book, = Cashbook.browse([job.booktransf])
            self.assertEqual(target_book.rec_name, 'Book 2 | 10.00 usd | Open')
            self.assertEqual(len(target_book.lines), 1)
            self.assertEqual(
                target_book.lines[0].rec_name,
                "06/01/2022|from|10.00 usd|booking 6/2022, 06/01/2022 " +
                "[Book 1 | -10.00 usd | Open]")
            self.assertEqual(target_book.lines[0].state, 'check')
        self.assertEqual(target_book.lines[0].state, 'check')

        IrDate.today = MagicMock(return_value=date.today())

    @with_transaction()
    def test_planner_cronjobs_booking_transfer_nonasset_usd_eur(self):
        """ create job, configure transfer-booking to non-asset-cashbook,
            from usd to eur, run job
        """
        pool = Pool()
        Planner = pool.get('cashbook.planner')
        IrDate = pool.get('ir.date')
        Category = pool.get('cashbook.category')
        Cashbook = pool.get('cashbook.book')

        company = self.prep_company()
        with Transaction().set_context({'company': company.id}):
            (usd, euro) = self.prep_2nd_currency(company)
            self.assertEqual(len(usd.rates), 1)
            self.assertEqual(usd.rates[0].rate, Decimal('1.05'))
            self.assertEqual(usd.rates[0].date, date(2022, 5, 2))
            self.assertEqual(euro.rates[0].rate, Decimal('1.0'))
            self.assertEqual(euro.rates[0].date, date(2022, 5, 2))
            self.assertEqual(company.currency.rec_name, 'Euro')

            job = self.prep_create_job()
            target_book, = Cashbook.create([{
                'name': 'Book 2',
                'btype': job.cashbook.btype.id,
                'company': company.id,
                'currency': usd.id,
                'number_sequ': self.prep_sequence().id,
                'start_date': date(2022, 5, 1)}])
            self.assertEqual(target_book.rec_name, 'Book 2 | 0.00 usd | Open')
            self.assertEqual(len(target_book.lines), 0)

        IrDate.today = MagicMock(return_value=date(2022, 5, 24))

        category, = Category.search([('name', '=', 'Cat1')])
        Planner.write(*[
            [job],
            {
                'name': 'Transfer to Book-2',
                'amount': Decimal('10.0'),
                'bookingtype': 'mvout',
                'category': category.id,
                'subject': 'booking 10 € --> 10.5 usd',
                'booktransf': target_book.id,
                'wfcheck': True}])
        self.assertEqual(
            job.rec_name,
            'Transfer to Book-2|Book 1|to|Book 2|06/01/2022|€10.00')
        self.assertEqual(job.cashbook.rec_name, 'Book 1 | 0.00 € | Open')
        self.assertEqual(job.booktransf.rec_name, 'Book 2 | 0.00 usd | Open')
        self.assertEqual(len(job.cashbook.lines), 0)

        job, = Planner.search([])
        self.assertEqual(job.nextrun[0].date, date(2022, 6, 1))
        IrDate.today = MagicMock(return_value=date(2022, 6, 1))
        Planner.cronjob()
        self.assertEqual(job.nextrun[0].date, date(2022, 7, 1))

        # check both cashbooks
        with Transaction().set_context({'date': date(2022, 6, 1)}):
            cashbook, = Cashbook.browse([job.cashbook])
            self.assertEqual(cashbook.rec_name, 'Book 1 | -10.00 € | Open')
            self.assertEqual(len(cashbook.lines), 1)
            self.assertEqual(
                cashbook.lines[0].rec_name,
                "06/01/2022|to|-10.00 €|booking 10 € --> 10.5 usd" +
                " [Book 2 | 10.50 usd | Open]")
            self.assertEqual(cashbook.lines[0].state, 'check')

            target_book, = Cashbook.browse([job.booktransf])
            self.assertEqual(target_book.rec_name, 'Book 2 | 10.50 usd | Open')
            self.assertEqual(len(target_book.lines), 1)
            self.assertEqual(
                target_book.lines[0].rec_name,
                "06/01/2022|from|10.50 usd|booking 10 € --> 10.5 usd" +
                " [Book 1 | -10.00 € | Open]")
            self.assertEqual(target_book.lines[0].state, 'check')
        self.assertEqual(target_book.lines[0].state, 'check')

        IrDate.today = MagicMock(return_value=date.today())

    @with_transaction()
    def test_planner_cronjobs_booking_transfer_asset(self):
        """ create job, configure transfer-booking to asset-cashbook,
            same currencies between cashbooks,
            same units between asset and cashbook
        """
        pool = Pool()
        Planner = pool.get('cashbook.planner')
        IrDate = pool.get('ir.date')
        Category = pool.get('cashbook.category')
        Cashbook = pool.get('cashbook.book')

        company = self.prep_company()
        with Transaction().set_context({'company': company.id}):
            job = self.prep_create_job()
            # rate of asset = 12.5 usd
            asset_book = self.prep_planner_asset_book()
            self.assertEqual(
                asset_book.rec_name,
                'Depot | 0.00 usd | Open | 0.0000 u')
            self.assertEqual(len(asset_book.lines), 0)

        IrDate.today = MagicMock(return_value=date(2022, 5, 24))

        category, = Category.search([('name', '=', 'Cat1')])
        Planner.write(*[
            [job],
            {
                'name': 'buy asset',
                'amount': Decimal('10.0'),
                'bookingtype': 'mvout',
                'category': category.id,
                'subject': 'invest 10.00 usd to buy 0.80 units',
                'booktransf': asset_book.id,
                'wfcheck': True}])
        self.assertEqual(
            job.rec_name,
            'buy asset|Book 1|to|Depot|06/01/2022|usd10.00')
        self.assertEqual(job.cashbook.rec_name, 'Book 1 | 0.00 usd | Open')
        self.assertEqual(
            job.booktransf.rec_name,
            'Depot | 0.00 usd | Open | 0.0000 u')
        self.assertEqual(len(job.cashbook.lines), 0)

        # check both cashbooks
        with Transaction().set_context({'date': date(2022, 6, 1)}):
            job, = Planner.search([])
            self.assertEqual(job.nextrun[0].date, date(2022, 6, 1))
            IrDate.today = MagicMock(return_value=date(2022, 6, 1))
            Planner.cronjob()
            self.assertEqual(job.nextrun[0].date, date(2022, 7, 1))

            cashbook, = Cashbook.browse([job.cashbook])
            self.assertEqual(cashbook.rec_name, 'Book 1 | -10.00 usd | Open')
            self.assertEqual(len(cashbook.lines), 1)
            self.assertEqual(
                cashbook.lines[0].rec_name,
                "06/01/2022|to|-10.00 usd|invest 10.00 usd to buy 0.80 " +
                "units [Depot | 10.00 usd | Open | 0.8000 u]")
            self.assertEqual(cashbook.lines[0].state, 'check')

            asset_book, = Cashbook.browse([job.booktransf])
            self.assertEqual(
                asset_book.rec_name, 'Depot | 10.00 usd | Open | 0.8000 u')
            self.assertEqual(len(asset_book.lines), 1)
            self.assertEqual(
                asset_book.lines[0].rec_name,
                "06/01/2022|from|10.00 usd|invest 10.00 usd to " +
                "buy 0.80 units [Book 1 | -10.00 usd | Open]|0.8000 u")
            self.assertEqual(asset_book.lines[0].state, 'check')
        self.assertEqual(asset_book.lines[0].state, 'check')

        IrDate.today = MagicMock(return_value=date.today())

    @with_transaction()
    def test_planner_cronjobs_booking_transfer_asset_eur_usd1(self):
        """ create job, configure transfer-booking to asset-cashbook,
            from euro to usd,
            same units between asset and cashbook
        """
        pool = Pool()
        Planner = pool.get('cashbook.planner')
        IrDate = pool.get('ir.date')
        Category = pool.get('cashbook.category')
        Cashbook = pool.get('cashbook.book')
        Currency = pool.get('currency.currency')
        Uom = pool.get('product.uom')
        Asset = pool.get('investment.asset')

        company = self.prep_company()
        with Transaction().set_context({'company': company.id}):
            asset_book = self.prep_planner_asset_book()

            (usd, euro) = self.prep_2nd_currency(company)
            chf, = Currency.create([{
                'name': 'Swiss Franc',
                'symbol': 'SFr',
                'code': 'CHF',
                'rates': [('create', [{
                    'date': date(2022, 5, 1),
                    'rate': Decimal('0.95'),
                }])]}])

            self.assertEqual(len(usd.rates), 1)
            self.assertEqual(usd.rates[0].rate, Decimal('1.05'))
            self.assertEqual(usd.rates[0].date, date(2022, 5, 2))
            self.assertEqual(euro.rates[0].rate, Decimal('1.0'))
            self.assertEqual(euro.rates[0].date, date(2022, 5, 2))
            self.assertEqual(company.currency.rec_name, 'Euro')

            job = self.prep_create_job()
            self.assertEqual(job.cashbook.rec_name, 'Book 1 | 0.00 € | Open')

            uom_u, = Uom.search([('symbol', '=', 'u')])
            self.assertEqual(uom_u.factor, Decimal('1.0'))
            self.assertEqual(uom_u.rate, Decimal('1.0'))

            uom_10u, = Uom.create([{
                'category': uom_u.category.id,
                'name': '10 Units',
                'symbol': '10xU',
                'factor': Decimal('10.0'),
                'rate': Decimal('0.1'),
                'rounding': Decimal('0.01'),
                'digits': 2}])
            self.assertEqual(uom_10u.factor, Decimal('10.0'))
            self.assertEqual(uom_10u.rate, 0.1)
            # check conversion: 1 [u] = 0.1 [10xU]
            self.assertEqual(Uom.compute_qty(uom_u, 1.0, uom_10u), 0.1)

            # asset-cashbook in CHF
            Cashbook.write(*[[asset_book], {'currency': chf.id}])
            self.assertEqual(
                asset_book.rec_name,
                'Depot | 0.00 SFr | Open | 0.0000 u')

            Asset.write(*[
                [asset_book.asset],
                {
                    'uom': uom_10u.id,
                    'rates': [(
                        'write',
                        [asset_book.asset.rates[0]],
                        {'rate': Decimal('1.25')})]}])
            # rate of asset = 1.25 usd
            self.assertEqual(
                asset_book.asset.rec_name,
                'Product 1 | 1.2500 usd/10xU | 05/02/2022')
            self.assertEqual(len(asset_book.lines), 0)

        IrDate.today = MagicMock(return_value=date(2022, 5, 24))

        category, = Category.search([('name', '=', 'Cat1')])
        Planner.write(*[
            [job],
            {
                'name': 'buy asset',
                'amount': Decimal('10.0'),
                'bookingtype': 'mvout',
                'category': category.id,
                'subject': 'invest 10.00 € to buy 0.xx units',
                'booktransf': asset_book.id,
                'wfcheck': True}])
        self.assertEqual(
            job.rec_name,
            'buy asset|Book 1|to|Depot|06/01/2022|€10.00')
        self.assertEqual(job.cashbook.rec_name, 'Book 1 | 0.00 € | Open')
        self.assertEqual(
            job.booktransf.rec_name,
            'Depot | 0.00 SFr | Open | 0.0000 u')
        self.assertEqual(len(job.cashbook.lines), 0)

        # check both cashbooks
        with Transaction().set_context({'date': date(2022, 6, 1)}):
            job, = Planner.search([])
            self.assertEqual(job.nextrun[0].date, date(2022, 6, 1))
            IrDate.today = MagicMock(return_value=date(2022, 6, 1))
            Planner.cronjob()
            self.assertEqual(job.nextrun[0].date, date(2022, 7, 1))

            # check rates to euro
            self.assertEqual(chf.rate, Decimal('0.95'))
            self.assertEqual(euro.rate, Decimal('1.0'))
            self.assertEqual(usd.rate, Decimal('1.05'))
            self.assertEqual(asset_book.asset.rate, Decimal('1.25'))
            self.assertEqual(asset_book.asset.uom.factor, Decimal('10.0'))

            # we invest 10€
            # transfer to chf-account, buy asset with rate in usd
            # 10€ --> 9.50 SFr
            # rate in CHF: 12.50 usd * 0.95 (SFr) / 1.05 (usd) = 11,3095
            # quantity = 9,50 SFr / 11,3095 = 0,8400
            cashbook, = Cashbook.browse([job.cashbook])
            self.assertEqual(cashbook.rec_name, 'Book 1 | -10.00 € | Open')
            self.assertEqual(len(cashbook.lines), 1)
            self.assertEqual(
                cashbook.lines[0].rec_name,
                "06/01/2022|to|-10.00 €|invest 10.00 € to buy 0.xx units " +
                "[Depot | 9.50 SFr | Open | 0.8400 u]")
            self.assertEqual(cashbook.lines[0].state, 'check')

            asset_book, = Cashbook.browse([job.booktransf])
            self.assertEqual(
                asset_book.rec_name, 'Depot | 9.50 SFr | Open | 0.8400 u')
            self.assertEqual(len(asset_book.lines), 1)
            self.assertEqual(
                asset_book.lines[0].rec_name,
                "06/01/2022|from|9.50 SFr|invest 10.00 € to buy 0.xx units " +
                "[Book 1 | -10.00 € | Open]|0.8400 u")
            self.assertEqual(asset_book.lines[0].state, 'check')
        self.assertEqual(asset_book.lines[0].state, 'check')

        IrDate.today = MagicMock(return_value=date.today())

# end PlannerTestCase
