# jgtml
JGTML

* primarily designed to analyze the effectiveness of trading signals
* designed to analyze the effectiveness of trading signals within the context of larger balance lines.


----



CLI's HELP
_____

## jgtfxcli
```
usage: jgtfxcli [-h] [-i INSTRUMENT] [-t TIMEFRAME] [-r TLIDRANGE] [-vp] [-xe]
                [-z] [-c MAX | [-uf | -nf]] [-v VERBOSE] [-debug] [-iprop]
                [-server] [-kba | -rmba] [-dv | -ddv] [-pdsrq] [-pdsrqn]
                [-pdsrqnf] [-pdsrqf] [-pdsrqff] [-idsrq] [-cdsrq] [-cdsrqf]
                [-cdsrqff] [-cdsrqnf] [-jsonf JSON_FILE]

Process command parameters.

options:
  -h, --help            show this help message and exit
  -xe, --exitonerror    Exit on error rather than trying to keep looking
  -iprop, --iprop       Toggle the downloads of all instrument properties
  -server, --server     Run the server

POV:
  Point of view

  -i INSTRUMENT, --instrument INSTRUMENT
                        An instrument which you want to use in sample. For
                        example, "EUR/USD".
  -t TIMEFRAME, --timeframe TIMEFRAME
                        Time period which forms a single candle. For example,
                        m1 - for 1 minute, H1 - for 1 hour.

DTRange:
  Date and range selection

  -r TLIDRANGE, --range TLIDRANGE
                        TLID range in the format YYMMDDHHMM_YYMMDDHHMM.

Output:
  Output arguments

  -vp, --viewpath       flag to just view the path of files from arguments -i
                        -t.
  -z, --compress        Compress the output. If specified, it will also
                        activate the output flag.
  -jsonf JSON_FILE, --json_file JSON_FILE
                        JSON filepath content to be loaded.

Bars:
  Bars flags

  -c MAX, --quotescount MAX
                        Max number of bars. 0 - Not limited
  -uf, --full           Output/Input uses the full store.
  -nf, --notfull        Output/Input uses NOT the full store.

Verbosity:
  control the verbosity of the output

  -v VERBOSE, --verbose VERBOSE
                        Set the verbosity level. 0 = quiet, 1 = normal, 2 =
                        verbose, 3 = very verbose, etc.
  -debug, --debug       Toggle debug

Cleanup:
  Cleanup data

  -kba, --keepbidask    Keep Bid/Ask in storage.
  -rmba, --rmbidask     Remove Bid/Ask in storage.
  -dv, --dropna_volume  Drop rows with NaN (or 0) in volume column.
                        (note.Montly chart does not dropna volume)
  -ddv, --dont_dropna_volume
                        Do not dropna volume

RQ Pattern:
  RQ Pattern to use. Future practice to create request patterns to load into
  the args later.

  -pdsrq, --pds_rq_base
                        Use PDS_RQ JSON_BASE
  -pdsrqn, --pds_rq_normal
                        Use PDS_RQ JSON_NORMAL
  -pdsrqnf, --pds_rq_normal_fresh
                        Use PDS_RQ JSON_NORMAL_FRESH
  -pdsrqf, --pds_rq_full
                        Use PDS_RQ JSON_FULL
  -pdsrqff, --pds_rq_full_fresh
                        Use PDS_RQ JSON_FULL_FRESH
  -idsrq, --ids_rq_base
                        Use IDS_RQ JSON_BASE
  -cdsrq, --cds_rq_normal
                        Use CDS_RQ JSON_NORMAL
  -cdsrqf, --cds_rq_full
                        Use CDS_RQ JSON_FULL
  -cdsrqff, --cds_rq_full_fresh
                        Use CDS_RQ JSON_FULL_FRESH
  -cdsrqnf, --cds_rq_norm_fresh
                        Use CDS_RQ JSON_NORM_FRESH
```
 
---
 
