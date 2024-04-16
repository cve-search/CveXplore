import collections

task_status_codes = collections.namedtuple("task_status_codes", ["OK", "NOK"])(0, 1)

task_status_list = [
    x.lower()
    for x in task_status_codes.__dir__()
    if not x.startswith("_") and x not in ["index", "count"]
]

task_status_rev_types = {
    getattr(task_status_codes, x.upper()): x for x in task_status_list
}
