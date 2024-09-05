import os
import subprocess
import curses
import datetime

def list_strategies(strategy_folder):
    return [
        f.replace('.py', '') for f in os.listdir(strategy_folder)
        if f.endswith('.py')
    ]

def select_items(stdscr, items, prompt):
    selected = []
    current_row = 0

    while True:
        stdscr.clear()
        stdscr.addstr(prompt + "\n")
        for idx, item in enumerate(items):
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(f"{idx + 1}: {item}\n")
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(f"{idx + 1}: {item}\n")

        if selected:
            stdscr.addstr("\nSelected:\n")
            stdscr.addstr(", ".join(selected) + "\n")

        stdscr.addstr("\nPress Enter to select/deselect, 'd' for Done.\n")

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(items) - 1:
            current_row += 1
        elif key == ord('\n'):
            if items[current_row] in selected:
                selected.remove(items[current_row])
            else:
                selected.append(items[current_row])
        elif key == ord('d'):
            return selected

    return selected

def get_custom_timerange(stdscr, prompt):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(prompt + "\n")
    stdscr.refresh()
    timerange = stdscr.getstr().decode('utf-8')
    curses.noecho()

    # Check if only one date was entered
    if '-' not in timerange:
        start_date = timerange
        end_date = datetime.datetime.today().strftime('%Y%m%d')
        timerange = f"{start_date}-{end_date}"

    return timerange

def run_backtest(strategy, timeframe, timerange):
    command = [
        'freqtrade', 'backtesting',
        '--strategy', strategy,
        '--timeframe', timeframe,
        '--timerange', timerange,
        '--config', './config_backtest_usdt_spot_new.json'
    ]
    subprocess.run(command)

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    strategy_folder = 'strategies'
    strategies = list_strategies(strategy_folder)

    if not strategies:
        stdscr.addstr("No strategies found in the folder.\n")
        stdscr.refresh()
        stdscr.getch()
        return

    selected_strategies = select_items(stdscr, strategies, "Select Strategies (use arrows to navigate):")

    if not selected_strategies:
        stdscr.addstr("No strategies selected.\n")
        stdscr.refresh()
        stdscr.getch()
        return

    timeframes = ['5m', '15m', '1h']
    selected_timeframes = select_items(stdscr, timeframes, "Select timeframes (use arrows to navigate):")

    if not selected_timeframes:
        stdscr.addstr("No timeframes selected.\n")
        stdscr.refresh()
        stdscr.getch()
        return

    timerange = get_custom_timerange(stdscr, "Enter the timerange (YYYYMMDD-YYYYMMDD):")

    for strategy in selected_strategies:
        for timeframe in selected_timeframes:
            stdscr.clear()
            stdscr.addstr(f"Running backtest for strategy '{strategy}' on timeframe '{timeframe}' with timerange '{timerange}'...\n")
            stdscr.refresh()
            run_backtest(strategy, timeframe, timerange)
            stdscr.addstr("Backtest completed.\n")
            stdscr.refresh()
            stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)