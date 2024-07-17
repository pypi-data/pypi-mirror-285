"""
Common code for generation of tray files for green and yellow tagged SiPMs
from a given wafer, and also filling blank SiPM entries in given tray files.
"""

import asyncio
import contextlib
import functools
import io
import itertools
import operator
import os
import random
import re
import sys
import textwrap

import aiohttp
import numpy as np
import pandas as pd

try:
    from ds20kdb import interface
except ModuleNotFoundError:
    print('Please install ds20kdb-avt')
    sys.exit(3)


##############################################################################
# data structures
##############################################################################


class SiPM:
    """
    Basic data container used for SiPMs.

    This requires network access.
    """
    __slots__ = {
        'lot_number': 'Wafer lot number, 7-digits, e.g. 9306869',
        'wafer_number': 'Wafer number, 1-2 digits in the range 1-25',
        'column': 'Physical location of this SiPM on the wafer',
        'row': 'Physical location of this SiPM on the wafer',
    }

    def __init__(self, column, row, lot_number=None, wafer_number=None):
        self.lot_number = lot_number if lot_number is None else int(lot_number)
        self.wafer_number = wafer_number if wafer_number is None else int(wafer_number)
        self.column = int(column)
        self.row = int(row)

    def __repr__(self):
        return (
            'SiPM('
            f'lot_number={self.lot_number}, '
            f'wafer_number={self.wafer_number}, '
            f'column={self.column}, '
            f'row={self.row})'
        )

    def __str__(self):
        contents = {
            'lot number': self.lot_number,
            'wafer number': self.wafer_number,
            'SiPM column': self.column,
            'SiPM row': self.row,
        }
        return ', '.join(f'{k}={v:>3}' for k, v in contents.items())


##############################################################################
# Methods of identifying good/bad SiPMs
##############################################################################


def identify_sipm_status(dbi, classification, wafer_pid, sequential, no_b_grade, qcid=None, nounusablesipmcheck=False):
    """
    For the given wafer, obtain two sets of wafer (column, row) pairs, for
    good/bad SiPMs respectively. Chooses between two methods of accomplishing
    this goal.

    Notes from 2023 12 06:

    The sipm_test.classification good/bad flag was historically used to
    indicate whether SiPMs were deemed acceptable for use in production. This
    should be true again at some point in the future.

    Currently, a more complex lookup is required. For a given SiPM ID, only the
    row with the largest value of sipm_test.sipm_qc_id is considered.
    From that row, for the SiPM to be regarded as good it must have
    sipm_test.classification == 'good' and sipm_test.quality_flag == 0.

    --------------------------------------------------------------------------
    args
        dbi : ds20kdb.interface.Database
            Instance of the Database interface class; allows communication
            with the database.
        full : bool
            Perform a comprehensive check of SiPM status.
        wafer_pid : int
        sequential : bool
        no_b_grade : bool
        qcid : bool
        nounusablesipmcheck : bool
    --------------------------------------------------------------------------
    returns (set, set, set) or None
    --------------------------------------------------------------------------
    """
    response = dbi.get('sipm', wafer_id=wafer_pid)
    if response.network_timeout:
        print('WARNING: network timeout')
        return None

    dfr = response.data

    if dfr.empty:
        print('WARNING: empty response')
        return None

    if classification:
        return sipm_status_by_classification(dbi, dfr)

    if nounusablesipmcheck:
        unusable_sipm_ids = set()
    else:
        unusable_sipm_ids = set(dbi.get('unusable_sipm').data.sipm_id.values)

    if sequential:
        return sipm_status_full_check(dbi, dfr, unusable_sipm_ids, no_b_grade, qcid)

    return sipm_status_whole_table(dbi, dfr, unusable_sipm_ids, no_b_grade, qcid)


def sipm_status_by_classification(dbi, dfr):
    """
    For the given wafer, obtain two sets of wafer (column, row) pairs, for
    good/bad SiPMs respectively.

    Uses just sipm_test.classification for the evaluation.

    Note that this check as currently implemented is overly pessimistic. If a
    SiPM ID has ever been assigned a bad classification, it will show as bad
    here. In Q4 2023, <1% of SiPM IDs had multiple entries, and a later
    corrected entry may contain a good result.

    --------------------------------------------------------------------------
    args
        dbi : ds20kdb.interface.Database
            Instance of the Database interface class; allows communication
            with the database.
        dfr : Pandas DataFrame
    --------------------------------------------------------------------------
    returns (set, set, set)
    --------------------------------------------------------------------------
    """
    print('Obtaining SiPMs with bad classification(s)')

    bad_sipm_ids = set(dbi.get('sipm_test', classification='bad').data.sipm_id)
    wafer_map_bad = {
        (col, row)
        for sipm_pid, col, row in zip(dfr.sipm_pid, dfr.column, dfr.row)
        if sipm_pid in bad_sipm_ids
    }

    all_locations = set(interface.wafer_map_valid_locations())
    wafer_map_good = all_locations.difference(wafer_map_bad)

    wafer_map_b_grade = {}
    return wafer_map_good, wafer_map_b_grade, wafer_map_bad


