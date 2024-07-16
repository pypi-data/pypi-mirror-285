


# Copyright 2019 Gehtsoft USA LLC
# Copyright 2023 JGWill (extended/variations)

# Licensed under the license derived from the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at

# http://fxcodebase.com/licenses/open-source/license.html

# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List
from enum import Enum
import json
import os
import tlid

#------------------------#

# common.py


#import logging
import datetime
import traceback
import argparse
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtos import tlid_range_to_start_end_datetime,tlid_range_to_jgtfxcon_start_end_str,tlid_dt_to_string,tlidmin_to_dt

from jgtutils.jgtcliconstants import (_ARG_GROUP_BARS_DESCRIPTION, _ARG_GROUP_BARS_TITLE, _ARG_GROUP_CLEANUP_DESCRIPTION, _ARG_GROUP_CLEANUP_TITLE, _ARG_GROUP_INDICATOR_DESCRIPTION, _ARG_GROUP_INDICATOR_TITLE, _ARG_GROUP_INTERACTION_DESCRIPTION, _ARG_GROUP_INTERACTION_TITLE, _ARG_GROUP_OUTPUT_DESCRIPTION, _ARG_GROUP_OUTPUT_TITLE, _ARG_GROUP_POV_DESCRIPTION, _ARG_GROUP_POV_TITLE, _ARG_GROUP_RANGE_DESCRIPTION, _ARG_GROUP_RANGE_TITLE, _ARG_GROUP_VERBOSITY_DESCRIPTION, _ARG_GROUP_VERBOSITY_TITLE, FRESH_FLAG_ARGNAME,
                      FRESH_FLAG_ARGNAME_ALIAS,
                      NOT_FRESH_FLAG_ARGNAME_ALIAS,
                      NOT_FRESH_FLAG_ARGNAME,
                      BALLIGATOR_FLAG_ARGNAME,
                      BALLIGATOR_FLAG_ARGNAME_ALIAS, QUOTES_COUNT_ARGNAME, QUOTES_COUNT_ARGNAME_ALIAS,
                      TALLIGATOR_FLAG_ARGNAME,
                      TALLIGATOR_FLAG_ARGNAME_ALIAS,
                      MFI_FLAG_ARGNAME,
                      MFI_FLAG_ARGNAME_ALIAS,
                      NO_MFI_FLAG_ARGNAME,
                      NO_MFI_FLAG_ARGNAME_ALIAS,
                      GATOR_OSCILLATOR_FLAG_ARGNAME,
                      GATOR_OSCILLATOR_FLAG_ARGNAME_ALIAS,
                      KEEP_BID_ASK_FLAG_ARGNAME,
                      KEEP_BID_ASK_FLAG_ARGNAME_ALIAS,
                      REMOVE_BID_ASK_FLAG_ARGNAME,
                      REMOVE_BID_ASK_FLAG_ARGNAME_ALIAS,
                      FULL_FLAG_ARGNAME,
                      FULL_FLAG_ARGNAME_ALIAS,
                      NOT_FULL_FLAG_ARGNAME,
                      NOT_FULL_FLAG_ARGNAME_ALIAS,
                      DROPNA_VOLUME_FLAG_ARGNAME,
                      DROPNA_VOLUME_FLAG_ARGNAME_ALIAS,
                      DONT_DROPNA_VOLUME_FLAG_ARGNAME,
                      DONT_DROPNA_VOLUME_FLAG_ARGNAME_ALIAS
                      )


args:argparse.Namespace=None # Default args when we are done parsing
try :
    import __main__
    # logging.basicConfig(filename='{0}.log'.format(__main__.__file__), level=logging.INFO,
    #                 format='%(asctime)s %(levelname)s %(message)s', datefmt='%m.%d.%Y %H:%M:%S')
    # console = logging.StreamHandler(sys.stdout)
    # console.setLevel(logging.INFO)
    # logging.getLogger('').addHandler(console)
    

except:
    #print('logging failed - dont worry')
    pass

try :    
    #if __main__ has a .parser then set the default parser to that
    if hasattr(__main__,'parser'):
        default_parser=__main__.parser
    else:
        if hasattr(__main__,'default_parser'):
            default_parser=__main__.default_parser
        else: 
            if hasattr(__main__,'__parser__'):
                default_parser=__main__.__parser__
            else:
                default_parser = argparse.ArgumentParser(description='JGWill Trading Utilities')
except:
    default_parser = argparse.ArgumentParser(description='JGWill Trading Utilities')
    pass

# try:
#     #indicator's group
#     indicator_group = default_parser.add_argument_group(INDICATOR_GROUP_TITLE, 'Indicators to use in the processing.')
#     #indicator_group = _get_group_by_title(default_parser, INDICATOR_GROUP_TITLE)
# except:
#     pass


def new_parser(description: str,epilog: str=None,prog: str=None)->argparse.ArgumentParser:
    global default_parser
    default_parser = argparse.ArgumentParser(description=description,epilog=epilog,prog=prog)
    return default_parser

# Get a group by its title
def _get_group_by_title(parser, title,description=""):
    for group in parser._action_groups:
        if group.title == title:
            return group
    #create it
    return parser.add_argument_group(title, description)


def init_default_parser(description: str):
    global default_parser
    default_parser = argparse.ArgumentParser(description=description)
    return default_parser




