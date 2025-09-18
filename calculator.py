# calculator.py
import re
from datetime import datetime, timedelta
import pytz

def calculate_office_time(raw_text, user_timezone='UTC'):
    """
    Calculate office time from biometric log data
    
    Args:
        raw_text: The biometric log text
        user_timezone: Timezone string (e.g., 'Asia/Kolkata', 'UTC', 'US/Eastern')
    """
    try:
        # Get timezone object
        tz = pytz.timezone(user_timezone)
        # Get current time in user's timezone
        now = datetime.now(tz).replace(second=0, microsecond=0)
    except:
        # Fallback to UTC if timezone is invalid
        now = datetime.utcnow().replace(second=0, microsecond=0)
    
    time_strs = re.findall(r"\b\d{1,2}:\d{2}\b", raw_text)
    if not time_strs:
        raise ValueError("No valid HH:MM times found in input.")

    # Parse times without timezone first
    times_only = [datetime.strptime(ts, "%H:%M").time() for ts in time_strs]

    # Convert to timezone-aware datetime
    today = now.date()
    first_dt_today = datetime.combine(today, times_only[0])
    first_dt_today = tz.localize(first_dt_today) if hasattr(tz, 'localize') else first_dt_today

    # Determine base date
    base_date = today - timedelta(days=1) if first_dt_today > now else today

    datetimes = []
    prev = None
    for t in times_only:
        candidate = datetime.combine(base_date, t)
        # Make timezone-aware
        if hasattr(tz, 'localize'):
            candidate = tz.localize(candidate)
        else:
            candidate = candidate.replace(tzinfo=tz)
        
        if prev is None:
            datetimes.append(candidate)
            prev = candidate
            continue
        while candidate < prev:
            candidate += timedelta(days=1)
        datetimes.append(candidate)
        prev = candidate

    sessions = []
    breaks = []
    total_work_seconds = 0
    total_break_seconds = 0
    n = len(datetimes)

    for i in range(0, n, 2):
        in_dt = datetimes[i]
        if i + 1 < n:
            out_dt = datetimes[i + 1]
            ongoing = False
        else:
            out_dt = now
            while out_dt < in_dt:
                out_dt += timedelta(days=1)
            ongoing = True

        diff_seconds = int((out_dt - in_dt).total_seconds())
        total_work_seconds += diff_seconds
        sessions.append({"in": in_dt, "out": out_dt, "seconds": diff_seconds, "ongoing": ongoing})

        if not ongoing and i + 2 < n:
            next_in = datetimes[i + 2]
            gap = int((next_in - out_dt).total_seconds())
            total_break_seconds += gap
            breaks.append({"start": out_dt, "end": next_in, "seconds": gap})

    # Convert totals
    work_minutes = total_work_seconds // 60
    work_h, work_m = divmod(work_minutes, 60)
    break_minutes = total_break_seconds // 60
    break_h, break_m = divmod(break_minutes, 60)

    # Targets
    target_work = 7 * 60 + 30   # 7h 30m = 450 minutes
    target_break = 90           # 90 minutes

    remaining_work = max(0, target_work - work_minutes)
    remaining_break = max(0, target_break - break_minutes)

    return {
        "work_hours": int(work_h),
        "work_minutes": int(work_m),
        "break_hours": int(break_h),
        "break_minutes": int(break_m),
        "sessions": sessions,
        "breaks": breaks,
        "remaining_work": divmod(remaining_work, 60),
        "remaining_break": divmod(remaining_break, 60),
        "current_time": now.strftime("%Y-%m-%d %H:%M %Z")
    }