def identify_b_grade_sipms(dbi, dfr, good_sipm_ids, qcid, sipm_test):
    """
    SK's additional checks based on device performance.

    Here we are returning generally good SiPMs. These passed electrical and
    visual inspection at LFoundry, and passed electrical tests at NOA.
    However, their performance is at the margins of acceptable performance.

    These SiPMs will not be discarded, they will be retained and handled as
    production silicon, except that they will not be used in production
    vTiles. They may be used towards the end of production if required.

    --------------------------------------------------------------------------
    args
        dbi : ds20kdb.interface.Database
            Instance of the Database interface class; allows communication
            with the database.
        dfr : Pandas DataFrame
        good_sipm_ids : set of int
        qcid : int
        sipm_test : pandas DataFrame
    --------------------------------------------------------------------------
    returns set of tuple
        e.g. {(int, int), ...} or None
        notionally these are B-grade SiPMs
    --------------------------------------------------------------------------
    """
    try:
        sipm = SiPMCheck(dbi, qcid, sipm_test)
    except (LookupError, TimeoutError):
        return None

    b_grade_sipm_ids = {
        sipm_id
        for sipm_id in good_sipm_ids
        if not sipm.production_standard(sipm_id)
    }

    return {
        (col, row)
        for sipm_pid, col, row in zip(dfr.sipm_pid, dfr.column, dfr.row)
        if sipm_pid in b_grade_sipm_ids
    }


def wafer_map_sets(dbi, dfr, good_sipm_ids, no_b_grade, qcid, sipm_test=None):
    """
    Generate the sets of locations necessary to generate the wafer map.

    --------------------------------------------------------------------------
    args
        dbi : ds20kdb.interface.Database
            Instance of the Database interface class; allows communication
            with the database.
        dfr : Pandas DataFrame
        good_sipm_ids : set of int
        no_b_grade : bool
        qcid : int
        sipm_test : pandas DataFrame
    --------------------------------------------------------------------------
    returns (set of tuple, set of tuple, set of tuple)
        where each tuple is a pair of column, row values
    --------------------------------------------------------------------------
    """
    wafer_map_good = {
        (col, row)
        for sipm_pid, col, row in zip(dfr.sipm_pid, dfr.column, dfr.row)
        if sipm_pid in good_sipm_ids
    }

    # Add SK's additional checks for device performance
    if no_b_grade:
        wafer_map_b_grade = set()
    else:
        wafer_map_b_grade = identify_b_grade_sipms(dbi, dfr, good_sipm_ids, qcid, sipm_test)
        if wafer_map_b_grade is None:
            wafer_map_b_grade = set()
            print('ERROR: could not read status of b-grade SiPMs')

    wafer_map_good -= wafer_map_b_grade

    all_locations = set(interface.wafer_map_valid_locations())
    wafer_map_bad = all_locations - wafer_map_good - wafer_map_b_grade

    if not wafer_map_good:
        print('WARNING: no good SiPMs found.')

    return wafer_map_good, wafer_map_b_grade, wafer_map_bad


def sipm_status_full_check(dbi, dfr, unusable_sipm_ids, no_b_grade, qcid):
    """
    For the given wafer, obtain two sets of wafer (column, row) pairs, for
    good/bad SiPMs respectively.

    Uses sipm_test.classification, sipm_test.quality_flag and
    sipm_test.sipm_qc_id for the evaluation.

    --------------------------------------------------------------------------
    args
        dbi : ds20kdb.interface.Database
            Instance of the Database interface class; allows communication
            with the database.
        dfr : Pandas DataFrame
        unusable_sipm_ids : set of int
        no_b_grade : bool
        qcid : int
    --------------------------------------------------------------------------
    returns (set of tuple, set of tuple, set of tuple)
        where each tuple is a pair of column, row values
    --------------------------------------------------------------------------
    """
    # this will give us 268 SiPM IDs, not 264
    all_sipms_ids_for_wafer = set(dfr.sipm_pid.values)

    columns = ['classification', 'quality_flag', 'sipm_qc_id', 'timestamp']

    good_sipm_ids = set()
    for sipm_id in all_sipms_ids_for_wafer:
        dfr_all_qc = dbi.get('sipm_test', sipm_id=sipm_id).data
        if qcid is not None:
            dfr_tmp = dfr_all_qc.loc[dfr_all_qc['sipm_qc_id'] == qcid]
        else:
            dfr_tmp = dfr_all_qc

        # Get columns for row with highest sipm_qc_id value.
        try:
            classification, quality_flag, *_ = dfr_tmp[columns].sort_values(
                ['sipm_qc_id', 'timestamp'], ascending=[True, True]
            ).values[-1]
        except IndexError:
            # We will see IndexError for the four SiPMs at the far left/right
            # edges that are not tested.
            pass
        else:
            if classification == 'good' and quality_flag == 0:
                good_sipm_ids.add(sipm_id)

    good_sipm_ids -= unusable_sipm_ids

    return wafer_map_sets(dbi, dfr, good_sipm_ids, no_b_grade, qcid)