## jgtcli
```
usage: jgtcli [-h] [-i INSTRUMENT] [-t TIMEFRAME] [-s "m.d.Y H:M:S"]
              [-e "m.d.Y H:M:S"] [-r TLIDRANGE] [-v VERBOSE] [-ads]
              [-c MAX | [-uf | -nf]] [-new | -old] [-mfi | -nomfi] [-go] [-ba]
              [-bjaw BALLIGATOR_PERIOD_JAWS] [-ta]
              [-tjaw TALLIGATOR_PERIOD_JAWS] [-lfp LARGEST_FRACTAL_PERIOD]
              [-vp] [-dv | -ddv] [-jsonf JSON_FILE] [-pdsrq] [-pdsrqn]
              [-pdsrqnf] [-pdsrqf] [-pdsrqff] [-idsrq] [-cdsrq] [-cdsrqf]
              [-cdsrqff] [-cdsrqnf]

jgtcli - Command Line Interface for JGTPY

options:
  -h, --help            show this help message and exit

POV:
  Point of view

  -i INSTRUMENT, --instrument INSTRUMENT
                        An instrument which you want to use in sample. For
                        example, "EUR/USD".
  -t TIMEFRAME, --timeframe TIMEFRAME
                        Time period which forms a single candle. For example,
                        m1 - for 1 minute, H1 - for 1 hour.

DTRange:
  Date and range selection

  -s "m.d.Y H:M:S", --datefrom "m.d.Y H:M:S"
                        Date/time from which you want to receive historical
                        prices. If you leave this argument as it is, it will
                        mean from last trading day. Format is "m.d.Y H:M:S".
                        Optional parameter.
  -e "m.d.Y H:M:S", --dateto "m.d.Y H:M:S"
                        Datetime until which you want to receive historical
                        prices. If you leave this argument as it is, it will
                        mean to now. Format is "m.d.Y H:M:S". Optional
                        parameter.
  -r TLIDRANGE, --range TLIDRANGE
                        TLID range in the format YYMMDDHHMM_YYMMDDHHMM.

Verbosity:
  control the verbosity of the output

  -v VERBOSE, --verbose VERBOSE
                        Set the verbosity level. 0 = quiet, 1 = normal, 2 =
                        verbose, 3 = very verbose, etc.

Interaction:
  Interaction arguments

  -ads, --ads           Action the creation of ADS and show the chart

Bars:
  Bars flags

  -c MAX, --quotescount MAX
                        Max number of bars. 0 - Not limited
  -uf, --full           Output/Input uses the full store.
  -nf, --notfull        Output/Input uses NOT the full store.
  -new, --fresh         Freshening the storage with latest market.
  -old, --notfresh      Output/Input wont be freshed from storage (weekend or
                        tests).

Indicators:
  Indicators flags

  -mfi, --mfi_flag      Enable the Market Facilitation Index indicator.
  -nomfi, --no_mfi_flag
                        Disable the Market Facilitation Index indicator.
  -go, --gator_oscillator_flag
                        Enable the Gator Oscillator indicator.
  -ba, --balligator_flag
                        Enable the Big Alligator indicator.
  -bjaw BALLIGATOR_PERIOD_JAWS, --balligator_period_jaws BALLIGATOR_PERIOD_JAWS
                        The period of the Big Alligator jaws.
  -ta, --talligator_flag
                        Enable the Tide Alligator indicator.
  -tjaw TALLIGATOR_PERIOD_JAWS, --talligator_period_jaws TALLIGATOR_PERIOD_JAWS
                        The period of the Tide Alligator jaws.
  -lfp LARGEST_FRACTAL_PERIOD, --largest_fractal_period LARGEST_FRACTAL_PERIOD
                        The largest fractal period.

Output:
  Output arguments

  -vp, --viewpath       flag to just view the path of files from arguments -i
                        -t.
  -jsonf JSON_FILE, --json_file JSON_FILE
                        JSON filepath content to be loaded.

Cleanup:
  Cleanup data

  -dv, --dropna_volume  Drop rows with NaN (or 0) in volume column.
                        (note.Montly chart does not dropna volume)
  -ddv, --dont_dropna_volume
                        Do not dropna volume

RQ Pattern:
  RQ Pattern to use. Future practice to create request patterns to load into
  the args later.

  -pdsrq, --pds_rq_base
                        Use PDS_RQ JSON_BASE
  -pdsrqn, --pds_rq_normal
                        Use PDS_RQ JSON_NORMAL
  -pdsrqnf, --pds_rq_normal_fresh
                        Use PDS_RQ JSON_NORMAL_FRESH
  -pdsrqf, --pds_rq_full
                        Use PDS_RQ JSON_FULL
  -pdsrqff, --pds_rq_full_fresh
                        Use PDS_RQ JSON_FULL_FRESH
  -idsrq, --ids_rq_base
                        Use IDS_RQ JSON_BASE
  -cdsrq, --cds_rq_normal
                        Use CDS_RQ JSON_NORMAL
  -cdsrqf, --cds_rq_full
                        Use CDS_RQ JSON_FULL
  -cdsrqff, --cds_rq_full_fresh
                        Use CDS_RQ JSON_FULL_FRESH
  -cdsrqnf, --cds_rq_norm_fresh
                        Use CDS_RQ JSON_NORM_FRESH
```
 
