import json
import os

stats_path = os.path.join(os.path.dirname(__file__), "../output")


def get_stats():
    res_dirs = []
    for root, dirs, files in os.walk(stats_path):
        for dir_ in dirs:
            res_dirs.append(dir_)

    stats = []
    for dir_ in res_dirs:
        res_file = None
        generated_methods = 0

        for root, dirs, files in os.walk(os.path.join(stats_path, dir_)):
            for file in files:
                if file.endswith("_res.json"):
                    res_file = os.path.join(stats_path, dir_, file)
            for dir__ in dirs:
                if dir__ == "generated_methods":
                    for _, _, files_ in os.walk(os.path.join(stats_path, dir_, dir__)):
                        for file in files_:
                            if file.endswith(".java.txt"):
                                generated_methods += 1

        if res_file is None:
            continue

        with open(res_file, "r") as file:
            data = json.load(file)

        mutable_events_index = [key for key in data if key.isdigit() and data[key]['mutable']]
        mutable_event_count = len(mutable_events_index)
        correlation = [
            {"assertion": int(key.split('_').pop()) + 1,
             "event": int(data['assertion_correlations'][key]['event_correlation']) + 1} for
            key in
            data['assertion_correlations']
        ]
        candidates_before = data['candidates_before']
        candidates_after = [len(data[key]['attempted_paths']) + len(data[key]['successful_paths']) for key in data if
                            key.isdigit()]
        time = f"{data['time']: .2f}"

        stat = {
            "name": dir_,
            "assertion_correlations": correlation,
            "candidates_after": candidates_after,
            "candidates_before": candidates_before,
            "generated_methods": generated_methods,
            "mutable_event_count": mutable_event_count,
            "mutable_event_indices": mutable_events_index,
            "path": os.path.abspath(os.path.join(stats_path, dir_)),
            "time": time
        }

        stats.append(stat)

    return stats


def find_stats(index: int):
    stats = get_stats()

    if len(stats) == 0:
        return None

    if index < 1 or index > len(stats):
        return None

    return stats[index - 1]


def get_stat_string(index: int):
    stats = get_stats()
    index = int(index)

    if len(stats) == 0:
        return "No statistics available."

    if index < 1 or index > len(stats):
        return "Invalid index."

    target = stats[index - 1]

    result = "Assertion Correlations:\n"
    for correlation in target['assertion_correlations']:
        result += f"  - Assertion {correlation['assertion']} correlates with Event {correlation['event']}\n"

    if len(target['assertion_correlations']) == 0:
        result += "  - None\n"

    result += "Candidates Before:\n"
    for i in range(len(target['candidates_before'])):
        result += f"  - Event {i + 1}: {target['candidates_before'][i]}\n"

    result += "Candidates After:\n"
    for i in range(len(target['candidates_after'])):
        result += f"  - Event {i + 1}: {target['candidates_after'][i]}\n"

    result += f"Generated Methods: {target['generated_methods']}\n"

    result += f"Mutable Event Count: {target['mutable_event_count']}\n"

    result += f"Mutable Event Indices: {' '.join(map(str, target['mutable_event_indices']))}\n"

    result += f"Time: {target['time']}s"

    result += f"\n\nPath: {target['path']}"

    return result
