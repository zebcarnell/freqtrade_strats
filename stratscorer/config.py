##!/usr/bin/env python3
# This file contains all configurations

# backtest timeframes
# Possible timeframes are ['1m','5m','15m','30m','1h','2h','4h','6h','8h','12h','1d','2d','3d','1w','1m','1y']
bt_tf = ["1d", "4h", "1h", "30m", "15m", "5m"]  # original settings
#bt_tf = ["1h", "30m", "15m", "5m"]
# bt_tf = ["1d", "4h", "1h",]

# backtest timeranges
bt_tr = "-20230101"
# bt_tr = "20220901-20231111"

# 30m, 15 min, 5 min and 1 min timerange.
# Since backtesting these timeframes over 5+ years prove to give unreliable backtests.
bt_tr_30m = "20190101-20230101"
bt_tr_15m = "20190101-20230101"
bt_tr_5m = "20200101-20230101"
bt_tr_1m = "20210101-20230101"
# ENTRIES BELOW ARE FOR TESTING OR INDIVIDUAL BACKTEST PURPOSES
# bt_tr_30m = "20221201-20230101"
# bt_tr_15m = "20220901-20230101"
# bt_tr_5m = "20220101-20230101"
# bt_tr_1m = "20221201-20230101"

# Hyperopt timeframes - different from backtesting!
ho_tr_30m = "20200101-20220101"
ho_tr_15m = "20200101-20220101"
ho_tr_5m = "20210101-20220101"
ho_tr_1m = "20210601-20220101"
ho_tr = "20190101-20220101"

# FREQTRADE INSTALLATION INFORMATION

# Directory configuration
ft_dir = "/opt/freqtrade"  # directory where freqtrade is installed
# strategies directory where you keep your strategies
strategy_dir = "/user_data/strategies/"

# name / location of the config files for spot or futures trading within the freqtrade directory.
# default is freqtrade dir.
spot_cfg = "/user_data/spot_config.json"
futures_cfg = "/user_data/futures_config.json"

# name of exchange where data is downloaded from
# determines the data directory to be used in backtesting.
crypto_exch = "binance"

# STRATSCORER INSTALLATION INFORMATION

# Directory configuration
install_dir = "/opt/stratscorer"  # Directory where program is located
db_path = "./db/"  # Databases location
logs_dir = "./logs/"  # Logs directory
backup_dir = "./db_backup/"  # Backup directory
bt_data = "/data"  # Directory for backtest export data
all_strategies_dir = "./all_strategies/"  # All tested strategies collection
import_dir = "./import/"
export_dir = "./export/"

# database names
db_name = "stratscorer.db"
league_db_name = "strategy_league.db"
pair_results_db_name = "pairs.db"