---
 
## jgtmlttfcli
```
usage: jgtmlttfcli [-h] -i INSTRUMENT -t TIMEFRAME [-uf] [-new] [-fr]
                   [-c QUOTESCOUNT]
                   [-clh COLUMNS_LIST_FROM_HIGHER_TF [COLUMNS_LIST_FROM_HIGHER_TF ...]]
                   [-pn PATTERNNAME]

Create ttf CSV file

options:
  -h, --help            show this help message and exit
  -i INSTRUMENT, --instrument INSTRUMENT
                        Instrument name
  -t TIMEFRAME, --timeframe TIMEFRAME
                        Timeframe (e.g., D1, H4)
  -uf, --full           Use full dataset
  -new, --fresh         Use fresh data
  -fr, --force_read     Force to read CDS (should increase speed but relies on
                        existing data)
  -c QUOTESCOUNT, --quotescount QUOTESCOUNT
                        Number of quotes to retrieve (default: 333)
  -clh COLUMNS_LIST_FROM_HIGHER_TF [COLUMNS_LIST_FROM_HIGHER_TF ...], --columns_list_from_higher_tf COLUMNS_LIST_FROM_HIGHER_TF [COLUMNS_LIST_FROM_HIGHER_TF ...]
                        List of columns to get from higher TF
  -pn PATTERNNAME, --patternname PATTERNNAME
                        Pattern Name
```
 
---
 
## jgtmlcli
```
usage: jgtmlcli [-h] [-i INSTRUMENT] [-t TIMEFRAME] [-r TLIDRANGE]
                [-v VERBOSE] [-uf | -nf] [-new | -old] [-kba | -rmba]
                [-mfi | -nomfi] [-go] [-ba] [-bjaw BALLIGATOR_PERIOD_JAWS]
                [-ta] [-tjaw TALLIGATOR_PERIOD_JAWS]
                [-lfp LARGEST_FRACTAL_PERIOD] [-dv | -ddv] [-rcds]
                [-sc SELECTED_COLUMNS [SELECTED_COLUMNS ...]] [-ddcc]
                [-pn PATTERNNAME]

Process command parameters.

options:
  -h, --help            show this help message and exit
  -uf, --full           Output/Input uses the full store.
  -nf, --notfull        Output/Input uses NOT the full store.
  -rcds, --regenerate_cds
                        Regenerate the CDS
  -sc SELECTED_COLUMNS [SELECTED_COLUMNS ...], --selected-columns SELECTED_COLUMNS [SELECTED_COLUMNS ...]
                        List of selected columns to keep
  -ddcc, --dont_drop_calc_col
                        Dont drop calculated columns
  -pn PATTERNNAME, --patternname PATTERNNAME
                        Pattern Name

POV:
  Point of view

  -i INSTRUMENT, --instrument INSTRUMENT
                        An instrument which you want to use in sample. For
                        example, "EUR/USD".
  -t TIMEFRAME, --timeframe TIMEFRAME
                        Time period which forms a single candle. For example,
                        m1 - for 1 minute, H1 - for 1 hour.

DTRange:
  Date and range selection

  -r TLIDRANGE, --range TLIDRANGE
                        TLID range in the format YYMMDDHHMM_YYMMDDHHMM.

Verbosity:
  control the verbosity of the output

  -v VERBOSE, --verbose VERBOSE
                        Set the verbosity level. 0 = quiet, 1 = normal, 2 =
                        verbose, 3 = very verbose, etc.

Bars:
  Bars flags

  -new, --fresh         Freshening the storage with latest market.
  -old, --notfresh      Output/Input wont be freshed from storage (weekend or
                        tests).

Cleanup:
  Cleanup data

  -kba, --keepbidask    Keep Bid/Ask in storage.
  -rmba, --rmbidask     Remove Bid/Ask in storage.
  -dv, --dropna_volume  Drop rows with NaN (or 0) in volume column.
                        (note.Montly chart does not dropna volume)
  -ddv, --dont_dropna_volume
                        Do not dropna volume

Indicators:
  Indicators flags

  -mfi, --mfi_flag      Enable the Market Facilitation Index indicator.
  -nomfi, --no_mfi_flag
                        Disable the Market Facilitation Index indicator.
  -go, --gator_oscillator_flag
                        Enable the Gator Oscillator indicator.
  -ba, --balligator_flag
                        Enable the Big Alligator indicator.
  -bjaw BALLIGATOR_PERIOD_JAWS, --balligator_period_jaws BALLIGATOR_PERIOD_JAWS
                        The period of the Big Alligator jaws.
  -ta, --talligator_flag
                        Enable the Tide Alligator indicator.
  -tjaw TALLIGATOR_PERIOD_JAWS, --talligator_period_jaws TALLIGATOR_PERIOD_JAWS
                        The period of the Tide Alligator jaws.
  -lfp LARGEST_FRACTAL_PERIOD, --largest_fractal_period LARGEST_FRACTAL_PERIOD
                        The largest fractal period.
```
 