def sipm_status_whole_table(dbi, dfr, unusable_sipm_ids, no_b_grade, qcid):
    """
    For the given wafer, obtain two sets of wafer (column, row) pairs, for
    good/bad SiPMs respectively.

    Uses sipm_test.classification, sipm_test.quality_flag and
    sipm_test.sipm_qc_id for the evaluation.

    Class SiPMCheck needs the entire sipm_test table. We need a subset of that
    table here, so it's more efficient just to load the whole table here and
    pass it to SiPMCheck.

    --------------------------------------------------------------------------
    args
        dbi : ds20kdb.interface.Database
            Instance of the Database interface class; allows communication
            with the database.
        dfr : Pandas DataFrame
        unusable_sipm_ids : set of int
        no_b_grade : bool
        qcid : int
    --------------------------------------------------------------------------
    returns (set of tuple, set of tuple, set of tuple) or None
        where each tuple is a pair of column, row values
    --------------------------------------------------------------------------
    """
    # this will give us 268 SiPM IDs, not 264
    all_sipms_ids_for_wafer = set(dfr.sipm_pid.values)

    response = dbi.get('sipm_test')
    if response.network_timeout:
        print('Network timeout')
        return None
    if response.data is None:
        print('No response')
        return None
    sipm_test = response.data

    columns = ['classification', 'quality_flag', 'sipm_qc_id', 'timestamp']

    good_sipm_ids = set()
    for sipm_id in all_sipms_ids_for_wafer:
        dfr_tmp = sipm_test[sipm_test['sipm_id'] == sipm_id]

        # Get columns for row with highest sipm_qc_id value.
        try:
            classification, quality_flag, *_ = dfr_tmp[columns].sort_values(
                ['sipm_qc_id', 'timestamp'], ascending=[True, True]
            ).values[-1]
        except IndexError:
            # We will see IndexError for the four SiPMs at the far left/right
            # edges that are not tested.
            pass
        else:
            if classification == 'good' and quality_flag == 0:
                good_sipm_ids.add(sipm_id)

    good_sipm_ids -= unusable_sipm_ids

    return wafer_map_sets(dbi, dfr, good_sipm_ids, no_b_grade, qcid, sipm_test)


async def fetch(url, session, sipm_id):
    """
    Fetch database response for a single SiPM URL.

    Given that the database is unhappy with many concurrent connections, we
    need to ensure that we catch connection errors here and retry as
    appropriate.

    --------------------------------------------------------------------------
    args
        url : string
        session : class aiohttp.client.ClientSession
        sipm_id : int
    --------------------------------------------------------------------------
    returns : dict with single key/value pair
        {int: string}
    --------------------------------------------------------------------------
    """
    data = None
    while data is None:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.text()
        except aiohttp.ClientError:
            await asyncio.sleep(1 + random.random() * 4)

    return {sipm_id: data}


async def fetch_all(dbi, urls):
    """
    Fetch database responses for all SiPM URLs.

    The database cannot cope with the default upper limit of 100 concurrent
    connections, so limit this to something it can handle. Note that the
    limit set here needs to take into consideration others connecting to the
    database. Too many concurrent connections causes the database to generate
    500 Internal Server Error.

    Could also use the following in this context:

    connector = aiohttp.TCPConnector(limit_per_host=16)

    --------------------------------------------------------------------------
    args
        dbi : ds20kdb.interface.Database
            Instance of the Database interface class; allows communication
            with the database.
        urls : dict
            {int: string, ...} e.g. {sipm_id: url, ...}
    --------------------------------------------------------------------------
    returns : list of dict
        [{int: string}, ...]
        e.g. [
            {307200: 'id,timestamp, ... ,77,good,0,,1.831e-11\n'}, ...
        ]
    --------------------------------------------------------------------------
    """
    connector = aiohttp.TCPConnector(limit=16)
    username, password = dbi.session.auth

    async with aiohttp.ClientSession(
        auth=aiohttp.BasicAuth(username, password=password),
        connector=connector
    ) as session:
        tasks = (fetch(url, session, sipm_id) for sipm_id, url in urls.items())
        return await asyncio.gather(*tasks)


