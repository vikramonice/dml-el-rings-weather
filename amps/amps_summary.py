"""
amps_summary.py
===============
Plain-language MODEL GUIDANCE for each DML/EL RINGS site, day by day, written by fixed rules from the
AMPS point forecast (amps_meteogram.py). AMPS only: it is the model tuned for Antarctica
(Polar WRF, 8 km), and the product stays with it.

This is not a forecast. There is no forecaster in the loop: every sentence is a threshold
applied to AMPS numbers. Nothing is generated freely.

The rules follow the local section of the International Antarctic Weather Forecasting Handbook
(Turner & Pendlebury, eds., 2004, British Antarctic Survey; section 7.5.7 Maitri and Dakshin
Gangotri, 7.5.8 Novolazarevskaya, 6.6.5-6.6.6 surface contrast and horizon). Dakshin Gangotri
was on the ice shelf ~17 km north of depot 43D, so its rules serve the shelf sites.

  drift      drifting snow starts at about 10 m/s (20 kt); blowing snow at about 18 m/s (35 kt);
             earlier on recently fallen snow (here: 7 m/s / 14 kt when >= 0.5 mm fell in the
             previous 48 h). Thresholds apply to the AMPS mean wind; gusts are stronger.
  pattern    wind direction marks the weather type at Maitri: E-SE = depression approaching
             from the west (storms, snow); S = katabatic (clear, dry, sudden onsets to 25-30 kt and
             sudden lulls); N-NW = ridge passing (light winds).
  storm      pressure falling while temperature rises (the inversion breaks up) = depression
             arriving; pressure rising steeply afterwards = clearing, wind easing.
  contrast   surface contrast and horizon are lost under deep, featureless low cloud
             (stratus/altostratus/nimbostratus): here a saturated layer (RH over ice >= 95 %)
             based in the lowest 1.5 km and >= 1.5 km deep. With snowfall or drift: whiteout.
  snow       daily total (mm water ~ cm of snow); >= 0.5 mm flagged; >= 2 mm on the shelf:
             mark depots and instruments.
Confidence from AMPS itself:
  run-to-run  the same day in the previous AMPS run (12 h older)
  lead time   forecast day 4 and later: "lower confidence"

Outputs (outputs/field/amps/):  <cycle>_<site>_summary.json  (and text on stdout)

Run (icepyx2 env), after amps_meteogram.py for the cycle:
    python amps_summary.py --cycle 2026101712 [--from "2026-10-18 09:00"]
The previous run is read from outputs/field/amps/<prev>_<site>.csv, or from the viewer manifest
(viewer_manifest.json embeds each run's CSV) in a fresh clone.
"""
import argparse
import csv
import datetime as dt
import io
import json

import numpy as np

from amps_meteogram import OUT

KN = 1.94384
CONST = dict(drift=10.0, drift_fresh=7.0, blow=18.0, fresh_mm=0.5, snow=0.5, snow_trace=0.2, snow_mark=2.0,
             rhi_cloud=95.0, thick=1500.0, pfall=4.0, prise=4.0, warm=5.0,
             same_wind=3.0)          # run-to-run: daily max wind within 3 m/s (6 kt) = consistent
DIR8 = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
# DML/EL RINGS copy: the site-type and weather-pattern rules come from the handbook sections for
# Maitri, Novolazarevskaya and Dakshin Gangotri (Dronning Maud Land) and are switched off here; the
# generic thresholds (drift, blowing snow, snowfall, low cloud, pressure falls) are kept.
SHELF, KATABATIC = set(), set()
PATTERN = False
SITE_NOTE = {
    "shelf": "On the ice shelf, blizzards are stronger and last longer than at Maitri, and the strong "
             "winds come from the east to south-east (handbook, Dakshin Gangotri).",
    "katabatic": "At the foot of the ice sheet, strong winds come from the south-east with storms; southerly "
                 "winds are katabatic (handbook, Maitri).",
}


