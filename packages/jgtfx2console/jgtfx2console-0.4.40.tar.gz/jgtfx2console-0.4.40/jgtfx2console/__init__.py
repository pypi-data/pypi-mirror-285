# Copyright 2024 Jean Guillaume Isabelle
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. moduleauthor:: Jean Guillaume Isabelle <jgi@jgwill.com>
"""

# from jgtfxcommon.BatchOrderMonitor import BatchOrderMonitor
# from jgtfxcommon.OrderMonitor import OrderMonitor
# from jgtfxcommon.OrderMonitorNetting import OrderMonitorNetting
# from jgtfxcommon.TableListenerContainer import TableListenerContainer
# from jgtfxcommon.common import add_main_arguments, add_instrument_timeframe_arguments, \
#     add_candle_open_price_mode_argument, add_direction_rate_lots_arguments, add_account_arguments, \
#     valid_datetime, add_date_arguments, add_report_date_arguments, add_max_bars_arguments, add_bars_arguments, \
#     print_exception, session_status_changed, diff_month, convert_timeframe_to_seconds

import os
import platform
import sys

import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))




import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="importlib._bootstrap")
    # your code here


__version__ = "0.4.40"


