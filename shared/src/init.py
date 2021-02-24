import logutils


def main():
    dirs = logutils.get_log_dirs()
    
    # concatenate the log files into one large file for each type
    for folder in dirs:
        logutils.gunzip_logs(folder)
        logutils.concatenate_logs(folder, logutils.TENANT_LOG_FILES, logutils.TENANT_LOG_FILE)

# Start program
if __name__ == "__main__":
    main()
