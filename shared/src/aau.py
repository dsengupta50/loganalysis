import utils
import logutils
import re
import os
import json

ALL_ACTIVITIES_LOGFILE = 'all_activities.log'
AAU_LOG_PATTERN = r'\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2},\d{3}\s[\S]+\s\s\[[\S]+\]\s[\S]+\s'
ACTIVITY_LOG_PATTERN_BEGIN = r'(\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s([\S]+)\s\s\[([\S]+)\]-(\[[\S]+)\]\s[\S]+\s'
ACTIVITY_LOG_PATTERN_END = r':\s(.*)'

vms_user_connected = r'ACTIVITY_ID\(\d\d\d\d\d\d\).*Admin chose not to update VMs with logged in users.*'
vms_failed_update = r'(ACTIVITY_ID\(\d\d\d\d\d\d\))(.*Agent Update failed.*)'
vms_timedout = r'(ACTIVITY_ID\(\d\d\d\d\d\d\))(.*Agent Update thread timeout.*)'
start_summary_regex = logutils.log_date_format + r'.*(ACTIVITY_ID\(\d+\): Created a fabric task to update agents on a pool\/Image\. pool_id:.*)'
end_summary_regex = logutils.log_date_format + r'.*POOL_TASK_UPDATES.*(ACTIVITY_ID\(\d+\): VM count.*)'


'''
We want to summarize every AAU activity run with the following parameters:
1. Start time
2. Pool ID
3. Agent version
4. Number of desktops in the pool
5. How many Success, Skipped, Failed
6. Failed - desktop name
7. Total Duration
'''
def summarize_aau(logs, ids):
    logutils.print_title('AAU STARTS')
    logutils.print_results(logs, start_summary_regex)
    logutils.print_title('SKIPPED VMs')
    logutils.print_results(logs, vms_user_connected)
    logutils.print_title('AAU TIMEOUTS')
    logutils.print_results(logs, vms_timedout)
    logutils.print_title('FAILED AAU')
    logutils.print_results(logs, vms_failed_update)
    logutils.print_title('AAU END')
    logutils.print_results(logs, end_summary_regex)

def get_unique_aau_runs(logs):
    # find the unique activity_ids
    unique_aau_ids = {}
    activity_ids = re.findall(r'ACTIVITY_ID\(\d+\)', str(logs))
    for ids in activity_ids:
        unique_aau_ids[ids] = ids

    aau_ids = unique_aau_ids.keys()
    return aau_ids

def save_activities_file(aau_logs):
    folder = logutils.RESULTS_DIR
    if not os.path.exists(folder):
        os.mkdir(folder)
    tfolder = folder + '/aau'
    if not os.path.exists(tfolder):
        os.mkdir(tfolder)

    filename = tfolder + '/' + ALL_ACTIVITIES_LOGFILE
    logutils.save_logs(filename, aau_logs)

    tfile = open(filename, 'r')
    logs = tfile.read()
    tfile.close()
    os.remove(filename)

    return logs

'''
def find_aau_runs(aau_runs, logs):
    activities = {}
    for run in aau_runs:
        id = run.replace('(', '.').replace(')', '.')
        pattern = ACTIVITY_LOG_PATTERN_BEGIN + run + ACTIVITY_LOG_PATTERN_END
        pattern = pattern.replace('(', '.').replace(')', '.')
        patterns = re.findall(pattern, logs)
        print(id + ':' + str(len(patterns)))
        activities[id] = patterns

    return activities
'''
def log_to_json(log):
    e = {}
    e['date'] = log[0]
    e['level'] = log[1]
    e['class'] = log[2]
    e['thread'] = log[3]
    e['message'] = log[4]

    return json.dumps(e)


def find_aau_runs(aau_runs, logs):
    activities = {}
    for run in aau_runs:
        id = run.replace('(', '.').replace(')', '.')
        pattern = ACTIVITY_LOG_PATTERN_BEGIN + id + ACTIVITY_LOG_PATTERN_END
        patterns = logutils.find_patterns(logs, pattern)
        pattern = pattern[:len(pattern)-2]
        print(id + ':' + str(len(patterns)))
        events = []
        for p in patterns:
            event = log_to_json(p)
            events.append(event)
        activities[id] = events

    return activities

def processAAU(folder, tenantlogs):
    tfile = open(folder + '/desktone/' + tenantlogs, 'r')
    logs = tfile.read()
    tfile.close()

    aau = re.findall(AAU_LOG_PATTERN + 'ACTIVITY_ID.*', logs)
    print("Found " + str(len(aau)) + " AAU logs")
    aau_logs = save_activities_file(aau)
    aau_runs = get_unique_aau_runs(aau)

#    print("The following AAU runs were identified:\t" + str(aau_runs))

    # save the individual runs into log files
    activities = find_aau_runs(aau_runs, aau_logs)

    return activities

def save_aau_run(folder, activities):
    if not os.path.exists(folder):
        os.mkdir(folder)
    
    tfolder = folder + '/aau'
    if not os.path.exists(tfolder):
        os.mkdir(tfolder)

    for run in activities.keys():
        f = run.replace('(', '_').replace(')', '')
        filename = tfolder + '/' + f + 'json'
        logutils.save_logs(filename, activities[run])

def main():
    # look for AAU in tenant logs
    activities = {}
    for folder in logutils.get_log_dirs():
        print("Processing AAU activity in " + folder)
        activity_logs = processAAU(folder, logutils.TENANT_LOG_FILE)
        activities = utils.merge_dicts_with_arrays(activities, activity_logs)
        print('\n')

    # save the activities in the base folder
    save_aau_run(logutils.RESULTS_DIR, activities)

    # convert the logs for each run into json records

# Start program
if __name__ == "__main__":
    main()