def csv_to_dataframe(response):
    """
    Convert database response text string to a Pandas DataFrame.

    --------------------------------------------------------------------------
    args
        response : string
            'id,timestamp,institute_id, ... ,77,good,0,,1.501e-11'
    --------------------------------------------------------------------------
    returns : pandas.DataFrame
    --------------------------------------------------------------------------
    """
    return pd.read_csv(
        io.StringIO(response), sep=',', encoding='utf-8', low_memory=False,
    )


def sipm_status_full_check_async(dbi, dfr, unusable_sipm_ids, no_b_grade, qcid):
    """
    For the given wafer, obtain two sets of wafer (column, row) pairs, for
    good/bad SiPMs respectively.

    Uses sipm_test.classification, sipm_test.quality_flag and
    sipm_test.sipm_qc_id for the evaluation.

    --------------------------------------------------------------------------
    args
        dbi : ds20kdb.interface.Database
            Instance of the Database interface class; allows communication
            with the database.
        dfr : Pandas DataFrame
        unusable_sipm_ids : set of int
        no_b_grade : bool
        qcid : int
    --------------------------------------------------------------------------
    returns (set of tuple, set of tuple, set of tuple) or None
        where each tuple is a pair of column, row values
    --------------------------------------------------------------------------
    """
    # this will give us 268 SiPM IDs, not 264
    all_sipms_ids_for_wafer = set(dfr.sipm_pid.values)

    urls = {
        sipm_id: dbi.get_url('sipm_test', sipm_id=sipm_id)
        for sipm_id in all_sipms_ids_for_wafer
    }

    # Fetch the good/bad status for this wafer's SiPMs in parallel.
    # functools.reduce combines the all the individual dicts (one for each
    # SiPM) to form a single dict.
    mapping = functools.reduce(operator.ior, asyncio.run(fetch_all(dbi, urls)), {})

    columns = ['classification', 'quality_flag', 'sipm_qc_id', 'timestamp']
    good_sipm_ids = set()
    for sipm_id, csv_str in mapping.items():
        dfr_all_qc = csv_to_dataframe(csv_str)
        if qcid is not None:
            dfr_tmp = dfr_all_qc.loc[dfr_all_qc['sipm_qc_id'] == qcid]
        else:
            dfr_tmp = dfr_all_qc

        # Get columns for row with highest sipm_qc_id value.
        try:
            classification, quality_flag, *_ = dfr_tmp[columns].sort_values(
                ['sipm_qc_id', 'timestamp'], ascending=[True, True]
            ).values[-1]
        except IndexError:
            # We will see IndexError for the four SiPMs at the far left/right
            # edges that are not tested.
            pass
        except KeyError:
            print(f'ERROR: broken response for sipm_id {sipm_id}')
            return None
        else:
            if classification == 'good' and quality_flag == 0:
                good_sipm_ids.add(sipm_id)

    good_sipm_ids -= unusable_sipm_ids

    return wafer_map_sets(dbi, dfr, good_sipm_ids, no_b_grade, qcid)


##############################################################################
# Code courtesy of Seraphim Koulosousas
##############################################################################


