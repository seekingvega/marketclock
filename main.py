from datetime import time, datetime, timedelta
import pytz, argparse
from businessdate import BusinessDate
import pandas as pd
import pandas_market_calendars as mcal

def get_avail_exchanges():
    return mcal.get_calendar_names()

def get_cal_obj(ex_name):
    assert ex_name in mcal.get_calendar_names(), f'get_cal_obj: {ex_name} is not a valid exchange name'
    return mcal.get_calendar(ex_name)

def get_mkt_schedule(trade_date, cal_obj):
    ''' return market schedule in JSON given trade date and calendar object
    '''
    df = cal_obj.schedule(start_date = trade_date, end_date = trade_date)
    sch_dict = df.to_dict(orient='records')[0]
    return {k:v.astimezone(pytz.timezone(cal_obj.tz.zone)) for k,v in sch_dict.items()}

def get_valid_trading_dates(ref_date, cal_obj, tenor = '1w'):
    tenor = tenor if type(tenor)==tuple else (tenor, tenor)
    sd = (BusinessDate(ref_date)- tenor[0]).to_date()
    ed = (BusinessDate(ref_date)+ tenor[1]).to_date()
    return cal_obj.valid_days(start_date = sd, end_date = ed)

def is_trading_day(ref_date, cal_obj):
    l_mkt_days = get_valid_trading_dates(ref_date = ref_date, cal_obj = cal_obj)
    return ref_date in [datetime.date(d) for d in l_mkt_days]

def get_liveness(datetime_obj, schedule):
    ''' return pre (pre-open), post (after close), live (live), break (lunch break)
    '''
    if datetime_obj < schedule['market_open']:
        return 'pre'
    if datetime_obj > schedule['market_close']:
        return 'post'
    # trading hour
    if 'break_start' in schedule.keys():
        if datetime_obj > schedule['break_start'] and datetime_obj < schedule['break_end']:
            return 'break'
    return 'live'

def liveness_im_url(liveness):
    if liveness == 'live':
        return "https://img.shields.io/badge/market%20is-OPEN-green"
    elif liveness == 'break':
        return "https://img.shields.io/badge/market%20is-on%20break-yellow"
    else:
        return "https://img.shields.io/badge/market%20is-CLOSED-red"

def preprocess_dt_obj(dt_obj, cal_obj):
    ex_tz = pytz.timezone(cal_obj.tz.zone)
    dt_ex_tz = dt_obj.astimezone(ex_tz)
    date_ex_tz = datetime.date(dt_ex_tz)

    return {
        'exchange_timezone': ex_tz,
        'datetime': dt_ex_tz,
        'date': date_ex_tz
    }

def td_diff(trade_date, l_valid_days, day_diff:int = 1):
    ''' return trade_date + day_diff in l_valid_days
    '''
    assert day_diff != 0, f'day_diff must be an integer and non-zero'
    l_days = [d for d in l_valid_days if d>trade_date] if day_diff > 0 else \
            sorted([d for d in l_valid_days if d<trade_date], reverse = True)
    return l_days[abs(day_diff)-1].date()

def get_time_till(ref_datetime, fut_datetime):
    diff_s = fut_datetime - ref_datetime
    return diff_s if isinstance(diff_s, timedelta) else timedelta(seconds = diff_s)

def Main(exchange_name, datetime_obj = datetime.now()):
    ''' return all trading time information for the given datetime_obj in the exchange's timezone
    '''
    if exchange_name not in mcal.get_calendar_names():
        return {'error': f'{exchange_name} is not a valid exchange name'}

    ex_cal = get_cal_obj(exchange_name)
    dt_dict = preprocess_dt_obj(dt_obj = datetime_obj, cal_obj=ex_cal)
    is_mkt_date = is_trading_day(ref_date = dt_dict['date'], cal_obj = ex_cal)
    ref_date_sch = get_mkt_schedule(trade_date = dt_dict['date'], cal_obj=ex_cal)\
                    if is_mkt_date else None
    liveness = get_liveness(datetime_obj = dt_dict['datetime'],
                schedule = ref_date_sch ) if is_mkt_date else None
    l_mkt_days = get_valid_trading_dates(ref_date = dt_dict['date'], cal_obj = ex_cal)

    if liveness == 'pre':
        str_msg = f"market opening in {get_time_till(dt_dict['datetime'], ref_date_sch['market_open'])}"
    elif liveness in ['live', 'break']:
        str_msg = f"market closing in {get_time_till(dt_dict['datetime'], ref_date_sch['market_close'])}"
    else:
        next_date_sch = get_mkt_schedule(
                        trade_date = td_diff(dt_dict['date'], l_valid_days = l_mkt_days, day_diff=1),
                        cal_obj=ex_cal)
        str_msg = f"market opening in {get_time_till(dt_dict['datetime'], next_date_sch['market_open'])}"

    return {
        'exchange_name': exchange_name,
        'exchange_timezone': str(dt_dict['exchange_timezone']), # getting JSON encoding issues here
        'ref_date_time': dt_dict['datetime'],
        'ref_date': dt_dict['date'],
        'is_trading_day': is_mkt_date,
        'status': liveness,
        'next_trading_date': td_diff(dt_dict['date'], l_valid_days = l_mkt_days, day_diff=1),
        'previous_trading_date': td_diff(dt_dict['date'], l_valid_days = l_mkt_days, day_diff=-1),
        'coming_event': str_msg,
        'status_img_url': liveness_im_url(liveness),
        'market_schedule': ref_date_sch
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description= f'Market Clock')
    parser.add_argument('--exchange', required = True, type = str,
                            help = 'exchange name')
    parser.add_argument('--datetime', required = False, type = float, default = datetime.now(),
                            help = 'reference datetime (default: now)')
    args = parser.parse_args()
    print(Main(exchange_name = args.exchange, datetime_obj=args.datetime))
