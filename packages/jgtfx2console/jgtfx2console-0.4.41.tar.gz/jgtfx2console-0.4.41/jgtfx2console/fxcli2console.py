#!/usr/bin/env python

# Copyright 2019 Gehtsoft USA LLC

# Licensed under the license derived from the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at

# http://fxcodebase.com/licenses/open-source/license.html

# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import subprocess
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
from forexconnect import ForexConnect, fxcorepy
#from jgtpy import JGTConfig as conf

from dotenv import load_dotenv
from dotenv import dotenv_values

load_dotenv()  # take environment variables from .env.
#env=load_dotenv(os.getenv(os.getcwd()))
env = dotenv_values(".env")

if os.getenv('user_id') == "":
  load_dotenv(os.getenv('HOME'))
if os.getenv('user_id') == "":
  load_dotenv(os.getenv(os.getcwd()))

user_id = os.getenv('user_id')
password = os.getenv('password')
url = os.getenv('url')
connection = os.getenv('connection')
quotes_count = os.getenv('quotes_count')

#from jgtpy import jgtcommon as jgtcomm,iprops
from jgtutils import jgtcommon as jgtcomm,iprops,jgtconstants as c

##import jgtcommon as jgtcomm,iprops

import common_samples
"""

url='https://www.fxcorporate.com/Hosts.jsp'
connection='Demo'
quotes_count='800'
"""

def _parse_args():
    
    parser = jgtcomm.new_parser("Get historical data from FXConnect","fxcli2console","That cli produces output to console and is used by jgtfxcli as a subprocess alternative for some retrieval that fails.  It is a wrapper around forexconnect package that you can install on python over 3.7.")
    #jgtcomm.add_main_arguments(parser)
    jgtcomm.add_instrument_timeframe_arguments(parser)
    #common_samples.add_date_arguments(parser)
    jgtcomm.add_tlid_range_argument(parser)
    #jgtcomm.add_date_arguments(parser)
    jgtcomm.add_bars_amount_V2_arguments(parser)
    jgtcomm.add_keepbidask_argument(parser)
    args = jgtcomm.parse_args(parser)
    return args


def main():
    args = _parse_args()    
    if len(sys.argv) == 1:
        subprocess.run([sys.argv[0], "--help"])
        return
    str_user_id = user_id#args.l
    str_password = password#args.p
    str_url = url#args.u
    
    keep_bid_ask = args.keepbidask

    #env variable bypass if env exist JGT_KEEP_BID_ASK=1, keep_bid_ask = True
    if os.getenv("JGT_KEEP_BID_ASK","0") == "1" and not args.rmbidask:
        keep_bid_ask = True
        
    using_tlid = False
    if args.tlidrange is not None:
      using_tlid= True
      tlid_range = args.tlidrange
      #print(tlid_range)
      dtf,dtt = jgtcomm.tlid_range_to_start_end_datetime(tlid_range)
      #print(str(dtf) + " " + str(dtt))
      date_from =dtf
      date_to = dtt
      print(str(date_from),str(date_to))
    else:
      quotes_count = args.quotescount
      
    str_connection = connection#args.c
    #str_session_id = args.session
    #str_pin = args.pin
    
    str_instrument = args.instrument
    str_timeframe = args.timeframe
    

    ip = iprops.get_iprop(instrument=str_instrument)
    pips= ip["pips"]
    lpip=len(str(pips))
    
    with ForexConnect() as fx:
        try:
            fx.login(str_user_id, str_password, str_url,
                     str_connection,
                     common_samples.session_status_changed)

            #print("")
            #print("Requesting a price history...")
            if using_tlid:
              history = fx.get_history(str_instrument, str_timeframe, date_from, date_to)
            else:
              history = fx.get_history(str_instrument, str_timeframe,None,None, quotes_count)
            current_unit, _ = ForexConnect.parse_timeframe(str_timeframe)
           
            #date_format = '%m.%d.%Y %H:%M:%S'
            date_format = '%Y-%m-%d %H:%M:%S'
            if current_unit == fxcorepy.O2GTimeFrameUnit.TICK:
                print("Date, Bid, Ask")
                #print(history.dtype.names)
                for row in history:
                    print("{0:s}, {1:,.5f}, {2:,.5f}".format(
                        pd.to_datetime(str(row['Date'])).strftime(date_format), row['Bid'], row['Ask']))
            else:
                csv_header_OHLC = "Date,Open,High,Low,Close,Median,Volume"
                csv_header_OHLCBIDASK="Date,BidOpen,BidHigh,BidLow,BidClose,AskOpen,AskHigh,AskLow,AskClose,Volume,Open,High,Low,Close,Median"
                csv_header=csv_header_OHLC
                if keep_bid_ask:
                    csv_header=csv_header_OHLCBIDASK
                print(csv_header)
                rounder = lpip+1
                for row in history:
                    print(format_output(rounder,row,rounder,date_format,keep_bid_ask=keep_bid_ask))
                    
                    # print("{0:s},{1:.5f},{2:.5f},{3:.5f},{4:.5f},{5:.5f},{6:d}".format(                    
                    #     pd.to_datetime(str(row['Date'])).strftime(date_format), open_price, high_price,
                    #     low_price, close_price, median, row['Volume']))
        except Exception as e:
            jgtcomm.print_exception(e)
        try:
            fx.logout()
        except Exception as e:
            jgtcomm.print_exception(e)