def _add_a_flag_helper(_description:str,  _argname_alias:str, _argname_full:str, parser: argparse.ArgumentParser,_action_value="store_true",group_title="",group_description=""):


    __alias_cmd_prefix = "-"
    __full_arg_prefix = "--"
    
    _argname_alias = __alias_cmd_prefix+_argname_alias
    _argname_full = __full_arg_prefix+_argname_full
    if group_title=="":
        parser.add_argument(
        _argname_alias,
        _argname_full,
        action=_action_value,
        help=_description,
        )
    else:
        #try get group name or create it.
        group = _get_group_by_title(parser, group_title,group_description)
        group.add_argument(
            _argname_alias,
            _argname_full,
            action=_action_value,
            help=_description,
        )
    
    return parser






def add_main_arguments(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    global default_parser
    if parser is None:
        parser=default_parser
        
    parser.add_argument('--login',
                        metavar="LOGIN",
                        required=True,
                        help='Your user name.')

    parser.add_argument('--password',
                        metavar="PASSWORD",
                        required=True,
                        help='Your password.')

    parser.add_argument('--urlserver',
                        metavar="URL",
                        required=True,
                        help='The server URL. For example,\
                                 https://www.fxcorporate.com/Hosts.jsp.')

    parser.add_argument('--connection',
                        metavar="CONNECTION",
                        required=True,
                        help='The connection name. For example, \
                                 "Demo" or "Real".')


    parser.add_argument('-session',
                        help='The database name. Required only for users who\
                                 have accounts in more than one database.\
                                 Optional parameter.')

    parser.add_argument('-pin',
                        help='Your pin code. Required only for users who have \
                                 a pin. Optional parameter.')
    return parser

def add_candle_open_price_mode_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    global default_parser
    if parser is None:
        parser=default_parser
    parser.add_argument('--openpricemode',
                        metavar="CANDLE_OPEN_PRICE_MODE",
                        default="prev_close",
                        help='Ability to set the open price candles mode. \
                        Possible values are first_tick, prev_close. For more information see description \
                        of O2GCandleOpenPriceMode enumeration. Optional parameter.')
    return parser

def add_instrument_timeframe_arguments(parser: argparse.ArgumentParser=None, timeframe: bool = True,add_IndicatorPattern=False):
    
    global default_parser
    if parser is None:
        parser=default_parser
    pov_group=_get_group_by_title(parser,_ARG_GROUP_POV_TITLE,_ARG_GROUP_POV_DESCRIPTION)
    pov_group.add_argument('-i','--instrument',
                        metavar="INSTRUMENT",
                        help='An instrument which you want to use in sample. \
                                  For example, "EUR/USD".')

    if timeframe:
        pov_group.add_argument('-t','--timeframe',
                            metavar="TIMEFRAME",
                            help='Time period which forms a single candle. \
                                      For example, m1 - for 1 minute, H1 - for 1 hour.')
    if add_IndicatorPattern:
        parser.add_argument('-ip',
                        metavar="IndicatorPattern",
                        required=False,
                        help='The indicator Pattern. For example, \
                                 "AOAC","JTL,"JTLAOAC","JTLAOAC","AOACMFI".')
    return parser
    

def add_direction_buysell_arguments(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    global default_parser
    if parser is None:
        parser=default_parser
    parser.add_argument('-d','--bs', metavar="TYPE", required=True,
                        help='The order direction. Possible values are: B - buy, S - sell.')
    return parser

def add_rate_arguments(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    global default_parser
    if parser is None:
        parser=default_parser
    parser.add_argument('-r','--rate', metavar="RATE", required=True, type=float,
                            help='Desired price of an entry order.')
    return parser


def add_lots_arguments(parser):
    parser.add_argument('-lots', metavar="LOTS", default=1, type=int,
                            help='Trade amount in lots.')

def add_direction_rate_lots_arguments(parser: argparse.ArgumentParser=None, direction: bool = True, rate: bool = True,
                                      lots: bool = True):
    global default_parser
    if parser is None:
        parser=default_parser

    if direction:
        add_direction_buysell_arguments(parser)
    if rate:
        add_rate_arguments(parser)
    if lots:
        add_lots_arguments(parser)
    
    return parser



def add_account_arguments(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    global default_parser
    if parser is None:
        parser=default_parser
    parser.add_argument('-account', metavar="ACCOUNT",
                        help='An account which you want to use in sample.')
    return parser


def str_to_datetime(date_str):
    formats = ['%m.%d.%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d', '%Y-%m-%d']
    
    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def valid_datetime(check_future: bool):
    def _valid_datetime(str_datetime: str):
        date_format = '%m.%d.%Y %H:%M:%S'
        try:
            result = datetime.datetime.strptime(str_datetime, date_format).replace(
                tzinfo=datetime.timezone.utc)
            if check_future and result > datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc):
                msg = "'{0}' is in the future".format(str_datetime)
                raise argparse.ArgumentTypeError(msg)
            return result
        except ValueError:
            now = datetime.datetime.now()
            msg = "The date '{0}' is invalid. The valid data format is '{1}'. Example: '{2}'".format(
                str_datetime, date_format, now.strftime(date_format))
            raise argparse.ArgumentTypeError(msg)
    return _valid_datetime


def add_tlid_date_V2_arguments(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    global default_parser
    if parser is None:
        parser=default_parser
    
    group1 = parser.add_argument_group('Group 1 (TLID Range)')
    g1x=group1.add_mutually_exclusive_group()
    g1x.add_argument('-r', '--range', type=str, required=False, dest='tlidrange',
                        help='TLID range in the format YYMMDDHHMM_YYMMDDHHMM.')
    g2x=g1x.add_mutually_exclusive_group()
    
    raise Exception("Not implemented - Complicated")
    
    #group1.
    #dt_range_group=parser.add_mutually_exclusive_group()
    #dt_range_group.add_argument('-r', '--range', type=str, required=False, dest='tlidrange',
    #                    help='TLID range in the format YYMMDDHHMM_YYMMDDHHMM.')
    # Second group of arguments
    group2 = parser.add_argument_group('Group 2 (Dates)')
    group2.add_argument('-s', '--datefrom', metavar='"m.d.Y H:M:S"',
                        help='Date/time from which you want to receive historical prices.',
                        type=valid_datetime(True),required=False)
    group2.add_argument('-e', '--dateto', metavar='"m.d.Y H:M:S"',
                        help='Datetime until which you want to receive historical prices.',
                        type=valid_datetime(False),required=False)
    
    # Exclusivity between the two groups
    group1_xor_group2 = parser.add_mutually_exclusive_group()
    group1_xor_group2.add_argument('-r', '--range', dest='tlidrange', action='store_true')
    
    group2x=group1_xor_group2.add_mutually_exclusive_group()
    group2x.add_argument('-s', '--datefrom', dest='tlidrange', action='store_false')
    group2x.add_argument('-e', '--dateto', dest='tlidrange', action='store_false')
    
    
    return parser


def add_tlid_range_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    global default_parser
    if parser is None:
        parser=default_parser
    #print("Tlid range active")
    group_range=_get_group_by_title(parser,_ARG_GROUP_RANGE_TITLE,_ARG_GROUP_RANGE_DESCRIPTION)
    group_range.add_argument('-r', '--range', type=str, required=False, dest='tlidrange',
                        help='TLID range in the format YYMMDDHHMM_YYMMDDHHMM.')
    return parser

def add_date_arguments(parser: argparse.ArgumentParser=None, date_from: bool = True, date_to: bool = True):
    global default_parser
    if parser is None:
        parser=default_parser
    
    group_range=_get_group_by_title(parser,_ARG_GROUP_RANGE_TITLE,_ARG_GROUP_RANGE_DESCRIPTION)
    if date_from:
        group_range.add_argument('-s','--datefrom',
                            metavar="\"m.d.Y H:M:S\"",
                            help='Date/time from which you want to receive\
                                      historical prices. If you leave this argument as it \
                                      is, it will mean from last trading day. Format is \
                                      "m.d.Y H:M:S". Optional parameter.',
                            type=valid_datetime(True)
                            )
    if date_to:
        group_range.add_argument('-e','--dateto',
                            metavar="\"m.d.Y H:M:S\"",
                            help='Datetime until which you want to receive \
                                      historical prices. If you leave this argument as it is, \
                                      it will mean to now. Format is "m.d.Y H:M:S". \
                                      Optional parameter.',
                            type=valid_datetime(False)
        )
    return parser


def add_report_date_arguments(parser: argparse.ArgumentParser=None, date_from: bool = True, date_to: bool = True):
    global default_parser
    if parser is None:
        parser=default_parser
    group_range=_get_group_by_title(parser,_ARG_GROUP_RANGE_TITLE,_ARG_GROUP_RANGE_DESCRIPTION)
    if date_from:
        group_range.add_argument('-s','--datefrom',
                            metavar="\"m.d.Y H:M:S\"",
                            help='Datetime from which you want to receive\
                                      combo account statement report. If you leave this argument as it \
                                      is, it will mean from last month. Format is \
                                      "m.d.Y H:M:S". Optional parameter.',
                            type=valid_datetime(True)
                            )
    if date_to:
        group_range.add_argument('-e','--dateto',
                            metavar="\"m.d.Y H:M:S\"",
                            help='Datetime until which you want to receive \
                                      combo account statement report. If you leave this argument as it is, \
                                      it will mean to now. Format is "m.d.Y H:M:S". \
                                      Optional parameter.',
                            type=valid_datetime(True)
        )
    return parser


def add_max_bars_arguments(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    global default_parser
    if parser is None:
        parser=default_parser
    
    group_bars=_get_group_by_title(parser,_ARG_GROUP_BARS_TITLE,_ARG_GROUP_BARS_DESCRIPTION)
    print("DEPRECATION: Use: add_bars_amount_V2_arguments intead of add_max_bars_arguments and add_use_full_argument")
    group_bars.add_argument('-'+QUOTES_COUNT_ARGNAME_ALIAS,'--'+QUOTES_COUNT_ARGNAME,
                        metavar="MAX",
                        default=-1,
                        type=int,
                        help='Max number of bars. 0 - Not limited')
    
    return parser

def add_bars_amount_V2_arguments(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    global default_parser
    if parser is None:
        parser=default_parser
    #help='Specify the number of bars to download or use the full number of bars available from the store.'
    bars_group=_get_group_by_title(parser,_ARG_GROUP_BARS_TITLE,_ARG_GROUP_BARS_DESCRIPTION)
    #g=parser.add_argument_group('Bars Amount', 'Specify the number of bars to download or use the full number of bars available from the store.')
    bars_exclusive_subgroup=bars_group.add_mutually_exclusive_group()
    
    
    bars_exclusive_subgroup.add_argument('-'+QUOTES_COUNT_ARGNAME_ALIAS,'--'+QUOTES_COUNT_ARGNAME,
                        metavar="MAX",
                        default=-1,
                        type=int,
                        help='Max number of bars. 0 - Not limited')
    g_full_notfull=bars_exclusive_subgroup.add_mutually_exclusive_group()
    g_full_notfull.add_argument('-'+FULL_FLAG_ARGNAME_ALIAS,'--'+FULL_FLAG_ARGNAME,
                        action='store_true',
                        help='Output/Input uses the full store. ')
    g_full_notfull.add_argument('-'+NOT_FULL_FLAG_ARGNAME_ALIAS,'--'+NOT_FULL_FLAG_ARGNAME,
                        action='store_true',
                        help='Output/Input uses NOT the full store. ')


def add_output_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    """
    Adds an output argument to the given argument parser.

    Args:
        parser (argparse.ArgumentParser): The argument parser to add the output argument to.

    Returns:
        parser (argparse.ArgumentParser): The argument parser with the output argument added.
    """
    global default_parser
    if parser is None:
        parser=default_parser
        
    parser.add_argument('-o','--output',
                        action='store_true',
                        help='Output PATH. If specified, output will be written in the filestore.')
    
    return parser

def add_compressed_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    """
    Adds an compressed argument to the given argument parser.
    
    Args:
        parser (argparse.ArgumentParser): The argument parser to add the output argument to.
        
    Returns:
        parser (argparse.ArgumentParser): The argument parser with argument added.
    """
    global default_parser
    if parser is None:
        parser=default_parser
    group_output=_get_group_by_title(parser,_ARG_GROUP_OUTPUT_TITLE,_ARG_GROUP_OUTPUT_DESCRIPTION)
    group_output.add_argument('-z','--compress',
                        action='store_true',
                        help='Compress the output. If specified, it will also activate the output flag.')
    return parser


def add_use_full_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    """
    Adds a use full argument to the given argument parser.
    
    Args:
        parser (argparse.ArgumentParser): The argument parser to add the read full argument to.
        
    Returns:
        parser (argparse.ArgumentParser): The argument parser with argument added.
    """
    global default_parser
    if parser is None:
        parser=default_parser
    
    #print("DEPRECATION: Use: add_bars_amount_V2_arguments")
    full_notfull_group = parser.add_mutually_exclusive_group()
    full_notfull_group.add_argument('-'+FULL_FLAG_ARGNAME_ALIAS,'--'+FULL_FLAG_ARGNAME,
                        action='store_true',
                        help='Output/Input uses the full store. ')
    full_notfull_group.add_argument('-'+NOT_FULL_FLAG_ARGNAME_ALIAS,'--'+NOT_FULL_FLAG_ARGNAME,
                        action='store_true',
                        help='Output/Input uses NOT the full store. ')
 
    return parser

def add_use_fresh_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    """
    Adds a use fresh argument to the given argument parser.
    
    Args:
        parser (argparse.ArgumentParser): The argument parser to add the use fresh argument to.
        
    Returns:
        parser (argparse.ArgumentParser): The argument parser with argument added.
    """
    global default_parser
    if parser is None:
        parser=default_parser
    bars_group=_get_group_by_title(parser,_ARG_GROUP_BARS_TITLE,_ARG_GROUP_BARS_DESCRIPTION)
    
    fresh_old_group=bars_group.add_mutually_exclusive_group()
    fresh_old_group.add_argument('-'+FRESH_FLAG_ARGNAME_ALIAS,'--'+FRESH_FLAG_ARGNAME,
                        action='store_true',
                        help='Freshening the storage with latest market. ')
    fresh_old_group.add_argument('-'+NOT_FRESH_FLAG_ARGNAME_ALIAS,'--'+NOT_FRESH_FLAG_ARGNAME,
                        action='store_true',
                        help='Output/Input wont be freshed from storage (weekend or tests). ')
 
    return parser


def add_keepbidask_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    """
    Adds a keep Bid/Ask argument to the given argument parser.
    
    Args:
        parser (argparse.ArgumentParser): The argument parser to add the keep bid/ask argument to.
        
    Returns:
        parser (argparse.ArgumentParser): The argument parser with the argument added.
    """
    global default_parser
    if parser is None:
        parser=default_parser
    
    cleanupGroup=_get_group_by_title(parser,_ARG_GROUP_CLEANUP_TITLE,_ARG_GROUP_CLEANUP_DESCRIPTION)
    group_kba=cleanupGroup.add_mutually_exclusive_group()
    
    group_kba.add_argument('-'+KEEP_BID_ASK_FLAG_ARGNAME_ALIAS,'--'+KEEP_BID_ASK_FLAG_ARGNAME,
                        action='store_true',
                        help='Keep Bid/Ask in storage. ')
    group_kba.add_argument('-'+REMOVE_BID_ASK_FLAG_ARGNAME_ALIAS,'--'+REMOVE_BID_ASK_FLAG_ARGNAME,
                        action='store_true',
                        help='Remove Bid/Ask in storage. ')
    return parser

import jgtclirqdata
def add_jgtclirqdata_arguments(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    global default_parser
    if parser is None:
        parser=default_parser
    group_pattern=parser.add_argument_group('RQ Pattern', 'RQ Pattern to use.  Future practice to create request patterns to load into the args later.')
    
    group_pattern.add_argument('-pdsrq','--pds_rq_base',
                        action='store_true',
                        help='Use PDS_RQ JSON_BASE')
    #PDS_RQ JSON_NORMAL
    group_pattern.add_argument('-pdsrqn','--pds_rq_normal',
                        action='store_true',
                        help='Use PDS_RQ JSON_NORMAL')
    #PDS_RQ JSON_NORMAL_FRESH
    group_pattern.add_argument('-pdsrqnf','--pds_rq_normal_fresh',
                        action='store_true',
                        help='Use PDS_RQ JSON_NORMAL_FRESH')
    #PDS_RQ JSON_FULL
    group_pattern.add_argument('-pdsrqf','--pds_rq_full',
                        action='store_true',
                        help='Use PDS_RQ JSON_FULL')
    #PDS_RQ JSON_FULL_FRESH
    group_pattern.add_argument('-pdsrqff','--pds_rq_full_fresh',
                        action='store_true',
                        help='Use PDS_RQ JSON_FULL_FRESH')
    #IDS_RQ JSON_BASE
    group_pattern.add_argument('-idsrq','--ids_rq_base',
                        action='store_true',
                        help='Use IDS_RQ JSON_BASE')
    
    group_pattern.add_argument('-cdsrq','--cds_rq_normal',
                        action='store_true',
                        help='Use CDS_RQ JSON_NORMAL')
    
    group_pattern.add_argument('-cdsrqf','--cds_rq_full',
                        action='store_true',
                        help='Use CDS_RQ JSON_FULL')
    #CDS_RQ JSON_FULL_FRESH
    group_pattern.add_argument('-cdsrqff','--cds_rq_full_fresh',
                        action='store_true',
                        help='Use CDS_RQ JSON_FULL_FRESH')
    #CDS_RQ JSON_NORM_FRESH
    group_pattern.add_argument('-cdsrqnf','--cds_rq_norm_fresh',
                        action='store_true',
                        help='Use CDS_RQ JSON_NORM_FRESH')
    
    return parser

#post add_jgtclirqdata_arguments
def __jgtclirqdata_post_parse():
    global args
    __check_if_parsed()
    _jgtclirqdata_to_load=[jgtclirqdata.PDS_RQ_BASE]
    try:
        if hasattr(args, 'pds_rq_base') and args.pds_rq_base:
            _jgtclirqdata_to_load.append(jgtclirqdata.PDS_RQ_BASE)
        if hasattr(args, 'ids_rq_base') and args.ids_rq_base:
            _jgtclirqdata_to_load.append(jgtclirqdata.IDS_RQ_BASE)
        if hasattr(args, 'cds_rq_normal') and args.cds_rq_normal:
            _jgtclirqdata_to_load.append(jgtclirqdata.CDS_RQ_NORMAL)
        if hasattr(args, 'cds_rq_full') and args.cds_rq_full:
            _jgtclirqdata_to_load.append(jgtclirqdata.CDS_RQ_FULL)
        if hasattr(args, 'cds_rq_full_fresh') and args.cds_rq_full_fresh:
            _jgtclirqdata_to_load.append(jgtclirqdata.CDS_RQ_FULL_FRESH)
        if hasattr(args, 'cds_rq_norm_fresh') and args.cds_rq_norm_fresh:
            _jgtclirqdata_to_load.append(jgtclirqdata.CDS_RQ_NORM_FRESH)
        if hasattr(args, 'pds_rq_normal') and args.pds_rq_normal:
            _jgtclirqdata_to_load.append(jgtclirqdata.PDS_RQ_NORMAL)
        if hasattr(args, 'pds_rq_normal_fresh') and args.pds_rq_normal_fresh:
            _jgtclirqdata_to_load.append(jgtclirqdata.PDS_RQ_NORMAL_FRESH)
        if hasattr(args, 'pds_rq_full') and args.pds_rq_full:
            _jgtclirqdata_to_load.append(jgtclirqdata.PDS_RQ_FULL)
        if hasattr(args, 'pds_rq_full_fresh') and args.pds_rq_full_fresh:
            _jgtclirqdata_to_load.append(jgtclirqdata.PDS_RQ_FULL_FRESH)
            
    except:
        pass
    #for each pattern we have, load their key/value into the args
    for pattern in _jgtclirqdata_to_load:
        try:
            #print(pattern)
            json_obj = json.loads(pattern)
            for key in json_obj:
                setattr(args, key, json_obj[key])
        except:
            pass
    return args


#Load a json content from the argument --json
def add_load_json_file_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    global default_parser
    if parser is None:
        parser=default_parser
    output_group=_get_group_by_title(parser,_ARG_GROUP_OUTPUT_TITLE,_ARG_GROUP_OUTPUT_DESCRIPTION)
    output_group.add_argument('-jsonf','--json_file',
                        help='JSON filepath content to be loaded.')
    
    return parser


def __json_post_parse():
    global args
    __check_if_parsed()
    
    try:
        #Create args from the json_file
        if hasattr(args, 'json_file') and args.json_file is not None:
            filepath = args.json_file
            #raise exception if file does not exist
            if not os.path.exists(filepath):
                raise Exception("File does not exist."+filepath)
            with open(filepath, 'r') as f:
                try:
                    json_obj = json.load(f)
                    for key in json_obj:
                        #print("key:"+key, " value:"+str(json_obj[key]))
                        setattr(args, key, json_obj[key])
                except:
                    pass
    except:
        pass
    return args


def add_exit_if_error(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    global default_parser
    if parser is None:
        parser=default_parser
        
    parser.add_argument('-xe','--exitonerror',
                        action='store_true',
                        help='Exit on error rather than trying to keep looking')
    return parser

def add_dropna_volume_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    global default_parser
    if parser is None:
        parser=default_parser
    
    cleanupGroup=_get_group_by_title(parser,_ARG_GROUP_CLEANUP_TITLE,_ARG_GROUP_CLEANUP_DESCRIPTION)
    
    dv_group=cleanupGroup.add_mutually_exclusive_group()
    
    dv_group.add_argument('-'+DROPNA_VOLUME_FLAG_ARGNAME_ALIAS,'--'+DROPNA_VOLUME_FLAG_ARGNAME,
                        action='store_true',
                        help='Drop rows with NaN (or 0) in volume column.  (note.Montly chart does not dropna volume)')
    
    dv_group.add_argument("-"+DONT_DROPNA_VOLUME_FLAG_ARGNAME_ALIAS,"--"+DONT_DROPNA_VOLUME_FLAG_ARGNAME, help="Do not dropna volume", action="store_true")
    
    return parser



def __dropna_volume__post_parse():
    try:
        dropna_volume_flag = _do_we_dropna_volume(args)
        setattr(args, 'dropna_volume',dropna_volume_flag)
        #dont_dropna_volume
        setattr(args, 'dont_dropna_volume',not dropna_volume_flag)
        
    except:
        pass
    return args

def __quiet__post_parse():
    try:
        if not hasattr(args, 'quiet') and (hasattr(args, 'verbose') and args.verbose==0):
            #add quiet to list
           #print("Quiet mode activated in parser")
           setattr(args, 'quiet', True)
        else:
            setattr(args, 'quiet', False)
    except:
        pass
    return args



def __timeframes_post_parse(timeframes=None)->argparse.Namespace:
    global args
    __check_if_parsed()
    if hasattr(args, 'timeframes'):
        _timeframes=args.timeframes 
    else :
        setattr(args, 'timeframes',None)
        return args
    
    _timeframes=None
    
    if isinstance(timeframes, list):
        _timeframes = timeframes
    else:
        _timeframes = parse_timeframes_helper(timeframes)
    setattr(args, 'timeframes',_timeframes)
    return args

from jgtconstants import TIMEFRAMES_ALL

def parse_timeframes_helper(timeframes):
    if timeframes in TIMEFRAMES_ALL:
        return [timeframes]
    if timeframes == "default" or timeframes == "all" :
        try:
            _timeframes = os.getenv("T").split(",")
        except:
            _timeframes = None
    else:
        try:
            _timeframes = timeframes.split(",")
        except:
            _timeframes = None
    return _timeframes

def __crop_last_dt__post_parse()->argparse.Namespace:
    global args
    __check_if_parsed()
    if hasattr(args, 'crop_last_dt'):
        if args.crop_last_dt is not None:
            setattr(args, 'crop_last_dt', args.crop_last_dt)
    else:
        setattr(args, 'crop_last_dt', None)
    return args

#@STCIssue We want this to Default to True and would be flagged to false by rm_bid_ask
def __keep_bid_ask__post_parse(keep_bid_ask_argname = 'keepbidask',rm_bid_ask_argname = 'rmbidask')->argparse.Namespace:
    global args
    __check_if_parsed()
    try:
        keep_bid_ask_value=True        
        
        if hasattr(args, rm_bid_ask_argname) or hasattr(args,'rm_bid_ask'):
            keep_bid_ask_value=False
        
        setattr(args, keep_bid_ask_argname,keep_bid_ask_value)
        setattr(args, 'keep_bid_ask',keep_bid_ask_value) # Future refactoring will be called just that.
        setattr(args, rm_bid_ask_argname,not keep_bid_ask_value)
    except:
        pass
    return args
    
def __verbose__post_parse()->argparse.Namespace:
    global args
    __check_if_parsed()
    try:
        if not hasattr(args, 'verbose'):
            setattr(args, 'verbose',0)
    except:
        pass
    return args

def __quotescount__post_parse()->argparse.Namespace:
    global args
    __check_if_parsed()
    try:
        if not hasattr(args, QUOTES_COUNT_ARGNAME):
            setattr(args, QUOTES_COUNT_ARGNAME,-1)
    except:
        pass
    return args

def __balligator_flag__post_parse()->argparse.Namespace:
    global args
    __check_if_parsed()
    try:
        if not hasattr(args, BALLIGATOR_FLAG_ARGNAME):
            setattr(args, BALLIGATOR_FLAG_ARGNAME,False)
            
        if hasattr(args, BALLIGATOR_FLAG_ARGNAME) and args.timeframe=="M1":
            #print("We dont do balligator for M1")
            setattr(args, BALLIGATOR_FLAG_ARGNAME,False)
    except:
        pass
    return args

def __talligator_flag__post_parse()->argparse.Namespace:
    global args
    __check_if_parsed()
    try:
        if not hasattr(args, TALLIGATOR_FLAG_ARGNAME):
            setattr(args, TALLIGATOR_FLAG_ARGNAME,False)
            
        if hasattr(args, TALLIGATOR_FLAG_ARGNAME) and args.timeframe=="M1":
            #print("We dont do talligator for M1")
            setattr(args, TALLIGATOR_FLAG_ARGNAME,False)
        
        if hasattr(args, TALLIGATOR_FLAG_ARGNAME) and args.timeframe=="W1":
            #print("We dont do talligator for W1")
            setattr(args, TALLIGATOR_FLAG_ARGNAME,False)
    except:
        pass
    return args


_NO_MFI_FOR_M1_flag=False
def __mfi_flag__post_parse()->argparse.Namespace:
    global args
    __check_if_parsed()
    try:
        if not hasattr(args, MFI_FLAG_ARGNAME):
            setattr(args, MFI_FLAG_ARGNAME,False)
        
        if _NO_MFI_FOR_M1_flag:
            if hasattr(args, MFI_FLAG_ARGNAME) and args.timeframe=="M1":
                #print("We dont do MFI for M1")
                setattr(args, MFI_FLAG_ARGNAME,False)
    except:
        pass
    return args


def __use_fresh__post_parse()->argparse.Namespace: 
    global args
    __check_if_parsed()
    try:
        if not hasattr(args, FRESH_FLAG_ARGNAME):
            setattr(args, FRESH_FLAG_ARGNAME,False)
        if hasattr(args, FRESH_FLAG_ARGNAME) and args.fresh:
            setattr(args, FRESH_FLAG_ARGNAME,True)
        else:
            if hasattr(args, NOT_FRESH_FLAG_ARGNAME) and args.notfresh:
                setattr(args, FRESH_FLAG_ARGNAME,False)
    except:
        pass
    return args

def __check_if_parsed():
    if args is None or args==[]:
        raise Exception("args is not set.  Run parse_args() first before calling this function.  Most likely, the CLI must be updated to do parser.parse_args() first instead of doing it in the main (REFACTORING Responsabilities)")

def _post_parse_dependent_arguments_rules()->argparse.Namespace:
    global args
    __check_if_parsed()
    
    args=__quiet__post_parse()
    
    
    # OTHER DEPENDENT RULES

    args=__dropna_volume__post_parse()
    
    args=__keep_bid_ask__post_parse()
    
    args=__timeframes_post_parse()
    args=__crop_last_dt__post_parse()
    args=__verbose__post_parse()
    args=__quotescount__post_parse()
    args=__balligator_flag__post_parse()
    args=__talligator_flag__post_parse()
    args=__mfi_flag__post_parse()
    args=__use_fresh__post_parse()
    args=__json_post_parse()   
    args=__jgtclirqdata_post_parse()
    return args



def parse_args(parser: argparse.ArgumentParser=None)->argparse.Namespace:
    global default_parser,args
    if parser is None:
        parser=default_parser
    args= parser.parse_args()
    
    
    args=_post_parse_dependent_arguments_rules()
    return args

def _do_we_dropna_volume(_args=None):
    global args
    if _args is None:
        _args=args
    dropna_volume_value = _args.dropna_volume or not _args.dont_dropna_volume
    if args.timeframe == "M1" and dropna_volume_value:
        print("We dont dropna volume for M1")
        return False # We dont drop for Monthly
    return dropna_volume_value

def add_viewpath_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
    """
    Adds an view path argument to the given argument parser.
    
    Args:
        parser (argparse.ArgumentParser): The argument parser to add the viewpath argument to.
        
    Returns:
        parser (argparse.ArgumentParser): The argument parser with the argument added.
    """
    global default_parser
    if parser is None:
        parser=default_parser
    output_group=_get_group_by_title(parser,_ARG_GROUP_OUTPUT_TITLE,_ARG_GROUP_OUTPUT_DESCRIPTION)
    output_group.add_argument('-vp','--viewpath',
                        action='store_true',
                        dest='viewpath',
                        help='flag to just view the path of files from arguments -i -t.')
    return parser


# def add_quiet_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:
#     parser.add_argument('-q','--quiet',
#                         action='store_true',
#                         help='Suppress all output. If specified, no output will be printed to the console.')
#     return parser

def add_verbose_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:

    global default_parser
    if parser is None:
        parser=default_parser
    
    group_verbosity=_get_group_by_title(parser,_ARG_GROUP_VERBOSITY_TITLE,_ARG_GROUP_VERBOSITY_DESCRIPTION)
    
    group_verbosity.add_argument('-v', '--verbose',
                        type=int,
                        default=0,
                        help='Set the verbosity level. 0 = quiet, 1 = normal, 2 = verbose, 3 = very verbose, etc.')
    return parser

def add_cds_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:

    global default_parser
    if parser is None:
        parser=default_parser

    parser.add_argument('-cds','--cds',
                        action='store_true',
                        default=False,
                        help='Action the creation of CDS')
    return parser

def add_ids_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:

    global default_parser
    if parser is None:
        parser=default_parser

    parser.add_argument('-ids','--ids',
                        action='store_true',
                        default=False,
                        help='Action the creation of IDS')
    return parser


def add_ids_mfi_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:

    global default_parser
    if parser is None:
        parser=default_parser
    group_indicators=_get_group_by_title(parser,_ARG_GROUP_INDICATOR_TITLE,_ARG_GROUP_INDICATOR_DESCRIPTION)
    mfi_exclusive_subgroup=group_indicators.add_mutually_exclusive_group()
    mfi_exclusive_subgroup.add_argument(
        "-"+MFI_FLAG_ARGNAME_ALIAS,
        "--"+MFI_FLAG_ARGNAME,
        action="store_true",
        help="Enable the Market Facilitation Index indicator.",
    )
    mfi_exclusive_subgroup.add_argument(
        "-"+NO_MFI_FLAG_ARGNAME_ALIAS,
        "--"+NO_MFI_FLAG_ARGNAME,  
        action="store_true",
        help="Disable the Market Facilitation Index indicator.",
    )  
    return parser

def add_ids_gator_oscillator_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:

    global default_parser
    if parser is None:
        parser=default_parser

    group_indicators=_get_group_by_title(parser,_ARG_GROUP_INDICATOR_TITLE,_ARG_GROUP_INDICATOR_DESCRIPTION)
    group_indicators.add_argument(
        "-"+GATOR_OSCILLATOR_FLAG_ARGNAME_ALIAS,
        "--"+GATOR_OSCILLATOR_FLAG_ARGNAME,
        action="store_true",
        help="Enable the Gator Oscillator indicator.",
    )
    return parser

def add_ids_fractal_largest_period_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:

    global default_parser
    if parser is None:
        parser=default_parser
    group_indicators=_get_group_by_title(parser,_ARG_GROUP_INDICATOR_TITLE,_ARG_GROUP_INDICATOR_DESCRIPTION)
    group_indicators.add_argument(
        "-lfp",
        "--largest_fractal_period",
        type=int,
        default=89,
        help="The largest fractal period.",
    )
    return parser

def add_ids_balligator_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:

    global default_parser
    if parser is None:
        parser=default_parser
    
    _description = "Enable the Big Alligator indicator."
    _argname_alias=BALLIGATOR_FLAG_ARGNAME_ALIAS
    _argname_full=BALLIGATOR_FLAG_ARGNAME
    
    
    _add_a_flag_helper( _description, _argname_alias, _argname_full,parser,group_title=_ARG_GROUP_INDICATOR_TITLE,group_description=_ARG_GROUP_INDICATOR_DESCRIPTION)
    
    group_indicators=_get_group_by_title(parser,_ARG_GROUP_INDICATOR_TITLE,_ARG_GROUP_INDICATOR_DESCRIPTION)
    group_indicators.add_argument(
        "-bjaw",
        "--balligator_period_jaws",
        type=int,
        default=89,
        help="The period of the Big Alligator jaws.",
    )
    return parser

  
def add_ids_talligator_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:

    global default_parser
    if parser is None:
        parser=default_parser
    
    group_indicators=_get_group_by_title(parser,_ARG_GROUP_INDICATOR_TITLE,_ARG_GROUP_INDICATOR_DESCRIPTION)
    group_indicators.add_argument(
        "-"+TALLIGATOR_FLAG_ARGNAME_ALIAS,
        "--"+TALLIGATOR_FLAG_ARGNAME,
        action="store_true",
        help="Enable the Tide Alligator indicator."
    )
    
    group_indicators.add_argument(
        "-tjaw",
        "--talligator_period_jaws",
        type=int,
        default=377,
        help="The period of the Tide Alligator jaws.",
    )
    return parser

def add_ads_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:

    global default_parser
    if parser is None:
        parser=default_parser
    interaction_group=_get_group_by_title(parser,_ARG_GROUP_INTERACTION_TITLE,_ARG_GROUP_INTERACTION_DESCRIPTION)
    interaction_group.add_argument('-ads','--ads',
                        action='store_true',
                        default=False,
                        help='Action the creation of ADS and show the chart')
    return parser

def add_iprop_init_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:

    global default_parser
    if parser is None:
        parser=default_parser

    parser.add_argument('-iprop','--iprop',
                        action='store_true',
                        default=False,
                        help='Toggle the downloads of all instrument properties ')
    return parser

def add_debug_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:

    global default_parser
    if parser is None:
        parser=default_parser

    group_verbosity=_get_group_by_title(parser,_ARG_GROUP_VERBOSITY_TITLE,_ARG_GROUP_VERBOSITY_DESCRIPTION)
    group_verbosity.add_argument('-debug','--debug',
                        action='store_true',
                        default=False,
                        help='Toggle debug ')
    return parser

def add_pdsserver_argument(parser: argparse.ArgumentParser=None)->argparse.ArgumentParser:

    global default_parser
    if parser is None:
        parser=default_parser

    parser.add_argument('-server','--server',
                        action='store_true',
                        default=False,
                        help='Run the server ')
    return parser


def print_exception(exception: Exception):
    #logging.error("Exception: {0}\n{1}".format(exception, traceback.format_exc()))
    print("Exception: {0}\n{1}".format(exception, traceback.format_exc()))






def diff_month(year: int, month: int, date2: datetime):
    return (year - date2.year) * 12 + month - date2.month



def export_env_if_any(config):
    # if has a key : "keep_bid_ask" and if yes and set to "true", export an env variable "JGT_KEEP_BID_ASK" to "1"
    if 'keep_bid_ask' in config and config['keep_bid_ask'] == True:
        os.environ['JGT_KEEP_BID_ASK'] = '1'

_JGT_CONFIG_JSON_SECRET=None

def readconfig(json_config_str=None,config_file = 'config.json',export_env=False,config_file_path_env_name='JGT_CONFIG_PATH',config_values_env_name='JGT_CONFIG'):
    global _JGT_CONFIG_JSON_SECRET
    #print argument values to debug
    _DEBUG_240619=False
    if _DEBUG_240619:
        print("json_config_str:",json_config_str)
        print("config_file:",config_file)
        print("export_env:",export_env)
        print("config_file_path_env_name:",config_file_path_env_name)
        print("config_values_env_name:",config_values_env_name)
    
    # Try reading config file from current directory

    if json_config_str is not None:
        config = json.loads(json_config_str)
        _JGT_CONFIG_JSON_SECRET=json_config_str
        if export_env:
            export_env_if_any(config)
        return config
    
    
    if _JGT_CONFIG_JSON_SECRET is not None:
        config = json.loads(_JGT_CONFIG_JSON_SECRET)
        if export_env:
            export_env_if_any(config)
        return config
    
    config = None

    # if file does not exist try set the path to the file in the HOME
    if not os.path.exists(config_file):
        config_file = os.path.join(os.path.expanduser("~"), config_file)
        
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            if export_env:
                export_env_if_any(config)
            return config
    else:
        # If config file not found, check home directory
        home_dir = os.path.expanduser("~")
        config_file = os.path.join(home_dir, config_file)
        if os.path.isfile(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            # If config file still not found, try reading from environment variable
            config_json_str = os.getenv('JGT_CONFIG_JSON_SECRET')
            if config_json_str:
                config = json.loads(config_json_str)
                if export_env:
                    export_env_if_any(config)
                return config


    # Now you can use the config dictionary in your application

    # if file dont exist, try loading from env var JGT_CONFIG
    if not os.path.exists(config_file):
        config_json_str = os.getenv(config_values_env_name)
        
        if config_json_str:
            config = json.loads(config_json_str)
            if export_env:
                export_env_if_any(config)
            #return config
        else:
            # if not found, try loading from env var JGT_CONFIG_PATH
            config_file = os.getenv(config_file_path_env_name)
            if config_file:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    if export_env:
                        export_env_if_any(config)
                    #return config
           # else:
               
    # Read config file
    if config is None:
        print("config_file:",config_file)
        if config_file is not None and os.path.exists(config_file) :
            with open(config_file, 'r') as file:
                config = json.load(file)
        
    if config is None:
        raise Exception(f"Configuration not found. Please provide a config file or set the JGT_CONFIG environment variable to the JSON config string. (config_file={config_file})")
    
    if export_env:
        export_env_if_any(config)
    return config
