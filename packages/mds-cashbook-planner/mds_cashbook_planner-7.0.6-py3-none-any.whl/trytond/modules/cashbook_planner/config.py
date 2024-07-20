# -*- coding: utf-8 -*-
# This file is part of the cashbook-planner from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.


from datetime import date, timedelta
from dateutil.easter import (
    easter, EASTER_JULIAN, EASTER_ORTHODOX, EASTER_WESTERN)
from trytond.pool import PoolMeta, Pool
from trytond.model import fields
from trytond.transaction import Transaction
from trytond.report import Report


holidays = fields.Char(
    string='Holidays', help='Semicolon separate list of dates: ' +
    'yyyy-mm-dd = single date, mm-dd = annual repetition, ' +
    'easter[greg|jul|orth] = Easter Sunday, ascension = Ascension Day, ' +
    'whitsun = Whitsunday, offset with :+/-n e.g.: easter:+1 = Easter Monday')


class Configuration(metaclass=PoolMeta):
    __name__ = 'cashbook.configuration'

    holidays = fields.MultiValue(holidays)
    holidays_info = fields.Function(fields.Char(
        string='Holidays', readonly=True,
        help='Holidays in the current year.'), 'on_change_with_holidays_info')

    @fields.depends('holidays')
    def on_change_with_holidays_info(self, name=None):
        """ get string of generated holidays for years in
        context-value 'holiday_years' or current year

        Args:
            name (str, optional): field. Defaults to None.

        Returns:
            str: formatted holidays in language of user
        """
        pool = Pool()
        Config = pool.get('cashbook.configuration')
        context = Transaction().context

        years = context.get('holiday_years', [])
        cfg1 = Config.get_singleton()
        if cfg1:
            dates = cfg1.holiday_dates(years)
            dates.sort()
            return '|'.join([
                Report.format_date(x) for x in dates])

    def holiday_dates(self, years=[]):
        """ get list of dates for list of years

        Args:
            years (list, optional): years to get holidays for. Defaults to [].

        Returns:
            list of date: holidays for requestd years
        """
        pool = Pool()
        IrDate = pool.get('ir.date')
        Config = pool.get('cashbook.configuration')

        if not years:
            years = [IrDate.today().year]

        cfg1 = Config.get_singleton()
        if not (cfg1 and cfg1.holidays and isinstance(cfg1.holidays, str)):
            return []
        return Config.holiday_parseconfig(cfg1.holidays, years)['dates']

    @classmethod
    def holiday_parseconfig(cls, holiday_string, years=[]):
        """ read holiday config, generate parsed list of defines

        Args:
            holiday_string (str): holiday definition string
            years (list of int): years to generate dates for

        Returns:
            dict: {'definition': '<parsed definition string>',
                'dates': [<requested dates>]}
        """
        IrDate = Pool().get('ir.date')

        def parse_date_offet(offset_str):
            """ parse offset string

            Args:
                offset_str (str): '+n' or '-n'

            Returns:
                tuple: (int(offset), 'offset-string')
            """
            # decode ':+n' or ':-n'
            offset_value = 0
            plus_sign = 1
            if offset_str:
                plus_sign = -1 if offset_str.startswith('-') else 1
                date_offset = offset_str[1:]
                if date_offset.isdigit():
                    offset_value = int(date_offset)
            return (offset_value * plus_sign, '%(sign)s%(amount)d' % {
                'sign': '+' if plus_sign >= 0 else '-',
                'amount': offset_value})

        def parse_date_definition(date_str, years):
            """ parse date definition string, generate list of
            dates

            Args:
                date_str (str): definition string
                years (list of int): years to generate dates for

            Returns:
                _type_: _description_
            """
            dates = []
            date_def = ''
            easter_type = {
                'greg': EASTER_WESTERN, 'jul': EASTER_JULIAN,
                'orth': EASTER_ORTHODOX}

            date_str = date_str.lower()
            # first parse easter-based dates
            for dt_calc in [
                    {'type': 'easter', 'days': 0},
                    {'type': 'ascension', 'days': 39},
                    {'type': 'whitsun', 'days': 49}]:
                if date_str.startswith(dt_calc['type']):
                    e_meth = date_str[len(dt_calc['type']):]
                    easter_meth = easter_type.get(e_meth, EASTER_WESTERN)
                    dates.extend([
                        easter(x, easter_meth) +
                        timedelta(days=dt_calc['days'])
                        for x in years])
                    date_def = date_str

            # if not detected try date string
            if not date_def:
                date_fields = date_str.split('-')
                try:
                    if len(date_fields) == 3:
                        dates.append(date.fromisoformat(date_str))
                        date_def = date_str
                    elif len(date_fields) == 2:
                        for year in years:
                            dates.append(date.fromisoformat(
                                str(year) + '-' + date_str))
                        date_def = date_str
                except Exception:
                    pass
            return (dates, date_def)

        if not (holiday_string and isinstance(holiday_string, str)):
            return {'definition': '', 'dates': []}

        if not years:
            years = [IrDate.today().year]

        parsed_str = []
        parsed_dates = []
        for datedef in holiday_string.split(';'):
            if not datedef:
                continue

            datedef = datedef.strip().split(':')
            date_offset = datedef[1] if len(datedef) > 1 else ''

            (date_offset, offset_str) = parse_date_offet(date_offset)
            (date_lst, date_def) = parse_date_definition(datedef[0], years)

            parsed_dates.extend([
                x + timedelta(days=date_offset)
                for x in date_lst])
            if date_def:
                if date_offset != 0:
                    date_def += ':' + offset_str
                parsed_str.append(date_def)
        return {'definition': ';'.join(parsed_str), 'dates': parsed_dates}

    @classmethod
    def multivalue_model(cls, field):
        """ get model for value
        """
        pool = Pool()

        if field in ['holidays']:
            return pool.get('cashbook.configuration_user')
        return super(Configuration, cls).multivalue_model(field)

    @classmethod
    def default_holidays(cls, **pattern):
        return cls.multivalue_model('holidays').default_holidays()

# end Configuration


class UserConfiguration(metaclass=PoolMeta):
    __name__ = 'cashbook.configuration_user'

    holidays = holidays

    @classmethod
    def default_holidays(cls):
        return 'easter+1;easter-2;ascension;05-01;12-25;12-26;01-01;'

# end CashbookLine