class SiPMCheck:
    """
    Class of functions to check a sipm test values against the NOA test
    distributions.
    """
    def __init__(self, dbi, qcid=None, sipm_test=None):
        """
        loading the database separately to allow the following functions to be
        able to loop over multiple sipms. If more tables are needed can
        thread the loading and save in a list
        """
        self.dbi = dbi

        # no need to load the table if we already have it in memory
        if sipm_test is None:
            response = self.dbi.get('sipm_test')
            if response.network_timeout:
                raise TimeoutError
            if response.data is None:
                raise LookupError
            self.df_sipm_qc = response.data
        else:
            self.df_sipm_qc = sipm_test

        if qcid is None:
            # Get Latest QA/QC criteria
            self.current_sipm_qc = self.df_sipm_qc['sipm_qc_id'].max()
        else:
            self.current_sipm_qc = qcid

        # Get NOA test results for sipms passing the latest quality qc cuts
        self.df_sipm_good = self.df_sipm_qc.loc[
            (self.df_sipm_qc['quality_flag'] == 0)
            & (self.df_sipm_qc['sipm_qc_id'] == self.current_sipm_qc)
        ]

    @staticmethod
    def cdf(counts, bins, pct):
        """
        Simple function to make a CDF of the NOA Distributions. They generally
        don't seem to follow any standard analytical function, so this is a
        bit of a workaround.

        This function looks for the x value intersect where the
        sum == 1 - pct. (i.e P(X<x) == 1-pct).

        ----------------------------------------------------------------------
        args
            counts : numpy.ndarray
            bins : numpy.ndarray
            pct : float
        ----------------------------------------------------------------------
        returns list or None
        ----------------------------------------------------------------------
        """
        try:
            binsize = bins[1] - bins[0]
        except IndexError:
            return None

        acc = 0
        for index, _bin in enumerate(bins):
            if acc > pct:
                return bins[index]

            acc += counts[index] * binsize

        return None

    def stat(self, required_test, sipm_id):
        """
        Function that checks the sipm id against the NOA Test results.

        ----------------------------------------------------------------------
        args
            sipm_id : int
                the id of the sipm you are checking against Noa's database
            required_test : tuple (string, float)
                e.g. ('i_at_35v', 0.01)
                    statistic : string
                            -> chi2_shape
                            -> i_at_20v
                            -> rq
                            -> i_at_35v
                    proportion_cut : float
                        proportion of the distribution to be cut
                        (i.e 0.01 == 1%)
        ----------------------------------------------------------------------
        returns : bool or None
        ----------------------------------------------------------------------
        """
        statistic, proportion_cut = required_test

        # Get SiPM Data
        sipm_data = self.df_sipm_qc.loc[self.df_sipm_qc['sipm_id'] == sipm_id]

        # Convert dataframe to numpy array
        statistic_array = self.df_sipm_good[statistic].to_numpy()
        counts, bins = np.histogram(statistic_array, bins=200, density=True)

        # default: 100 - 1%
        pct = 1 - proportion_cut

        # get the xValue that corresponds to the specified Proportion Cut
        xval = self.cdf(counts, bins, pct)

        try:
            sipm_stat_value = sipm_data[statistic].values[0]
        except IndexError:
            print(f'[ERROR]: no data for sipm id: {sipm_id}')
            return None

        # True: SiPM good
        try:
            return sipm_stat_value < xval
        except TypeError:
            return None

    def production_standard(self, sipm_id):
        """
        Run all the required assessments on the SiPM. The statistic specified
        in the 'tests' variable is the desired field from table 'sipm_test'.

        dbi.describe('sipm_test').data
        [
            'id', 'timestamp', 'institute_id', 'operator', 'sipm_id',
            'vbd', 'rq', 'i_at_20v', 'i_at_35v', 'iv_rev', 'iv_fwd',
            'chi2_shape', 'sipm_qc_id', 'group', 'temperature',
            'classification', 'quality_flag', 'comment', 'i_at_25v'
        ]

        ----------------------------------------------------------------------
        args
            sipm_id : int
                the id of the sipm you are checking against Noa's database
        ----------------------------------------------------------------------
        returns : bool
        ----------------------------------------------------------------------
        """
        # [(statistic_test, cut_ratio), ...]
        # cut_ratio: proportion of the distribution to be cut (i.e 0.01 == 1%)
        tests = [
            ('chi2_shape', 0.01),
            ('i_at_20v', 0.01),
            # quenching resistance
            ('rq', 0.01),
            ('i_at_35v', 0.01),
        ]
        stat_test = functools.partial(self.stat, sipm_id=sipm_id)

        return all(map(stat_test, tests))


##############################################################################
# python 3.6 compatibility
##############################################################################


def grouper(iterable, n, fillvalue=None):
    """
    Collect data into fixed-length chunks or blocks

    grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"

    Ref:
    https://docs.python.org/3.6/library/itertools.html#itertools-recipes

    Python 3.11 has a recipe for batched():
    https://docs.python.org/3.11/library/itertools.html#itertools-recipes

    Python 3.12 has batched() in the standard library which is similar:
    https://docs.python.org/3.12/library/itertools.html#itertools.batched
    """
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


##############################################################################
# tray file i/o
##############################################################################


def tray_file_lines(filename):
    """
    Yield fields extracted from individual tray file lines.

    Fields are delimited by spaces and/or commas:

    'a,b,c'     -> ['a', 'b', 'c']
    'a b,c'     -> ['a', 'b', 'c']
    'a b, ,,,c' -> ['a', 'b', 'c']

    --------------------------------------------------------------------------
    args
        filename : string
    --------------------------------------------------------------------------
    yields : int, list
    --------------------------------------------------------------------------
    """
    with open(filename, 'r', encoding='utf-8') as infile:
        for line_number, line in enumerate(infile, start=1):
            no_comment = line.split('#')[0].strip()
            fields = [
                field.strip() for field in re.split(r'[, ]+', no_comment)
                if field.strip()
            ]

            # Only yield if there's something to process.
            # The tray number is for internal site usage only, it won't be
            # added to the database so ignore it.
            if fields and not fields[0].startswith('tray'):
                yield line_number, no_comment, fields


def lot_wafer(line):
    """
    Extract lot or wafer number value from text line.

    --------------------------------------------------------------------------
    args
        line : string
            e.g. 'lot, 9333249' or 'wafer_number 02'
    --------------------------------------------------------------------------
    returns : int or None
    --------------------------------------------------------------------------
    """
    parameter = None

    try:
        _, value = line
    except ValueError:
        return parameter

    with contextlib.suppress(ValueError):
        parameter = int(value)

    return parameter