def kn(v):
    return int(round(v * KN))


def hours(times):
    """Merge a sorted list of datetimes (3-hourly) into 'HH-HH UTC' spans."""
    if not times:
        return ""
    spans, a, b = [], times[0], times[0]
    for t in times[1:]:
        if t - b <= dt.timedelta(hours=3):
            b = t
        else:
            spans.append((a, b)); a = b = t
    spans.append((a, b))
    # values are 3-h steps ending in the day, so 00 UTC is the day's end: midnight / 24
    one = lambda t: "around midnight" if t.hour == 0 else "around %02d UTC" % t.hour
    two = lambda a, b: "%02d-%s UTC" % (a.hour, "24" if b.hour == 0 else "%02d" % b.hour)
    return ", ".join(one(a) if a == b else two(a, b) for a, b in spans)


def parse(text):
    rows = list(csv.DictReader(io.StringIO(text)))
    A = {"time": np.array([dt.datetime.strptime(r["time"], "%Y-%m-%d %H:%M") for r in rows])}
    for k in ("t2", "wchill", "wspd", "wdir", "mslp", "apcp", "rhi_low", "cld_depth", "ws500", "wd500"):
        A[k] = np.array([float(r.get(k) or "nan") for r in rows])
    return A


def previous(cycle, slug):
    """AMPS series of the run 12 h before `cycle`, or None."""
    prev = (dt.datetime.strptime(cycle, "%Y%m%d%H") - dt.timedelta(hours=12)).strftime("%Y%m%d%H")
    f = OUT / ("%s_%s.csv" % (prev, slug))
    if f.exists():
        return prev, parse(f.read_text())
    man = OUT / "viewer_manifest.json"
    if man.exists():
        for r in json.loads(man.read_text()):
            if r["cycle"] == prev:
                for s in r["sites"]:
                    if s["slug"] == slug and s.get("csv"):
                        return prev, parse(s["csv"])
    return prev, None


