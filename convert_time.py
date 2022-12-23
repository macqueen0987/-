import re
import var
from datetime import datetime, timedelta


def get_time(datetime, args):
    timedelta_days = 0
    no_timedetla = False
    found = False
    party_hour, party_minute = 0, 0
    keys = []
    r = re.compile('\s*\d+일후')
    m = r.search(args)
    if m is not None:
        match = m.group(0)
        keys.append(match)
        match = match.replace('일후', '')
        timedelta_days = int(match)
        no_timedetla = True

    r = re.compile('\s*\d+일뒤')
    m = r.search(args)
    if m is not None:
        match = m.group(0)
        keys.append(match)
        match = match.replace('일뒤', '')
        timedelta_days = int(match)
        no_timedetla = True


    r = re.compile('\s*\d+시\s*\d+분')
    m = r.search(args)
    if m is not None and not found:
        # print(m)
        found = True
        match = m.group(0)
        match = match.replace(" ","").replace("분","")
        party_hour, party_minute = map(int, match.split("시"))

    r = re.compile('\s*\d+시\s*반')
    m = r.search(args)
    if m is not None and not found:
        found = True
        match = m.group(0)
        party_hour = match.replace(" ","").split("시")[0]
        party_hour = int(party_hour)
        party_minute = 30

    r = re.compile('\s*\d+시')
    m = r.search(args)
    if m is not None and not found:
        found = True
        match = m.group(0)
        party_hour = match.replace(" ","").split("시")[0]
        party_hour = int(party_hour)
        party_minute = 0

    if party_hour > 23 or party_minute > 59:
        return [1, datetime, keys]

    if party_hour == 0 and party_minute == 0:
        return [2, datetime, keys]

    am = False
    pm = False
    for i in var.AM:
        if i in args:
            am = True
            break

    for i in var.PM:
        if i in args:
            pm = True
            break

    if pm:
        party_hour = party_hour % 12 + 12

    if am:
        party_hour = party_hour % 12

    if not am and not pm and not no_timedetla:
        if party_hour < datetime.hour:
            party_hour += 12
            if party_hour > 23:
                party_hour = party_hour % 24
                timedelta_days = 1

    for i in var.tomorrow:
        if i in args:
            timedelta_days = 1
            break

    datetime = datetime + timedelta(days=timedelta_days)
    datetime = datetime.replace(hour=party_hour, minute=party_minute, second=0, microsecond=0)
    return [0, datetime, keys]


def change_time(time, args):
    timedelta_days, timedelta_hours, timedelta_mins = 0,0,0

    if ":" in args:
        args = args.split(":")

        if len(args) == 2:
            timedelta_hours = int(args[0])
            timedelta_mins = int(args[1])

        elif len(args) == 3:
            timedelta_days = int(args[0])
            timedelta_hours = int(args[1])
            timedelta_mins = int(args[2])

        else:
            return [1]

    else:
        r = re.compile('\s*\d+일')
        m = r.search(args)
        if m is not None:
            match = m.group(0)
            match = match.replace('일', '')
            timedelta_days = int(match)

        r = re.compile('\s*\d+시간')
        m = r.search(args)
        if m is not None:
            match = m.group(0)
            match = match.replace('시간', '')
            timedelta_hours = int(match)

        r = re.compile('\s*\d+분')
        m = r.search(args)
        if m is not None:
            match = m.group(0)
            match = match.replace('분', '')
            timedelta_mins = int(match)

    return [0, timedelta_days, timedelta_hours, timedelta_mins]