def process_sipm_definition(data, sipms_from_default_wafer, fail, fields):
    """
    --------------------------------------------------------------------------
    args
        data : dict
        sipms_from_default_wafer : set
        fail : bool
        fields : list
    --------------------------------------------------------------------------
    returns : bool
    --------------------------------------------------------------------------
    """
    # long form: 5 values
    # short form: 3 values
    # named SiPM but no information, 1 or 2 values
    try:
        key, column, row, lot_num, wafer_num = fields
    except ValueError:
        try:
            key, column, row = fields
        except ValueError:
            # This is likely to be a line starting with sipm_xx and no
            # following information (an unfilled template line), so just
            # allow this case to be silently ignored.
            if len(fields) != 1:
                fail = True
        else:
            # short form
            # sipm_number, wafer_column, wafer_row
            sipm = sipm_key(key)
            if sipm is not None:
                with contextlib.suppress(ValueError):
                    sipms_from_default_wafer.add(sipm)
                    data[sipm] = SiPM(column, row)
            else:
                # SiPM number is probably out of range
                fail = True
    else:
        # long form
        # sipm_number, wafer_column, wafer_row, wlot, wnum

        sipm = sipm_key(key)

        if sipm is not None:
            with contextlib.suppress(ValueError):
                data[sipm] = SiPM(column, row, lot_num, wafer_num)
        else:
            # SiPM number is probably out of range
            fail = True

    return fail


def sipm_key(key):
    """
    Check if a string represents a SiPM.

    --------------------------------------------------------------------------
    args
        key : string
            e.g. 'sipm_1' or 'sipm_23'
    --------------------------------------------------------------------------
    returns : int or None
        int if the SiPM information appears valid, None otherwise
    --------------------------------------------------------------------------
    """
    try:
        sipm_text, number = key.split('_')
    except ValueError:
        sipm_text = number = None
    else:
        number = int(number)

    return number if sipm_text == 'sipm' and 1 <= number <= 24 else None


def read_tray_file(filename):
    """
    Import data recorded during the wafer picking stage, where a file
    represents the contents of a SiPM tray (24 SiPMS).

    The contents of the file should look something like this:

    tray, 1
    lot, 9262109
    wafer_number, 15
    # sipm_number, wafer_column, wafer_row
    sipm_1, 07, 23
    sipm_2, 08, 23
    sipm_3, 09, 23
    sipm_4, 10, 23
    sipm_5, 11, 23
    sipm_6, 12, 23
    sipm_7, 06, 22
    sipm_8, 07, 22
    sipm_9, 08, 22
    sipm_10, 09, 22
    sipm_11, 10, 22
    sipm_12, 11, 22
    sipm_13, 12, 22
    sipm_14, 13, 22
    sipm_15, 06, 21
    sipm_16, 07, 21
    sipm_17, 08, 21
    sipm_18, 09, 21
    sipm_19, 10, 21
    sipm_20, 11, 21
    sipm_21, 12, 21
    sipm_22, 13, 21
    sipm_23, 14, 21
    sipm_24, 04, 20

    For the SiPM lines, there are some variants for tray locations:

    (1) empty (n=1):

    sipm_number,
    sipm_number

    (2) has come from another wafer (n=5):

    sipm_number, wafer_column, wafer_row, wafer_lot, wafer_number

    At some stage, we should also allow SiPM PIDs to be used (n=2):

    sipm_number, sipm_pid

    --------------------------------------------------------------------------
    args
        widgets : list
            Contains details of GUI widgets.
    --------------------------------------------------------------------------
    returns : dict or None
    --------------------------------------------------------------------------
    """
    data = {}
    lot_number = wafer_number = None
    sipms_from_default_wafer = set()

    for _line_number, _no_comment, fields in tray_file_lines(filename):
        fail = False

        if fields[0].startswith('lot'):
            lot_number = lot_wafer(fields)
            if lot_number is None:
                fail = True

        elif fields[0].startswith('wafer_number'):
            wafer_number = lot_wafer(fields)
            if wafer_number is None:
                fail = True

        elif fields[0].startswith('sipm_'):
            fail = process_sipm_definition(
                data, sipms_from_default_wafer, fail, fields
            )

        else:
            # issue a warning for any non-matching line
            fail = True

    # lot_number and/or wafer_number can be None as long as there are no
    # short-form (column/row only) entries that require that pair of values.
    if sipms_from_default_wafer and (lot_number is None or wafer_number is None):
        return None

    # For SiPMs that didn't have a wafer lot and wafer number specified, fill
    # in the default values. We can't guarantee that the wafer and lot number
    # will precede SiPM definitions, so this can't be done earlier.
    for number in sipms_from_default_wafer:
        data[number].lot_number = lot_number
        data[number].wafer_number = wafer_number

    return data


