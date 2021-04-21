import utils
import logutils
import anomaly_detection

import sys
import re
import os
import json
import numpy as np

ALL_ACTIVITIES_LOGFILE = 'all_activities.log'
AAU_LOG_PATTERN = r'\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2},\d{3}\s[\S]+\s+\[[\S]+\]\s+[\S]+\s+.*'
ACTIVITY_LOG_PATTERN_BEGIN = r'(\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s([\S]+)\s+\[([\S]+)\]-(\[[\S]+)\]\s[\S]+\s+.*'
ACTIVITY_LOG_PATTERN_END = r':\s(.*)'

vms_user_connected = r'ACTIVITY_ID\(\d\d\d\d\d\d\).*Admin chose not to update VMs with logged in users.*'
vms_failed_update = r'(ACTIVITY_ID\(\d\d\d\d\d\d\))(.*Agent Update failed.*)'
vms_timedout = r'(ACTIVITY_ID\(\d\d\d\d\d\d\))(.*Agent Update thread ti`meout.*)'
start_summary_regex = logutils.log_date_format + r'.*(ACTIVITY_ID\(\d+\): Created a fabric task to update agents on a pool\/Image\. pool_id:.*)'
end_summary_regex = logutils.log_date_format + r'.*POOL_TASK_UPDATES.*(ACTIVITY_ID\(\d+\): VM count.*)'

# activities with no failures
zero_failure_activity_regex = 'ACTIVITY_ID.*Finished updating all VM.*0 failures'

# these are AAU specific patterns to turn to * in the messages
aau_star_regex      = [
    r'(?<=vmName\=)([A-Za-z0-9\-])+(?=\,)',
    r'(?<=application\=)([A-Za-z0-9\-])+(?=\,)',
    r'(?<=poolOrPatternName: )([A-Za-z0-9\-])+(?=\,)'
]

# folders where the results from the activities are stored in a json file for training and test
TRAINING_FOLDER = logutils.RESULTS_DIR + "/aau"
TEST_FOLDER = logutils.RESULTS_DIR + "/aau_test"
TRAINED_MODEL_FILENAME = TRAINING_FOLDER + "/aau.clf"

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

def log_to_json(run, log):
    e = {}
    e['activity'] = run
    e['date'] = log[0]
    e['level'] = log[1]
    e['class'] = log[2]
    e['thread'] = log[3]
    e['message'] = log[4]

    return e


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
            event = log_to_json(run, p)
            events.append(event)
        activities[id] = events

    return activities

def processAAU(folder, tenantlogs):
    tfile = open(folder + '/' + tenantlogs, 'r')
    logs = tfile.read()
    tfile.close()

    aau = re.findall(AAU_LOG_PATTERN + 'ACTIVITY_ID.*', logs)
#    aau = re.findall(r'ACTIVITY_ID\(\d+\)', logs)
    print("Found " + str(len(aau)) + " AAU logs")
    aau_logs = save_activities_file(aau)
    aau_runs = get_unique_aau_runs(aau)

    zero_failures = re.findall(AAU_LOG_PATTERN + zero_failure_activity_regex, logs)
    zero_failure_runs = get_unique_aau_runs(zero_failures)

#    print("The following had no failures:" + str(zero_failure_runs))
#    print("The following AAU runs were identified:\t" + str(aau_runs))

    # save the individual runs into log files
    activities = find_aau_runs(aau_runs, aau_logs)

    return activities, zero_failure_runs

def save_aau_train_test_runs(folder, activities, zero_failures):
    if not os.path.exists(folder):
        os.mkdir(folder)
    
    tfolder = folder + '/aau'
    if not os.path.exists(tfolder):
        os.mkdir(tfolder)

    testfolder = folder + '/aau_test'
    if not os.path.exists(testfolder):
        os.mkdir(testfolder)

    for run in activities.keys():
        f = run.replace('(', '_').replace(')', '')
        if run in zero_failures:
            filename = tfolder + '/' + f + 'json'
        else:
            filename = testfolder + '/' + f + 'json' 
        utils.save_json(filename, activities[run])

def save_aau_runs(name, activities):
    folder = logutils.RESULTS_DIR
    if not os.path.exists(folder):
        os.mkdir(folder)
    
    tfolder = folder + '/' + name
    if not os.path.exists(tfolder):
        os.mkdir(tfolder)

    for run in activities.keys():
        f = run.replace('(', '_').replace(')', '')
        filename = tfolder + '/' + f + 'json'
        utils.save_json(filename, activities[run])

def extract_aau_events(folder):
    data_folder = logutils.LOG_BASE_DIR + '/' + folder
    print("Processing AAU activity in " + data_folder)
    activity_logs, no_fails = processAAU(data_folder, logutils.TENANT_LOG_FILE)
    save_aau_runs(folder, activity_logs)


def main():
    args = sys.argv[1:]

    if not args:
        # look for AAU in tenant logs
        activities = {}
        zero_failures = []
        for folder in logutils.get_log_dirs():
            print("Processing AAU activity in " + folder)
            activity_logs, no_fails = processAAU(folder, logutils.TENANT_LOG_FILE)
            activities = utils.merge_dicts_with_arrays(activities, activity_logs)
            for success in no_fails:
                zero_failures.append(success.replace('(', '.').replace(')', '.'))
            
            print('\n')

        # save the activities in the base folder
        print('All activities with no failures - ' + str(zero_failures))
        save_aau_train_test_runs(logutils.RESULTS_DIR, activities, zero_failures)

        # train the model on successful runs
        anomaly_detection.train_and_save_model(TRAINING_FOLDER, aau_star_regex, TRAINED_MODEL_FILENAME)

    elif (args[0] == '-test'):
        # test the model on trained model
        anomaly_detection.predict(TEST_FOLDER, aau_star_regex, TRAINED_MODEL_FILENAME)

    elif (args[0]=='-bm'):
        print("Building model ")
        # only build the model based on training data in the TRAINING_FOLDER
        anomaly_detection.train_and_save_model(TRAINING_FOLDER, aau_star_regex, TRAINED_MODEL_FILENAME)

    elif (args[0] == '-f'):
        folder = args[1]
        extract_aau_events(folder)

        # predict the anomalies for the given folder
        anomaly_detection.predict(logutils.RESULTS_DIR + "/" + folder, aau_star_regex, TRAINED_MODEL_FILENAME)
    else:
        print ("Invalid arguments " + args)




# Start program
if __name__ == "__main__":
    main()