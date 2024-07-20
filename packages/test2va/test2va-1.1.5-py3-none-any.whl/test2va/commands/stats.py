from test2va.bridge import get_stats
from test2va.bridge.stats import get_stat_string


def stats_list_command():
    stats = get_stats()

    if len(stats) == 0:
        print("No statistics available.")
        return

    for i in range(len(stats)):
        print(f"{i + 1}. {stats[i]['name']}")


def stats_view_command(index):
    print(get_stat_string(index))