def format_output(nb_decimal, row, rounder, date_format = '%Y-%m-%d %H:%M:%S',keep_bid_ask=False):
    open_price = round(((row[c.BIDOPEN] + row[c.ASKOPEN]) / 2), rounder)
    high_price = round(((row[c.BIDHIGH] + row[c.ASKHIGH]) / 2), rounder)
    low_price = round(((row[c.BIDLOW] + row[c.ASKLOW]) / 2), rounder)
    close_price = round(((row[c.BIDCLOSE] + row[c.ASKCLOSE]) / 2), rounder)
    median = round(((high_price + low_price) / 2), rounder)
    dt_formatted=pd.to_datetime(str(row[c.DATE])).strftime(date_format)
    #print("dt formatted: " + dt_formatted)
    #if keep_bid_ask:Date,BidOpen,BidHigh,BidLow,BidClose,AskOpen,AskHigh,AskLow,AskClose,Volume,Open,High,Low,Close,Median
    if keep_bid_ask:
        formatted_string = f"{dt_formatted},{row[c.BIDOPEN]:.{nb_decimal}f},{row[c.BIDHIGH]:.{nb_decimal}f},{row[c.BIDLOW]:.{nb_decimal}f},{row[c.BIDCLOSE]:.{nb_decimal}f},{row[c.ASKOPEN]:.{nb_decimal}f},{row[c.ASKHIGH]:.{nb_decimal}f},{row[c.ASKLOW]:.{nb_decimal}f},{row[c.ASKCLOSE]:.{nb_decimal}f},{row[c.VOLUME]:d},{open_price:.{nb_decimal}f},{high_price:.{nb_decimal}f},{low_price:.{nb_decimal}f},{close_price:.{nb_decimal}f},{median:.{nb_decimal}f}"
    else:
        formatted_string = f"{dt_formatted},{open_price:.{nb_decimal}f},{high_price:.{nb_decimal}f},{low_price:.{nb_decimal}f},{close_price:.{nb_decimal}f},{median:.{nb_decimal}f},{row['Volume']:d}"
        
    return formatted_string
  
def format_output1(nb_decimal, row, rounder,date_format = '%Y-%m-%d %H:%M:%S'):
    open_price = round(((row['BidOpen'] + row['AskOpen']) / 2),rounder)
    high_price = round(((row['BidHigh'] + row['AskHigh']) / 2),rounder)
    low_price = round(((row['BidLow'] + row['AskLow']) / 2),rounder)
    close_price = round(((row['BidClose'] + row['AskClose']) / 2),rounder)
    median = round(((high_price + low_price) / 2),rounder)
    format_specifier = f"{{:.{nb_decimal}f}}"
    formatted_string = f"{pd.to_datetime(str(row['Date'])).strftime(date_format)},{open_price:{format_specifier}},{high_price:{format_specifier}},{low_price:{format_specifier}},{close_price:{format_specifier}},{median:{format_specifier}},{row['Volume']:d}"
    return formatted_string

# Usage

if __name__ == "__main__":
    main()
    print("")
    #input("Done! Press enter key to exit\n")