---
 
## jgtmlfcli
```
usage: jgtmlfcli [-h] [-lp LAG_PERIOD] [-tlp TOTAL_LAGGING_PERIODS]
                 [-ctk COLUMNS_TO_KEEP [COLUMNS_TO_KEEP ...]]
                 [-ctd COLUMNS_TO_DROP [COLUMNS_TO_DROP ...]] [-f] [-mfiao]
                 [-dba] [-pn PATTERNNAME] [-i INSTRUMENT] [-t TIMEFRAME]
                 [-c MAX | [-uf | -nf]] [-new | -old] [-dv | -ddv] [-fr]

Create mlf alpha CSV file

options:
  -h, --help            show this help message and exit
  -lp LAG_PERIOD, --lag_period LAG_PERIOD
                        Lag period
  -tlp TOTAL_LAGGING_PERIODS, --total_lagging_periods TOTAL_LAGGING_PERIODS
                        Total lagging periods
  -ctk COLUMNS_TO_KEEP [COLUMNS_TO_KEEP ...], --columns_to_keep COLUMNS_TO_KEEP [COLUMNS_TO_KEEP ...]
                        List of selected columns to keep
  -ctd COLUMNS_TO_DROP [COLUMNS_TO_DROP ...], --columns_to_drop COLUMNS_TO_DROP [COLUMNS_TO_DROP ...]
                        List of selected columns to drop
  -f, --force_refresh   Force refresh
  -mfiao, --mfiao       Use mfiao
  -dba, --drop_bidask   Drop bidask
  -pn PATTERNNAME, --patternname PATTERNNAME
                        Pattern Name
  -fr, --force_read     Force to read CDS (should increase speed but relies on
                        existing data)

POV:
  Point of view

  -i INSTRUMENT, --instrument INSTRUMENT
                        An instrument which you want to use in sample. For
                        example, "EUR/USD".
  -t TIMEFRAME, --timeframe TIMEFRAME
                        Time period which forms a single candle. For example,
                        m1 - for 1 minute, H1 - for 1 hour.

Bars:
  Bars flags

  -c MAX, --quotescount MAX
                        Max number of bars. 0 - Not limited
  -uf, --full           Output/Input uses the full store.
  -nf, --notfull        Output/Input uses NOT the full store.
  -new, --fresh         Freshening the storage with latest market.
  -old, --notfresh      Output/Input wont be freshed from storage (weekend or
                        tests).

Cleanup:
  Cleanup data

  -dv, --dropna_volume  Drop rows with NaN (or 0) in volume column.
                        (note.Montly chart does not dropna volume)
  -ddv, --dont_dropna_volume
                        Do not dropna volume
```
 
---
 
## jgtapp
```
usage: jgtapp [-h] {tide,pds,cds,ocds,ttf,ttfmxwf,mx,ttfwf} ...

CLI equivalent of bash functions

positional arguments:
  {tide,pds,cds,ocds,ttf,ttfmxwf,mx,ttfwf}
    tide                Run the pto tidealligator
    pds                 Refresh the PDS full for an instrument and timeframe
    cds                 Refresh the CDS
    ocds                Refresh the CDS from old PDS
    ttf                 Refresh the TTF for an instrument and timeframe
    ttfmxwf             Refresh the TTF, MX and CDS for an instrument
    mx                  Refresh the MX (using the TTF) for an instrument and
                        timeframe
    ttfwf               Refresh TTF preparation for an instrument

options:
  -h, --help            show this help message and exit
```
 
---
 
