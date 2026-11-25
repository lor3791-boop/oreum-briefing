"""data/prices.csv로 카드2·사이트용 시세 비교값을 계산한다.

기준: 축평원 한돈 탕박 경락가격, 원/kg, 제주 제외, 평균=1+·1·2등급(등외 제외).
사용: python3 scripts/price_stats.py [YYYY-MM-DD]  (기본: csv 마지막 날짜)
출력: JSON. 월 누적 일수가 부족하면 month_days_note에 표시 → 축평원 공표 누적평균 사용.
월평균·전월·전년 동월 값은 data/monthly.csv에 확정값이 있으면 그것을 우선한다.
"""
import csv, datetime as dt, json, pathlib, sys

D = pathlib.Path(__file__).resolve().parent.parent / "data"
rows = [r for r in csv.DictReader(open(D / "prices.csv", encoding="utf-8")) if r["avg"]]
rows.sort(key=lambda r: r["date"])
monthly = {r["month"]: int(r["avg"]) for r in csv.DictReader(open(D / "monthly.csv", encoding="utf-8"))}
target = sys.argv[1] if len(sys.argv) > 1 else rows[-1]["date"]
by = {r["date"]: int(r["avg"]) for r in rows}
day = dt.date.fromisoformat(target)

def avg(vals):
    return round(sum(vals) / len(vals)) if vals else None

def pct(a, b):
    return None if a is None or b is None else round((a - b) / b * 100, 1)

prev = [d for d in by if d < target]
prev_day = max(prev) if prev else None
wk_start = day - dt.timedelta(days=day.weekday())
this_wk = [v for d, v in by.items() if wk_start.isoformat() <= d <= target]
last_wk = [v for d, v in by.items() if (wk_start - dt.timedelta(7)).isoformat() <= d < wk_start.isoformat()]
ym = target[:7]
mtd = [v for d, v in by.items() if d.startswith(ym) and d <= target]
prev_m = (day.replace(day=1) - dt.timedelta(days=1)).strftime("%Y-%m")
prev_m_vals = [v for d, v in by.items() if d.startswith(prev_m)]
ly = f"{day.year - 1}-{day.month:02d}"

out = {
    "date": target,
    "status": next(r["status"] for r in rows if r["date"] == target),
    "daily": by[target],
    "prev_day": prev_day, "prev_day_value": by.get(prev_day),
    "dod_won": None if not prev_day else by[target] - by[prev_day],
    "dod_pct": pct(by[target], by.get(prev_day)),
    "week_avg": avg(this_wk), "last_week_avg": avg(last_wk),
    "wow_won": None if not (this_wk and last_wk) else avg(this_wk) - avg(last_wk),
    "wow_pct": pct(avg(this_wk), avg(last_wk)),
    "month_avg_from_csv": avg(mtd), "month_days_in_csv": len(mtd),
    "prev_month_avg": monthly.get(prev_m) or avg(prev_m_vals),
    "last_year_month_avg": monthly.get(ly),
}
mo = out["month_avg_from_csv"]
out["mom_pct"] = pct(mo, out["prev_month_avg"])
out["yoy_pct"] = pct(mo, out["last_year_month_avg"])
if len(mtd) < sum(1 for i in range(day.day) if (day - dt.timedelta(i)).weekday() < 5):
    out["month_days_note"] = "csv 일수 부족: 축평원 공표 월 누적평균을 쓰고 빠진 날짜를 csv에 채울 것"
print(json.dumps(out, ensure_ascii=False, indent=1))
