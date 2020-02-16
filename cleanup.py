import os
import sys
import shutil
import datetime as dt
from datetime import datetime

"""Cleanup old files and folders

This script is made to remove files and folders, older then a specified amount of days.
Just provide a path and optional arguments, to clean your folders.

# Usage
$ python3 cleanup.py [OPTIONS] PATH

Hint: You may use this script as cron script. Just set it to run once a day, per path.

# Options
    --dryrun                    Show what files and/or folders would be deleted without deleting them. (Default: False)
    --files(=Yes|No)            Remove files. You may use this option without a value to activate file removing
                                or use "Yes" to activate or "No" to deactivate file removing. (Default: Yes)
    --files_after=NUM           Max age of files in days, when they will be removed. (Default: 30)
    --folders(=Yes|No)          Remove folders. You may use this option without a value to activate folder removing
                                or use "Yes" to activate or "No" to deactivate folder removing. (Default: No)
    --folders_after=NUM         Max age of folders in days, when they will be removed. (Default: 10)


Author: Ralph Dittrich <dittrich.ralph@lupuscoding.de>
Version: 1.0.0
"""

def get_time_before(days=30):
    """Get datetime before x days

    :param days: Days before today
    :type days: int
    :return: datetime object for today - x days
    :rtype: datetime
    """
    dtn = datetime.now()
    dstr = str(dtn.year) + '-' + str(dtn.month) + '-' + str(dtn.day) + ' 23:59:59'
    rm_dt = datetime.strptime(dstr, "%Y-%m-%d %H:%M:%S")
    rm_dt += dt.timedelta(days=(days*-1))
    return rm_dt

def get_files_by_path(path):
    """Get files by path

    :param path: Path to files
    :type path: str
    :return: List of file names
    :rtype: list
    """
    apath = os.path.abspath(path)
    rpath, subdirs, files = next(os.walk(apath))
    return files

def get_subdirs_by_path(path):
    """Get files by path

    :param path: Path to subdirs
    :type path: str
    :return: List of subdir names
    :rtype: list
    """
    apath = os.path.abspath(path)
    rpath, subdirs, files = next(os.walk(apath))
    return subdirs

def is_older(file_path, comp_time):
    """Check if file is older than compare time

    :param file_path: Path to file
    :type file_path: str
    :param comp_time: Datetime to compare with
    :type comp_time: datetime
    :return: True if file is older, otherwise False
    :rtype: bool
    """
    f_ctime = os.path.getctime(file_path)
    return f_ctime < comp_time.timestamp()

def rm_files_in(path, days, dryun=False):
    """Remove files in path, if they are older then days

    :param path: Path to files
    :type path: str
    :param days: Days in past
    :type days: int
    :return: Count of removed files
    :rtype: int
    """
    cnt = 0
    rm_time = get_time_before(days)
    for file in get_files_by_path(path):
        f_path = os.path.join(path, file)
        if not os.path.isfile(f_path):
            continue
        if not is_older(f_path, rm_time):
            continue
        if not dryun:
            print('Removing file', f_path, '...')
            os.remove(f_path)
        else:
            print('Would remove', f_path)
        cnt += 1
    return cnt

def rm_folders_in(path, days, dryrun=False):
    """Remove sub folders in path, if they are older then days

    :param path: Path to folders
    :type path: str
    :param days: Days in past
    :type days: int
    :return: Count of removed folders
    :rtype: int
    """
    cnt = 0
    rm_time = get_time_before(days)
    for dir in get_subdirs_by_path(path):
        d_path = os.path.join(path, dir)
        if not os.path.isdir(d_path):
            continue
        if not is_older(d_path, rm_time):
            continue
        if not dryrun:
            print('Removing directory', d_path, '...')
            shutil.rmtree(d_path)
        else:
            print('Would remove', d_path)
        cnt += 1
    return cnt

def __main__():
    # defaults
    path = '/tmp/'
    rm_files = True
    rm_files_after = 30
    rm_folders = False
    rm_folders_after = 10
    dryrun = False

    # options from args
    args = sys.argv[1:]
    for arg in args:
        if arg == '--':
            continue
        if arg[0:2] == '--':
            # long opt
            opt = arg[2:].split('=')
            # print('long opt found:', opt[0], '::', opt[1])
            if len(opt) > 1:
                # with value
                if opt[0] =='files':
                    rm_files = True if opt[1].lower() == 'yes' else False
                elif opt[0] == 'files_after':
                    rm_files_after = int(opt[1])
                elif opt[0] == 'folders':
                    rm_folders = True if opt[1].lower() == 'yes' else False
                elif opt[0] == 'folders_after':
                    rm_folders_after = int(opt[1])
                elif opt[0] == 'dryrun':
                    dryrun = True if opt[1].lower() == 'yes' else False
            else:
                # without value
                if opt[0] == 'files':
                    rm_files = True
                elif opt[0] == 'folders':
                    rm_folders = True
                elif opt[0] == 'dryrun':
                    dryrun = True
        if arg[0:1] == '-':
            # short opt - unsupported
            continue
        else:
            # argument
            path = arg

    print('Starting cleanup')
    print('Cleanup for base', path)
    if not os.path.isdir(path):
        raise NotADirectoryError('"' + path + '" is not a directory')
    if rm_files:
        print('Cleaning files...')
        fi_cnt = rm_files_in(path, rm_files_after, dryrun)
        print('Removed', fi_cnt, 'files')
    else:
        print('Skipping file cleanup')
    if rm_folders:
        print('Cleaning folders...')
        fo_cnt = rm_folders_in(path, rm_folders_after, dryrun)
        print('Removed', fo_cnt, 'folders')
    else:
        print('Skipping folder cleanup')
    print('Finished cleanup')

__main__()