def dir8(deg):
    return DIR8[int(((deg % 360) + 22.5) // 45) % 8]


def prevailing(spd, d):
    ok = spd > 2
    if not ok.any():
        return "variable"
    u = np.sum(-spd[ok] * np.sin(np.radians(d[ok])))
    v = np.sum(-spd[ok] * np.cos(np.radians(d[ok])))
    return dir8(np.degrees(np.arctan2(-u, -v)))


def in_day(A, day):
    return (A["time"] > day) & (A["time"] <= day + dt.timedelta(days=1))   # 3-h values ending in the day


def change12(A, i, key):
    """Change of A[key] over the 12 h ending at index i (nan if not available)."""
    j = np.flatnonzero(A["time"] == A["time"][i] - dt.timedelta(hours=12))
    return A[key][i] - A[key][j[0]] if j.size else np.nan


# ---------------------------------------------------------------- DML/EL: nearest handbook section per site
# International Antarctic Weather Forecasting Handbook (Turner & Pendlebury 2004), printed pages:
#   7.5.9  Inland of Syowa (Asuka)  346-350      7.5.10 Syowa Station  350-354
#   7.6.1  Molodezhnaya Station      354-362      7.6.2  Mount King      362-366
SECTION = {"pea": "asuka", "w1": "syowa", "s17": "syowa", "e1": "molodezhnaya", "e2": "molodezhnaya",
           "e3": "mountking", "e4": "mountking"}
SITE_NOTE_EL = {
    "pea": "Nearest handbook station: Asuka (Sør Rondane, 930 m, about 30 km from PEA). A katabatic wind zone: "
           "the annual mean wind there exceeds 12 m/s (23 kt), and strong winds often give deep blowing snow and "
           "poor visibility (handbook 7.5.9).",
    "w1": "Nearest handbook station: Syowa, about 350 km east; W1 lies between Asuka and Syowa, so these rules are "
          "an approximation. At Syowa, blizzards come with north-east to east-north-east wind as a low passes or "
          "stops nearby; pure easterly is the katabatic, about 7-10 m/s in the morning (handbook 7.5.10).",
    "s17": "Nearest handbook station: Syowa, about 20 km. Blizzards come with north-east to east-north-east wind as "
           "a low passes or stops nearby; pure easterly is the katabatic, about 7-10 m/s in the morning and gone "
           "by the afternoon. When the katabatic reaches the coast, visibility can fall from 1 km to 100 m within "
           "minutes (handbook 7.5.10).",
    "e1": "Nearest handbook station: Molodezhnaya, about 40 km. East and south-east winds make up 85% of the "
          "record; the south-east wind is the katabatic, in summer mainly at night. The strongest winds come in "
          "the rear of a cyclone, when katabatic and cyclonic winds line up (handbook 7.6.1).",
    "e2": "Nearest handbook station: Molodezhnaya, about 150 km west. East and south-east winds make up 85% of "
          "the record; the south-east wind is the katabatic, in summer mainly at night. The strongest winds come "
          "in the rear of a cyclone (handbook 7.6.1).",
    "e3": "Nearest handbook station: Mount King (summer camp 1975-80, about 120 km south-west), from four summers "
          "of notes. The usual wind is easterly; most bad weather arrived from the north-west; moist north-easterly "
          "flow brings extensive low cloud; long fine spells came under a ridge of the polar high (handbook 7.6.2).",
    "e4": "Nearest handbook station: Mount King (summer camp 1975-80, about 170 km west), from four summers of "
          "notes. The usual wind is easterly; most bad weather arrived from the north-west; moist north-easterly "
          "flow brings extensive low cloud (handbook 7.6.2).",
}


def between(d, lo, hi):
    """Direction d (deg) in [lo, hi), wrapping through north when lo > hi."""
    d = np.asarray(d) % 360
    return (d >= lo) & (d < hi) if lo <= hi else (d >= lo) | (d < hi)


def regional(slug, A, idx, ta, w, d, T, rh, dep, pr, flags):
    """Rules from the nearest handbook section (DML/EL copy). Thresholds marked 'ours' in RULES.md."""
    sec, out = SECTION.get(slug), []
    if not sec:
        return out
    hr = np.array([t.hour for t in ta])
    w5 = A.get("ws500", np.full(len(A["time"]), np.nan))[idx]
    d5 = A.get("wd500", np.full(len(A["time"]), np.nan))[idx]
    dp3 = np.array([A["mslp"][i] - A["mslp"][i - 1] if i > 0 else np.nan for i in idx])     # 3-h change
    if sec == "syowa":
        ne = between(d, 22.5, 78.75) & (w >= 10)
        if ne.any():
            t_ = [t for t, x in zip(ta, ne) if x]
            fast = ne & (dp3 <= -3)
            txt = ("North-east to east-north-east wind of %d kt %s: at Syowa, blizzards come only with wind from "
                   "this direction." % (kn(np.nanmax(w[ne])), hours(t_)))
            lev = "watch"
            if fast.any():
                txt += (" Pressure is falling %.0f hPa in 3 h at the same time; the handbook ties fast falls "
                        "(3-5 hPa per hour) to blizzards developing." % -np.nanmin(dp3[fast]))
                lev = "warn"
            out.append(dict(kind="Handbook", level=lev, text=txt)); flags.append("blizzard direction")
        kat = between(d, 78.75, 112.5) & (w >= 7) & (hr >= 3) & (hr <= 9)
        if kat.any():
            out.append(dict(kind="Handbook", level="ok",
                            text="Easterly wind in the morning %s: the katabatic, which at Syowa reaches about "
                                 "10 m/s and dies off by the afternoon." % hours([t for t, x in zip(ta, kat) if x])))
    if sec == "molodezhnaya":
        kat = between(d, 112.5, 157.5) & (w >= 7) & ((hr >= 21) | (hr <= 3))
        if kat.any():
            out.append(dict(kind="Handbook", level="watch" if np.nanmax(w[kat]) >= 10 else "ok",
                            text="South-east wind at night %s: the katabatic. In summer it blows mainly between 01 "
                                 "and 05 local time, and its gusts can reach 25-30 m/s, far above the mean wind."
                                 % hours([t for t, x in zip(ta, kat) if x])))
        rise = np.array([change12(A, i, "mslp") for i in idx])
        rear = between(d, 67.5, 157.5) & (w >= 15) & (rise >= 3)
        if rear.any():
            out.append(dict(kind="Handbook", level="warn",
                            text="Strong east to south-east wind while pressure rises after a low %s: the strongest "
                                 "winds come in the rear of a cyclone, when katabatic and cyclonic winds line up; "
                                 "with loose snow, blowing snow." % hours([t for t, x in zip(ta, rear) if x])))
            flags.append("rear of a low")
        thin = (rh >= 95) & ~(dep >= 1500) & (hr >= 6) & (hr <= 15) & (w < 10)
        if thin.any():
            out.append(dict(kind="Handbook", level="watch",
                            text="Thin low cloud over the snow by day %s: the handbook warns of white-out in sunny "
                                 "weather under thin, broken stratus; flights over the ice sheet are best planned with "
                                 "a cloud-free forecast." % hours([t for t, x in zip(ta, thin) if x])))
            flags.append("white-out (thin cloud)")
    if sec == "mountking":
        ne = between(d, 22.5, 67.5) & (w >= 5)
        if ne.any():
            out.append(dict(kind="Handbook", level="watch",
                            text="North-easterly flow %s: at Mount King these airstreams were almost always moist, "
                                 "with extensive low cloud." % hours([t for t, x in zip(ta, ne) if x])))
            flags.append("moist north-easterly")
        nw = between(d5, 247.5, 337.5) & (w5 >= 10)
        if nw.any() and ((rh >= 95).any() or np.nansum(pr) >= 0.2):
            out.append(dict(kind="Handbook", level="watch",
                            text="Upper (500 hPa) north-westerly to westerly flow %s, with cloud or snow: most "
                                 "deteriorations at Mount King arrived from the north-west in this pattern, even "
                                 "with an easterly surface wind." % hours([t for t, x in zip(ta, nw) if x])))
            flags.append("weather from the north-west")
        if not ne.any() and np.isfinite(d5).all() and between(d5, 90, 270).all() and np.mean(rh >= 95) < 0.25:
            out.append(dict(kind="Handbook", level="ok",
                            text="No northerly component in the upper wind all day: the only long clear spells at "
                                 "Mount King came in this pattern."))
    if sec == "syowa":
        north = (between(d5, 315, 45)) & (w5 >= 10)
        south = between(d5, 135, 225) & (w5 >= 10)
        if north.any():
            out.append(dict(kind="Handbook", level="watch",
                            text="Upper (500 hPa) wind from the north, up to %d kt, %s: at Syowa, upper northerlies of "
                                 "10 m/s or more bring bad weather." % (kn(np.nanmax(w5[north])), hours([t for t, x in zip(ta, north) if x]))))
            flags.append("upper northerly")
        elif south.any() and not north.any():
            out.append(dict(kind="Handbook", level="ok",
                            text="Upper (500 hPa) wind from the south %s: at Syowa, upper southerlies bring good "
                                 "weather." % hours([t for t, x in zip(ta, south) if x])))
        up = np.array([change12(A, i, "ws500") if "ws500" in A else np.nan for i in idx])
        nws = between(d5, 270, 330) & (w5 >= 15) & (up >= 5)
        if nws.any():
            out.append(dict(kind="Handbook", level="watch",
                            text="Upper (500 hPa) north-westerly strengthening to %d kt %s: the handbook warns that a "
                                 "low may be approaching, which can deepen into a major blizzard."
                                 % (kn(np.nanmax(w5[nws])), hours([t for t, x in zip(ta, nws) if x]))))
            flags.append("low approaching")
    if sec in ("syowa", "molodezhnaya"):
        jump = np.array([A["t2"][i] - A["t2"][i - 2] if i > 1 else np.nan for i in idx])          # 6-h warming
        if np.nanmax(jump) >= 10:
            i = int(np.nanargmax(jump))
            out.append(dict(kind="Handbook", level="watch",
                            text="Sudden warming of %.0f °C in 6 h to %02d UTC: the handbook links a jump of about 10 °C "
                                 "in 3-4 h to the surface inversion breaking up, often as a blizzard develops."
                                 % (jump[i], ta[i].hour or 24)))
            flags.append("sudden warming")
    return out


def day_summary(day, A, P, prev_label, lead_day, slug):
    c = CONST
    ia = in_day(A, day)
    idx = np.flatnonzero(ia)
    ta = list(A["time"][ia])
    w, d, T, wc, pr, rh, dep = (A[k][ia] for k in ("wspd", "wdir", "t2", "wchill", "apcp", "rhi_low", "cld_depth"))
    items, flags = [], []

    # fresh snow in the previous 48 h lowers the drift threshold
    def fresh(i):
        t = A["time"][i]
        m = (A["time"] > t - dt.timedelta(hours=48)) & (A["time"] <= t)
        return np.nansum(A["apcp"][m]) >= c["fresh_mm"]
    thr = np.array([c["drift_fresh"] if fresh(i) else c["drift"] for i in idx])

    # --- wind and drift
    k = int(np.nanargmax(w))
    txt = "%s %d-%d kt (%.0f-%.0f m/s), strongest %s from %s." % (
        prevailing(w, d), kn(np.nanmin(w)), kn(np.nanmax(w)), np.nanmin(w), np.nanmax(w), hours([ta[k]]), dir8(d[k]))
    level = "ok"
    blow = [t for t, x in zip(ta, w) if x >= c["blow"]]
    drift = [t for t, x, h in zip(ta, w, thr) if h <= x < c["blow"]]
    if blow:
        txt += " Blowing snow likely %s: visibility poor to nil." % hours(blow)
        level = "warn"; flags.append("blowing snow")
    if drift:
        low = any(h < c["drift"] for x, h in zip(w, thr) if x >= h)
        txt += " Drifting snow likely %s%s." % (hours(drift), " (fresh snow drifts from about 14 kt)" if low else "")
        level = level if blow else "watch"; flags.append("drifting snow")
    items.append(dict(kind="Wind", text=txt, level=level))

    # --- weather pattern from wind direction (handbook, Maitri): any easterly to south-easterly spell with
    #     falling pressure or snow = cyclonic (storm); south-south-east to south-south-west = katabatic
    pf = np.nanmax([-change12(A, i, "mslp") for i in idx])
    cyc = [t for t, x, y in zip(ta, w, d) if x >= 5 and 60 <= y < 157.5]
    kat = [t for t, x, y in zip(ta, w, d) if x >= 5 and 157.5 <= y <= 210]
    if PATTERN and cyc and (pf >= 2 or np.nansum(pr) >= c["snow_trace"]):
        items.append(dict(kind="Pattern", level="watch",
                          text="Easterly to south-easterly wind %s with falling pressure or snow: a depression "
                               "approaching from the west. This is the storm pattern here." % hours(cyc)))
    if kat and slug in KATABATIC:
        items.append(dict(kind="Pattern", level="watch" if np.nanmax(w) >= c["drift_fresh"] else "ok",
                          text="Southerly katabatic wind %s: usually clear, dry air. Onsets can be sudden, from calm "
                               "to 25-30 kt, with equally sudden lulls." % hours(kat)))
    if PATTERN and not cyc and not kat and (w >= 5).any() and (d[k] >= 300 or d[k] <= 30):
        items.append(dict(kind="Pattern", level="ok", text="Northerly: a ridge passing, usually light winds."))

    # --- nearest handbook section (DML/EL)
    items += regional(slug, A, idx, ta, w, d, T, rh, dep, pr, flags)

    # --- snow
    tot = float(np.nansum(pr))
    if tot < c["snow_trace"]:
        items.append(dict(kind="Snow", text="None expected.", level="ok"))
    else:
        txt = "%.1f mm water (%s of fresh snow), mainly %s." % (
            tot, "under 1 cm" if tot < 1 else "about %.0f cm" % tot, hours([t for t, x in zip(ta, pr) if x >= 0.1]))
        lev = "ok"
        if tot >= c["snow"]:
            lev = "watch"; flags.append("snow")
            txt += " Loose fresh snow drifts at lower wind speeds for the next two days."
            falling = pr >= 0.1
            if falling.any() and np.nanmax(w[falling]) < 5:
                txt += " It falls with light wind, so it lies loose."
        if tot >= c["snow_mark"] and slug in SHELF:
            txt += " Mark depots and instruments."
        items.append(dict(kind="Snow", text=txt, level=lev))

    # --- cloud, surface contrast and whiteout
    thick = dep >= c["thick"]
    lowc = rh >= c["rhi_cloud"]
    frac = float(np.mean(lowc)) if len(lowc) else 0
    txt = "Low cloud %s." % ("likely most of the day" if frac >= 0.6 else "at times" if frac >= 0.25 else "unlikely")
    lev = "ok"
    tk = [t for t, x in zip(ta, thick) if x]
    if tk:
        txt += " Thick low cloud %s: poor surface contrast and horizon likely." % hours(tk)
        lev = "watch"; flags.append("poor contrast")
    wo = [t for t, a_, x, y, h in zip(ta, thick, pr, w, thr) if a_ and (x >= c["snow_trace"] or y >= h)]
    if wo:
        txt += " Whiteout risk %s (thick cloud with snowfall or drift)." % hours(wo)
        lev = "warn"; flags.append("whiteout risk")
    if frac >= 0.25 or tk:
        txt += " Cloud is the model's weakest field."
    items.append(dict(kind="Cloud", text=txt, level=lev))

    # --- temperature
    items.append(dict(kind="Temperature", level="ok",
                      text="%.0f to %.0f °C, wind chill down to %.0f °C." % (np.nanmin(T), np.nanmax(T), np.nanmin(wc))))

    # --- pressure: storm arrival (fall + warming) and clearing (steep rise)
    dp = np.array([change12(A, i, "mslp") for i in idx])
    dT = np.array([change12(A, i, "t2") for i in idx])
    if np.nanmin(dp) <= -c["pfall"]:
        i = int(np.nanargmin(dp))
        txt = "Falling fast: %.0f hPa in the 12 h to %02d UTC." % (-dp[i], ta[i].hour or 24)
        if dT[i] >= c["warm"]:
            txt += " With %.0f °C of warming: the classic sign of a depression arriving. Expect wind to rise." % dT[i]
        else:
            txt += " A sign of worsening weather."
        items.append(dict(kind="Pressure", level="watch", text=txt))
        flags.append("pressure falling")
    elif np.nanmax(dp) >= c["prise"]:
        items.append(dict(kind="Pressure", level="ok",
                          text="Rising fast: %.0f hPa in 12 h. After a storm this usually means wind easing and "
                               "skies clearing." % np.nanmax(dp)))

    # --- run-to-run consistency (same day, previous AMPS run)
    if P is not None and in_day(P, day).sum() >= len(ta):
        ip = in_day(P, day)
        pw, pt = np.nanmax(P["wspd"][ip]), float(np.nansum(P["apcp"][ip]))
        same_w = abs(pw - np.nanmax(w)) <= c["same_wind"]
        same_s = (pt >= c["snow"]) == (tot >= c["snow"])
        txt = "Previous run (%s): strongest wind %d kt, snow %.1f mm. " % (prev_label, kn(pw), pt)
        if same_w and same_s:
            txt += "Consistent with this run."
        else:
            ch = []
            if not same_w:
                ch.append("wind %s" % ("stronger now" if np.nanmax(w) > pw else "weaker now"))
            if not same_s:
                ch.append("snow %s" % ("new in this run" if tot >= c["snow"] else "dropped in this run"))
            txt += "Changed: %s. Treat as uncertain." % ", ".join(ch)
        items.append(dict(kind="Last run", text=txt, level="ok" if same_w and same_s else "watch"))

    return dict(date=day.strftime("%Y-%m-%d"), label=day.strftime("%a %d %b"), items=items, flags=flags,
                note="lower confidence (forecast day %d)" % (lead_day + 1) if lead_day >= 3 else None)


def summarise(cycle, slug, start):
    A = parse((OUT / ("%s_%s.csv" % (cycle, slug))).read_text())
    prev, P = previous(cycle, slug)
    pl = dt.datetime.strptime(prev, "%Y%m%d%H").strftime("%d %b %H UTC")
    c0 = dt.datetime.strptime(cycle, "%Y%m%d%H")
    d = dt.datetime(start.year, start.month, start.day)
    days = []
    while d + dt.timedelta(hours=12) <= A["time"][-1]:
        days.append(day_summary(d, A, P, pl, (d - dt.datetime(c0.year, c0.month, c0.day)).days, slug))
        d += dt.timedelta(days=1)
    watch = ["%s: %s" % (x["label"][:3], ", ".join(x["flags"])) for x in days if x["flags"]]
    head = ("Watch: " + "; ".join(watch) + ".") if watch else "No hazards flagged by AMPS."
    note = SITE_NOTE_EL.get(slug, "")
    return dict(cycle=cycle, site=slug, made=start.strftime("%Y-%m-%d %H:%M"), headline=head, site_note=note,
                days=days,
                disclaimer="Written automatically by fixed rules from the AMPS numbers, not by a forecaster. The rules are "
                           "taken from the International Antarctic Weather Forecasting Handbook (Turner & Pendlebury 2004): general "
                           "thresholds, plus each site's nearest station section (Asuka, Syowa, Molodezhnaya or Mount King). "
                           "The handbook describes those stations up to 2004 (Molodezhnaya and Mount King were already closed); "
                           "it is a guide for travel on the ice, not an aviation forecast. Mean wind only: gusts are stronger. Use the newest run, and trust what you see "
                           "and what the station forecaster says over the model.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycle")
    ap.add_argument("--from", dest="start", help="UTC 'YYYY-mm-dd HH:MM'; default now")
    a = ap.parse_args()
    cycle = a.cycle or sorted({p.name[:10] for p in OUT.glob("??????????_sites.json")})[-1]
    start = (dt.datetime.strptime(a.start, "%Y-%m-%d %H:%M") if a.start
             else dt.datetime.now(dt.timezone.utc).replace(tzinfo=None))
    start = max(start, dt.datetime.strptime(cycle, "%Y%m%d%H"))
    for s in json.loads((OUT / ("%s_sites.json" % cycle)).read_text()):
        S = summarise(cycle, s["slug"], start)
        (OUT / ("%s_%s_summary.json" % (cycle, s["slug"]))).write_text(json.dumps(S, indent=1, ensure_ascii=False),
                                                                      encoding="utf-8")
        print("\n=== %s  (AMPS %s)\n%s\n%s" % (s["name"], cycle, S["headline"], S["site_note"]))
        for dday in S["days"]:
            print("\n%s%s" % (dday["label"], "  [%s]" % dday["note"] if dday["note"] else ""))
            for it in dday["items"]:
                print("  %-11s %s%s" % (it["kind"], {"warn": "!! ", "watch": "! "}.get(it["level"], ""), it["text"]))


if __name__ == "__main__":
    main()
