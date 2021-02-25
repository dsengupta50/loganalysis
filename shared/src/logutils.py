import glob
import sys
import numpy
import re
import os

log_date_format = r'(\d\d\d\d-\d\d-\d\d\s\d\d:\d\d:\d\d,\d\d\d\s)'

# log directories and files
LOG_BASE_DIR = 'data'
TENANT_LOG_FILES = 'tenant.log*'
TENANT_LOG_FILE = 'alltenant.log'

RESULTS_DIR = 'results'

def order(name):
    return int(findLogRotationNumber('\.\d+', name)[1:])

def find(pat, text):
    match = re.search(pat, text)
    if match:
        #print(text + ":\t" + match.group())
        return match.group()
        
    return None

def findLogRotationNumber(pat, text):
    number = find(pat, text)
    if number==None:
        return '.0'

    return number

def sort_files(files):
    return sorted(files, reverse=True, key=order)

def concatenate_logs(folder, input_pattern, outputfilename):
    print("\nProcessing files from " + folder + ".......")
    logfiles = folder + input_pattern
    outfile = folder + outputfilename
    if (os.path.exists(outfile)) :
        print (outfile + " already exists, not regenerating")
        return
    
    files = glob.glob(logfiles)
    sorted_files = sort_files(files)
    out = open(outfile, "a")

    for file in sorted_files:
        print("Appending " + file)
        fin = open(file, 'r')
        input = fin.read()
        out.write(input)
        fin.close()

    out.close()

def gunzip_logs(folder):
    gzfiles = folder + '/*.gz'
    print ('starting gunzip on' + folder)
    os.system('gunzip ' + gzfiles)
    print ("gunzip completed.")

def find_patterns(logs, regex):
    return re.findall(regex, logs)

def print_results(logs, regex):
    results = re.findall(regex, logs)
    for result in results:
        print(str(result))

    return results

def print_title(str):
    print('*********' + str + '***********')

def test():
    files = ['/Users/senguptad/Downloads/pwc-pod50-aau-phase2/desktone/tenant.log.50', '/Users/senguptad/Downloads/pwc-pod50-aau-phase2/desktone/tenant.log.9', '/Users/senguptad/Downloads/pwc-pod50-aau-phase2/desktone/tenant.log.32', '/Users/senguptad/Downloads/pwc-pod50-aau-phase2/desktone/tenant.log.35', '/Users/senguptad/Downloads/pwc-pod50-aau-phase2/desktone/tenant.log.7']
#    files = ['tenant.log.50', 'tenant.log.9', 'tenant.log.32', 'tenant.log.35', 'tenant.log.7']
    print(sort_files(files))

def get_log_dirs():
    dirs = []
    files = os.listdir(LOG_BASE_DIR)
    
    for f in files:
        f = LOG_BASE_DIR+'/'+f
        if os.path.isdir(f):            
            dirs.append(f)
    
    #print(dirs)
    return dirs

def save_logs(filename, logs):
    tfile = open(filename, 'w')
    for log in logs:
        #print(log + '\n')
        tfile.writelines(str(log) + '\n')
    tfile.close()