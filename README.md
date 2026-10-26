# RINGS Enderby Meteograms

Five-day weather model output for the RINGS airborne survey in Enderby Land (East Antarctica), from
the Antarctic Mesoscale Prediction System (AMPS, NCAR; WRF 8 km). A copy of the
[MINIS Meteograms](https://github.com/vikramonice/minis-weather) site, set up on 26 October 2026.

**Site:** https://vikramonice.github.io/rings-enderby-weather/

**Model output, not a forecast.** The charts and notes are made automatically, with no forecaster
involved. They were first set up for a ground traverse in Dronning Maud Land and have not been
adapted to Enderby Land or to flying. The wind-aloft numbers are shown as the model gives them,
without interpretation. For flight decisions use the official forecast and the station forecaster.

## Sites (west to east, as the flights go from Syowa)

| Site | Position | AMPS grid point | Note |
|---|---|---|---|
| S17 (skiway near Syowa) | 69.03 S, 40.09 E | 1.0 km, model ground 592 m | reference near the start of the flights |
| E1 | 68.0 S, 45.0 E | 4.7 km, ~500 m | |
| E2 | 67.5 S, 49.0 E | 1.6 km, ~410 m | |
| E3 | 66.0 S, 53.0 E | 4.0 km, ~360 m | |
| E4 | 66.5 S, 56.5 E | 4.2 km, ~350 m | 22 km west of the requested 66.5 S, 57 E, whose grid point is at the coast (60 m) |

The positions may change; each site keeps its file name (`s17`, `e1` ... `e4`) so its history
continues. Sites are set in `SITES` at the top of [`amps/amps_meteogram.py`](amps/amps_meteogram.py).

Each meteogram shows temperature and wind chill, cloud by altitude and cloud base, snowfall, 10 m
wind, sea-level pressure, and **wind aloft at 850, 700 and 500 hPa** (arrows and knots, every 6 h).

**Station check:** Syowa (WMO 89532) reports every 3 h are compared with AMPS at Syowa's own grid
point (fetched for the check only; the cell is sea, the station is on an island). Molodezhnaya
(89542, near E1) reports are shown alongside.

**Season:** updates run until the end of February 2027 (`SEASON_END` in `publish.py`), then stop.

How the field weather notes are written: [RULES.md](RULES.md). In this copy the rules specific to
Dronning Maud Land (the weather-pattern rules from the Maitri section of the handbook) are switched
off; the general thresholds remain.

## How it updates

A GitHub Actions workflow (`.github/workflows/update.yml`) checks every 30 minutes while a new AMPS
run is due (09:00-12:00 and 21:00-00:30 UTC; runs finish about 10 h after 00/12 UTC).
`publish.py` reads the previous state from the `gh-pages` branch, fetches only the few hundred kB
of AMPS GRIB it needs (HTTP byte ranges), makes the charts, notes and station check, rebuilds the
page (the last 8 runs = 4 days) and force-pushes `gh-pages` as a single commit. A monthly
keep-alive stops GitHub disabling the schedule. Run it by hand from the Actions tab ("Run
workflow"); tick *rebuild* after changing the page template.

Map: `static/map.jpg` and `amps/amps_sites_map_web.json`, made by
`code/python/fieldwork/amps_site_map_enderby.py` in the Nivl project (MODIS Mosaic of Antarctica,
Bedmap3 coast and elevations).

Data: AMPS, NCAR, run for NSF. Station reports via ogimet.com.
