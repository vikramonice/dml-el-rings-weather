# How the field weather notes are written

> **DML/EL RINGS page.** The [DML/EL RINGS page](https://vikramonice.github.io/dml-el-rings-weather/)
> uses the **general thresholds** described further down (drifting and blowing snow, snowfall, low
> cloud and contrast, pressure changes), plus **rules from the nearest station section of the
> handbook** for each site (next section). The Maitri / Dakshin Gangotri pattern rules from the
> MINIS page are switched off here. The meteograms themselves have no rules: they are AMPS model
> data, and the wind-aloft panel shows the numbers only. The station check uses Syowa (89532) and
> Molodezhnaya (89542).

## DML/EL RINGS: rules from the nearest station section

Source: *International Antarctic Weather Forecasting Handbook* (Turner & Pendlebury, eds., British
Antarctic Survey, 2004; open access at
[NORA](https://nora.nerc.ac.uk/id/eprint/17324/1/handbook_16june04.pdf)). Printed page numbers.

| Site | Section used | Distance | Pages |
|---|---|---|---|
| PEA | 7.5.9 Inland of Syowa: Asuka (Sør Rondane, 930 m) | ~30 km | 346-350 |
| W1 | 7.5.10 Syowa Station (W1 lies between Asuka and Syowa: an approximation) | ~350 km | 350-354 |
| S17 | 7.5.10 Syowa Station | ~20 km | 350-354 |
| E1, E2 | 7.6.1 Molodezhnaya Station | ~40 km, ~150 km | 354-362 |
| E3, E4 | 7.6.2 Mount King (summer camp 1975-80; four summers of notes) | ~120 km, ~170 km | 362-366 |

Limits: the handbook describes these stations up to 2004 (Molodezhnaya and Mount King were already
closed). It is climate and forecasting experience for the stations, not an aviation forecast, and
none of it was written for the exact sites here.

Each rule below is a note that appears only when the AMPS numbers meet the condition. "Ours" marks a
threshold we chose to turn the handbook's description into a test on 3-hourly model values.

| Section | Note appears when (AMPS) | What the handbook says | Ours |
|---|---|---|---|
| Syowa | surface wind from 22.5-78.75° (NE-ENE) at 10 m/s or more | blizzards occur only with wind from the NE or ENE (p. 352) | 10 m/s |
| Syowa | same, with pressure falling 3 hPa or more in 3 h: shown in red | falls of 3-5 hPa per hour may come with blizzards developing (p. 352) | 3 hPa / 3 h (AMPS is 3-hourly) |
| Syowa | easterly (78.75-112.5°) at 7 m/s or more, 03-09 UTC | katabatic winds reach 10 m/s or more in the morning, cease in the afternoon (p. 352) | 7 m/s, the time window |
| Syowa | 500 hPa wind from 315-45° (north) at 10 m/s or more | upper northerlies of 10 m/s or more bring bad weather; southerlies good weather (p. 352) | the sector |
| Syowa | 500 hPa wind from 270-330° at 15 m/s or more, up 5 m/s in 12 h | an increasing 500 hPa wind from about 300° calls for caution: a low approaching, a major blizzard may develop (pp. 352-353) | 15 m/s, +5 m/s |
| Syowa, Molodezhnaya | temperature up 10 °C or more within 6 h | a rise of about 10 °C in 3-4 h, from the inversion breaking up, may come with a blizzard (Syowa, p. 354) | 6 h (3-hourly data) |
| Molodezhnaya | south-easterly (112.5-157.5°) at 7 m/s or more, 21-03 UTC | the SE wind (~140°) is the katabatic; in summer mainly 01-05 local time, gusts 25-30 m/s (p. 358) | 7 m/s, the window |
| Molodezhnaya | E-SE wind at 15 m/s or more while pressure has risen 3 hPa in 12 h | the strongest winds come in the rear of a cyclone, when katabatic and cyclonic winds coincide (p. 358) | 15 m/s, 3 hPa |
| Molodezhnaya | thin low cloud (saturated below 1.5 km, layer under 1.5 km deep), 06-15 UTC, wind under 10 m/s | white-out in sunny weather with thin, broken stratus; flights over the dome best with a cloud-free forecast (p. 360) | the cloud test, the window |
| Mount King | surface wind from 22.5-67.5° (NE) at 5 m/s or more | north-easterly airstreams are almost invariably very moist, with extensive low cloud (p. 364) | 5 m/s |
| Mount King | 500 hPa wind from 247.5-337.5° at 10 m/s or more, with cloud or snow that day | most deteriorations came from the north-west with upper north-westerly flow, even with easterly surface wind (pp. 364-365) | the sector, 10 m/s |
| Mount King | no northerly component in the 500 hPa wind all day, little low cloud, no NE flow | the only substantial nil-cloud period came with no northerly component in the upper winds (p. 364) | the cloud limit |

Site notes (one per site, shown above the day-by-day notes) summarise the section: PEA, katabatic
zone with annual mean wind over 12 m/s and frequent deep blowing snow (Asuka, p. 348); S17 and W1,
Syowa's blizzard direction and morning katabatic, and the sudden loss of visibility when the
katabatic reaches the coast (p. 353); E1 and E2, Molodezhnaya's E/SE winds and night katabatic;
E3 and E4, Mount King's easterly wind, weather from the north-west and moist north-easterlies.

Code: `regional()` in [`amps/amps_summary.py`](amps/amps_summary.py).

---

*The rest of this page is the original MINIS rule record; its general thresholds also apply here.*

The **field weather notes** on the [MINIS Meteograms page](https://vikramonice.github.io/minis-weather/)
are the meteogram in words. They are written **automatically, by fixed rules**, from the numbers of
the AMPS weather model for each site. There is no forecaster in the loop and no free text: every
sentence is a template that appears only when a number crosses a threshold. This page lists every
rule, where it comes from, and its limits, so anyone can check what the notes mean.

Code: [`amps/amps_summary.py`](amps/amps_summary.py) (rules), [`amps/amps_meteogram.py`](amps/amps_meteogram.py)
(how the numbers are read from AMPS), [`amps/amps_verify.py`](amps/amps_verify.py) (check against
station reports).

## Source

**International Antarctic Weather Forecasting Handbook** (J. Turner and S. Pendlebury, eds.,
British Antarctic Survey, 2004):

- section 7.5.7 *Maitri and Dakshin Gangotri* (Dakshin Gangotri was an Indian station on the ice
  shelf about 17 km north of Depot 43D, so its notes serve the ice-shelf sites),
- section 7.5.8 *Novolazarevskaya*,
- sections 6.6.5–6.6.6 *surface contrast and horizon*.

Grain of salt: the handbook describes the physics and typical behaviour; several exact cut-off
values below are our own practical choices. The table marks which is which.

## The numbers the rules use

AMPS (Antarctic Mesoscale Prediction System, NCAR; Polar WRF on an 8 km grid) runs at 00 and
12 UTC and forecasts 5 days ahead. For each site the page takes the **nearest 8 km grid point**,
every **3 hours**:

| Quantity | How it is obtained |
|---|---|
| Wind speed and direction | 10 m wind, rotated from the model grid to true north. **Mean wind only: AMPS publishes no gusts.** |
| Temperature | 2 m air temperature |
| Wind chill | Standard wind-chill formula (Environment Canada / US NWS) with the 10 m wind, when wind > 4.8 km/h |
| Snowfall | Precipitation in the 3 h step, mm of water |
| Pressure | Sea-level pressure |
| Low-cloud humidity | Highest relative humidity **over ice** in the lowest 1.5 km above the model ground (converted from the model's humidity over water with the Magnus formula, Alduchov & Eskridge 1996) |
| Thick low cloud | Depth of the saturated layer (humidity over ice ≥ 95 %) whose base is within 1.5 km of the ground |

A **day** is the eight 3-hourly values ending within that UTC day (03, 06, … 21, 24 UTC).

## The rules

| Topic | Rule (exactly as coded) | What appears in the notes | Basis |
|---|---|---|---|
| **Drifting snow** | Mean wind ≥ **10 m/s (20 kt)**; ≥ **7 m/s (14 kt)** if ≥ **0.5 mm** of snow fell in the previous 48 h | "Drifting snow likely HH–HH UTC" (+ "fresh snow drifts from about 14 kt") · amber | Handbook: drift from about 10 m/s, earlier on fresh snow. **7 m/s and 0.5 mm: our choice** |
| **Blowing snow** | Mean wind ≥ **18 m/s (35 kt)** | "Blowing snow likely …: visibility poor to nil" · red | Handbook: blowing snow from about 18 m/s |
| **Wind line** | Prevailing direction (vector mean of winds > 2 m/s), daily range, time and direction of the strongest wind | "E 19–29 kt (10–15 m/s), strongest around 12 UTC from E" | Description only |
| **Storm pattern** | Wind ≥ 5 m/s from **60–157°** (east to south-east) **and** (pressure fell ≥ 2 hPa in 12 h **or** ≥ 0.2 mm of snow that day) | "Easterly to south-easterly wind … a depression approaching from the west. This is the storm pattern here." · amber | Handbook (Maitri): east to south-east winds come with depressions to the west; storms and snow. **Thresholds: our choice** |
| **Katabatic wind** (Maitri and A12 only) | Wind ≥ 5 m/s from **157–210°** (south) | "Southerly katabatic wind …: usually clear, dry air. Onsets can be sudden, from calm to 25–30 kt, with equally sudden lulls." · amber if the day's wind reaches 7 m/s | Handbook (Maitri): southerly winds are katabatic, with sudden onsets and lulls |
| **Ridge** | No storm or katabatic spell, wind ≥ 5 m/s, strongest from 300–30° | "Northerly: a ridge passing, usually light winds." | Handbook (Maitri) |
| **Snow** | Daily total < 0.2 mm → "None expected"; otherwise amount and timing; ≥ **0.5 mm** → amber + "loose fresh snow drifts at lower wind speeds for the next two days"; snow falling with wind < 5 m/s → "lies loose"; ≥ **2 mm** at an ice-shelf site → "Mark depots and instruments." | "6.4 mm water (about 6 cm of fresh snow) …" | 1 mm of water ≈ 1 cm of fresh snow (density about 100 kg/m³). **Levels: our choice** |
| **Low cloud** | Share of the day's steps with low-cloud humidity ≥ 95 %: ≥ 60 % "likely most of the day", ≥ 25 % "at times", else "unlikely" | "Low cloud likely most of the day." | **Our choice** (no cloud-cover output in AMPS GRIB) |
| **Poor contrast** | Thick low cloud: saturated layer ≥ **1.5 km** deep, based within 1.5 km of the ground | "Thick low cloud …: poor surface contrast and horizon likely" · amber | Handbook 6.6.5–6.6.6: contrast and horizon are lost under deep, featureless low cloud. **95 %, 1.5 km: our choice** |
| **Whiteout risk** | Thick low cloud **and** (snow ≥ 0.2 mm or drifting snow) in the same step | "Whiteout risk … (thick cloud with snowfall or drift)" · red | Handbook: whiteout = no contrast with falling or drifting snow |
| **Cloud caveat** | Added whenever low cloud is mentioned | "Cloud is the model's weakest field." | Known weakness of models in Antarctica |
| **Temperature** | Daily minimum and maximum, lowest wind chill | "−12 to −9 °C, wind chill down to −24 °C" | Description only |
| **Pressure falling** | Fall ≥ **4 hPa in 12 h** | "Falling fast … A sign of worsening weather." · amber | Handbook: falling pressure precedes depressions. **4 hPa/12 h: our choice** |
| **Classic storm arrival** | Fall ≥ 4 hPa **and** warming ≥ **5 °C** in the same 12 h | "With … warming: the classic sign of a depression arriving. Expect wind to rise." | Handbook: pressure falls while the surface inversion breaks up and it warms. **5 °C: our choice** |
| **Clearing** | Rise ≥ **4 hPa in 12 h** | "Rising fast … After a storm this usually means wind easing and skies clearing." | Handbook. **4 hPa: our choice** |
| **Last run** | Same day in the AMPS run 12 h older: strongest wind within **3 m/s** and snow (≥ 0.5 mm) yes/no the same | "Consistent with this run" or "Changed: wind stronger now … Treat as uncertain" · amber if changed | General forecasting practice: a hazard seen in both runs is more trustworthy. **3 m/s: our choice** |
| **Lead time** | Forecast day 4 and 5 | "lower confidence (forecast day 4)" | Model errors grow with lead time |

**Site note** (shown once per site):

- ice-shelf sites (Depot 43D, MN_04, C13): *"On the ice shelf, blizzards are stronger and last
  longer than at Maitri, and the strong winds come from the east to south-east"* (handbook,
  Dakshin Gangotri);
- foot of the ice sheet (Maitri, A12): *"strong winds come from the south-east with storms;
  southerly winds are katabatic"* (handbook, Maitri).

**Headline**: the amber and red flags of each day, e.g. *"Watch: Fri: drifting snow, snow, poor
contrast, whiteout risk; Sat: …"*. If nothing is flagged: *"No hazards flagged by AMPS."*

## Worked example

Depot 43D, Friday 23 October 2026, AMPS run of 23 Oct 00 UTC. The model gave wind 10–15 m/s from
the east, 6.4 mm of snowfall, a saturated layer several km deep from near the ground, −12 to −9 °C
(wind chill −24 °C), pressure rising from 986 to 990 hPa.

| Rule | Numbers | Result |
|---|---|---|
| Drift | snow fell → threshold 7 m/s; wind ≥ 7 m/s from 03 UTC | *Drifting snow likely 03–24 UTC (fresh snow drifts from about 14 kt)* |
| Blowing snow | maximum 15 m/s < 18 | not shown |
| Pattern | east wind ≥ 5 m/s with snow | *storm pattern* |
| Snow | 6.4 mm ≥ 2 mm, shelf site | *about 6 cm of fresh snow … Mark depots and instruments* |
| Contrast | saturated layer > 1.5 km deep all day | *poor surface contrast and horizon likely* |
| Whiteout | thick cloud + snow + drift | *Whiteout risk 03–24 UTC* |
| Pressure | +4 hPa in 12 h | *Rising fast … wind easing and skies clearing* |
| Last run | previous run: 30 kt, 6.6 mm | *Consistent with this run* |

## Check against real weather

Every update compares what the page showed with the 6-hourly SYNOP reports of **Maitri** (WMO
89514) and **Novolazarevskaya** (89512, 28 km west), from [Ogimet](https://www.ogimet.com). Each
Maitri report is compared with the AMPS Maitri value from the **newest run that was on the page at
that time** (run start + 10 h before the report), i.e. what the field team actually saw; once
stored, a comparison is never changed.

- **Bias** = AMPS minus observed (temperature, wind speed); **mean absolute error** alongside.
- **Katabatic nights** (00 and 06 UTC reports with wind ≥ 7 m/s from 150–260°): caught, missed,
  false alarms.
- Shown for the last 7 days and the whole record (kept 120 days).

Read it as a correction: for example "AMPS about 3 °C too cold" means expect it warmer than shown.

## Limits

- The notes are only as good as AMPS, and AMPS is only as good as an 8 km model can be near a
  coast, an ice front and an oasis.
- **Mean wind only.** Gusts are stronger than any wind given here.
- **Cloud is the model's weakest field;** contrast and whiteout are inferred from humidity, not
  observed cloud.
- Cut-off values marked "our choice" are reasonable starting points, not tuned to Nivlisen. They
  can be adjusted as the station check builds up.
- **What you see on site comes first.**

## Change log

- 2026-10-23: rules documented here; section renamed "Field weather notes" (was "Model guidance").