def missing_sipm_entries(tray):
    """
    Generate a set of missing SiPM entries.

    --------------------------------------------------------------------------
    args
        tray : dict of class SiPM
            {
                1: SiPM(lot_number=9323939, wafer_number=1, column=9, row=5),
                ...
                24: SiPM(lot_number=9323939, wafer_number=1, column=9, row=2),
            }
    --------------------------------------------------------------------------
    returns : set of SiPM numbers of missing entries in the tray file
        e.g. {1, 14, 15, 24}
    --------------------------------------------------------------------------
    """
    return set(range(1, 25)) - set(tray.keys())


def evaluate_tray_files(files):
    """
    --------------------------------------------------------------------------
    args
        files : set
    --------------------------------------------------------------------------
    returns
        tray_details : dict
            {filename: (details of tray file contents, missing entries), ...}
            e.g. {
                'green.txt': (
                    {
                        'sipm_1|column': 15,
                        'sipm_1|row': 6,
                        'sipm_1|lot_number': 9323939,
                        'sipm_1|wafer_number': 2,
                        ...
                        'sipm_24|column': 7,
                        'sipm_24|row': 3,
                        'sipm_24|lot_number': 9323939,
                        'sipm_24|wafer_number': 2
                    },
                    {10, 6},
                    )
                }
    --------------------------------------------------------------------------
    """
    tray_details = {}

    for tray_file in files:
        contents = read_tray_file(tray_file)
        missing = missing_sipm_entries(contents)

        tray_details[tray_file] = (contents, missing)

    return tray_details


def fill_file(filename, missing_sipms, sipm_allocation, lot, wafer_number, write):
    """
    Go through the file and place the new sipms in the empty slots.

    We will not create a new file from the data already held in memory, since
    this will remove any comments/formatting that the user may have made.
    Since the files are tiny, read it into memory, modify just the lines that
    need to change, and overwrite the file.

    Existing SiPM entries may be present, or missing altogether.

    If the file contains any broken lines they will be propagated into the
    new file.

    Try to make minimal changes to the file, to avoid creating confusing
    commit diffs.

    --------------------------------------------------------------------------
    args
        filename : str
        missing_sipms : set
        sipm_allocation : set
        lot : int
        wafer_number : int
        write : bool
    --------------------------------------------------------------------------
    returns
        missing_sipms : set
            no explicit return, mutable type amended in place
        external file amended
    --------------------------------------------------------------------------
    """
    lines = [f'\n{"-" * 58}\n{filename}\n{"-" * 58}']

    with open(filename, 'r', encoding='utf-8') as file:
        data = file.readlines()

    # replace existing empty SiPM entries
    for index, line in enumerate(data.copy()):
        for missing_sipm in missing_sipms.copy():
            if re.search(r'^\s*sipm_0*' + f'{missing_sipm}', line):
                try:
                    col, row = sipm_allocation.pop(0)
                except IndexError:
                    break

                new_line = (
                    f'sipm_{missing_sipm:02}, {col:>2}, {row:>2}, '
                    f'{lot:>2}, {wafer_number:>2}\n'
                )
                data[index] = new_line
                lines.append(
                    f'{"replaced blank entry with":>25}: {new_line.strip()}'
                )
                missing_sipms.remove(missing_sipm)
                break

    # add in SiPM definitions if the was no definition in the file
    # append rather than attempt to insert in the right place or sort the
    # entries in case the user has added comments above the SiPM entry
    for missing_sipm in sorted(missing_sipms.copy()):
        try:
            col, row = sipm_allocation.pop(0)
        except IndexError:
            break

        new_line = (
            f'sipm_{missing_sipm:02}, {col:>2}, {row:>2}, '
            f'{lot:>2}, {wafer_number:>2}\n'
        )
        data.append(new_line)
        lines.append(
            f'{"appended":>25}: {new_line.strip()}'
        )
        missing_sipms.remove(missing_sipm)

    if write:
        with open(filename, 'w', encoding='utf-8') as file:
            file.writelines(data)

    return lines


def fill_files(var, lot, wafer_number, write=True):
    """
    --------------------------------------------------------------------------
    args
        var : tuple (dict, list)
            e.g. (existing_tray_files, new_sipms)
                {
                    'yellow2.txt': (
                        {
                            'sipm_01|column': 6,
                            'sipm_01|row': 4,
                            'sipm_1|lot_number': 9323959,
                            'sipm_1|wafer_number': 2,
                            ...
                        },
                        {6, 7, 8, 9, 10, 11, 12, ...},
                    ),
                    'yellow.txt': (
                        {
                            'sipm_1|column': 9,
                            'sipm_1|row': 5,
                            'sipm_1|lot_number': 9323939,
                            'sipm_1|wafer_number': 1,
                            ...
                        },
                        {18, 22},
                    )
                }
        lot : int
        wafer_number : int
    --------------------------------------------------------------------------
    returns : none
        external file amended
    --------------------------------------------------------------------------
    """
    _sipm_type, existing_tray_files, new_sipms = var

    lines_for_all_files = []
    for filename, (_contents, missing_sipms) in existing_tray_files.items():

        sipm_allocation = []
        for _ in itertools.repeat(None, len(missing_sipms)):
            try:
                sipm = new_sipms.pop(0)
            except (IndexError, KeyError):
                break
            else:
                sipm_allocation.append(sipm)

        lines_for_all_files += fill_file(
            filename, missing_sipms, sipm_allocation, lot, wafer_number, write
        )

    return lines_for_all_files


def write_tray_file(lot, wafer_number, detailed, filename, write):
    """
    Write tray file to filestore, if writes are enabled.

    e.g.

    lot, 9323959
    wafer_number, 4
    # sipm_num, wafer_col, wafer_row [, lot, wafer_num]
    sipm_01, 12,  4
    sipm_02,  7, 17
    ...
    sipm_23,  6, 20
    sipm_24,  7, 19

    --------------------------------------------------------------------------
    args
        lot :
        wafer_number :
        detailed :
        filename : string
        write : bool
    --------------------------------------------------------------------------
    returns : list
    --------------------------------------------------------------------------
    """
    header = []
    header += [
        f'\n{"-" * 58}\n'
        f'{filename}\n'
        f'{"-" * 58}\n'
    ]

    lines = [
        f'sipm_{i:02}, {x[0]:2}, {x[1]:2}\n'
        for i, x in enumerate(detailed, start=1)
    ]
    lines.insert(0, '# sipm_num, wafer_col, wafer_row [, lot, wafer_num]\n')
    lines.insert(0, f'wafer_number, {wafer_number}\n')
    lines.insert(0, f'lot, {lot}\n')

    if write:
        with open(filename, 'w', encoding='utf-8') as file:
            file.writelines(lines)

    return header + lines


def tray_filename(sipm_type, lot, wafer_number, offset, tray_number):
    """
    Create a properly formatted filename for green/yellow SiPM tray files,
    e.g.

    green:  9323959_04_green_tray_04.txt
    yellow: yellow_0002.txt

    Green files are created in a directory specifically related to their
    wafer. So it makes sense to name them accordingly.

    Yellow files detail the contents of SiPM trays containing devices that
    were regarded as production standard, but failed visual inspection. These
    SiPMs may be used later for production, but the trays they are housed in
    may contain a devices from many different wafers, hence the generic
    filename.

    --------------------------------------------------------------------------
    args
        sipm_type : string
        lot : int
        wafer_number : int
        offset : int
        tray_number : int
    --------------------------------------------------------------------------
    returns : list
    --------------------------------------------------------------------------
    """
    if sipm_type == 'green':
        return (
            f'{lot}_{wafer_number:02}_'
            f'{sipm_type.lower()}_tray_{tray_number:02}.txt'
        )

    return f'yellow_{offset + tray_number:04}.txt'


def create_tray_files(var, lot, wafer_number, write):
    """
    Create tray files for green or yellow SiPMs.

    --------------------------------------------------------------------------
    args
        var : tuple (dict, list)
            e.g. (sipm_type, available_sipms)
                sipm_type : string, e.g. 'green' or 'yellow'
                available_sipms : list of tuple (column, row)
                    e.g. [(7, 2), ...]
        lot : int
        wafer_number : int
        write : book
    --------------------------------------------------------------------------
    returns : none
        external file amended
    --------------------------------------------------------------------------
    """
    sipm_type, available_sipms, directory, offset = var

    lines_for_all_files = []

    for i, x in enumerate(grouper(available_sipms, 24), start=1):
        detailed = [(t[0], t[1], lot, wafer_number) for t in x if t]
        filename = tray_filename(sipm_type, lot, wafer_number, offset, i)

        lines_for_all_files += write_tray_file(
            lot,
            wafer_number,
            detailed,
            os.path.join(directory, filename),
            write,
        )

    return lines_for_all_files


def box_message(message, text_width):
    """
    Print message in a box, fitted to the console size, e.g.

    +--------------------------------------------------------+
    | ALLIANCE, n.  In international politics, the union of  |
    | two thieves who have their hands so deeply inserted in |
    | each other's pockets that they cannot separately       |
    | plunder a third.                                       |
    +--------------------------------------------------------+

    Quote from The Devil's Dictionary, Ambrose Bierce
    https://www.gutenberg.org/cache/epub/972/pg972.txt

    ----------------------------------------------------------------------
    args
        message : string
    ----------------------------------------------------------------------
    returns : string
    ----------------------------------------------------------------------
    """
    top_bottom_line_len = text_width - 2
    width = text_width - 4

    header = footer = f'+{"-" * top_bottom_line_len}+'
    filling = [
        f'| {line:<{width}} |'
        for line in textwrap.wrap(message, width)
    ]

    return '\n'.join([header, *filling, footer]) + '\n\n'
