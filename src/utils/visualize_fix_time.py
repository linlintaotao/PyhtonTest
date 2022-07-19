import os
import sys

from datetime import datetime
import matplotlib.dates as md
import matplotlib.pyplot as plt
import time
import dateutil
import numpy as np


def test_txt(file_p):
    float_times = 0
    fix_times = 0
    pre_timestamp = None
    float_not_fix_time = 0
    float_not_single_time = 0
    only_single_time = 0
    with open(file_p) as f:
        all_lines = f.readlines()
        line_num = all_lines.__len__()
        for i in range(line_num):
            if not all_lines[i].__contains__('TIME,'):
                continue
            timestamp = all_lines[i].split(',')[2]
            if all_lines[i].__contains__('status:5,'):
                float_times = float_times + 1
                if i + 1 < line_num:
                    if not all_lines[i + 1].__contains__('status:4,' + timestamp):
                        float_not_fix_time = float_not_fix_time + 1
                    else:
                        fix_times = fix_times + 1
                if i - 1 >= 0:
                    if not all_lines[i - 1].__contains__('status:1,' + timestamp):
                        # print('not 5 followed 1', i)
                        float_not_single_time = float_not_single_time + 1
            elif all_lines[i].__contains__('status:1,'):
                if i + 1 < line_num:
                    if (not all_lines[i + 1].__contains__('status:5,' + timestamp)) and (
                            not all_lines[i + 1].__contains__('status:4,' + timestamp)):
                        print('not 5 or 4 followed 1', i)
                        only_single_time = only_single_time + 1

    return [float_times, fix_times, float_not_fix_time, float_not_single_time, only_single_time]


def analysisLogFile(filePath, resultPath):
    fix_times = {}
    float_times = {}
    single_times = {}
    single_outlier = 0
    fix_outlier = 0
    cold_reset_times = 0
    warm_reset_times = 0
    fix_time_threshold = 40
    single_time_threshold = 25
    time_threshold = 3
    new_log = filePath.replace('.log', '_new.dat')
    valid_info_file = open(new_log, 'w')
    version = ''
    ackIsOK = True
    with open(filePath, 'r', errors='ignore') as log_file:
        lines = log_file.readlines()
        cold_reset = False
        for line in lines:
            if version == '':
                if line.__contains__('VERSION:RTK'):
                    version = line[12:]
            if not line.__contains__("TIME,"):
                continue
            if line.__contains__('status:4') and not cold_reset:
                elements = line.split(',')
                if elements.__len__() >= 4:
                    cur_time = int(float(elements[2]))
                    fix_time = round(float(elements[3]), 1)
                    valid_info_file.write(line)
                    fix_times[cur_time] = fix_time
                    if fix_time > fix_time_threshold:
                        fix_outlier = fix_outlier + 1

            elif line.__contains__('status:1') and not cold_reset:
                ackIsOK = True
                elements = line.split(',')
                if elements.__len__() >= 4:
                    cur_time = int(float(elements[2]))
                    single_time = round(float(elements[3]), 1)
                    if not single_times.keys().__contains__(cur_time) and single_time > 1:
                        valid_info_file.write(line)
                        single_times[cur_time] = single_time

            elif line.__contains__('status:5') and not cold_reset:
                elements = line.split(',')
                if elements.__len__() >= 4:
                    cur_time = int(float(elements[2]))
                    float_time = round(float(elements[3]), 1)
                    if float_time > 15:
                        print('time > 15', cur_time)
                    if not float_times.keys().__contains__(cur_time):
                        valid_info_file.write(line)
                        float_times[cur_time] = float_time

            elif line.__contains__('cold reset'):
                cold_reset_times = cold_reset_times + 1
                cold_reset = True
                valid_info_file.write(line)
                if not ackIsOK:
                    single_outlier += 1
                ackIsOK = False

            elif line.__contains__('warm reset'):
                warm_reset_times = warm_reset_times + 1
                if cold_reset:
                    cold_reset = False
                if not ackIsOK:
                    single_outlier += 1
                ackIsOK = False
                valid_info_file.write(line)

    valid_info_file.close()
    times = test_txt(new_log)
    common = list(fix_times.keys() & float_times.keys() & single_times.keys())
    # common = single_times.keys()
    dates = [datetime.fromtimestamp(s) for s in sorted(common)]
    single_ys = [single_times[s] for s in sorted(common)]
    fix_ys = [fix_times[s] for s in sorted(common)]
    float_ys = [float_times[s] for s in sorted(common)]
    size = dates.__len__()
    resultInfo = ""
    if size > 0:
        resultInfo = f'a.Total:%s,WARM_RESET Times:%s,COLD_RESET Times:%s\n' \
                     f'b.ACK Failed Times:%s(%s%%)\n' \
                     f'c.Fixed used time > %sS times: %s(%s%%)\n' \
                     f'd.Float Times:%s;Fixed Times:%s(used time in %s min)\n' \
                     f'e.Not Fixed Times:%s,direct Float Times:%s,Only Single Times:%s\n' % \
                     (size, warm_reset_times, cold_reset_times, single_outlier,
                      round(100.0 * single_outlier / size, 2), fix_time_threshold, fix_outlier,
                      round(100.0 * fix_outlier / size, 2),
                      str(times[0]), str(times[1]), time_threshold, times[2], times[3], times[4])

    x = np.array(['Total', 'WarmReset', 'ColdReset', 'ACK Filed', 'FixedTimes', 'Not Fixed', 'Only Single'])
    y = np.array([size, warm_reset_times, cold_reset_times, single_outlier, times[1], times[2], times[4]])
    file_n = os.path.basename(filePath)
    fig, ax = plt.subplots(figsize=[10, 8])
    ax_pic = plt.subplot(211)
    plt.title(file_n + '\n' + version)
    ax_pic.grid(axis='y')
    ax_pic.set_xlabel('(HHMMSS)' + str(dates[0]) + '~' + str(dates[-1]))
    ax_pic.set_ylabel('time elapse (s)')
    ax_pic.plot(dates, fix_ys, "o-", label='fixed', color='green')
    ax_pic.plot(dates, float_ys, "o-", label='float', color='blue')
    ax_pic.plot(dates, single_ys, "o-", label='single', color='red')
    ax_pic.legend()

    # plt.xticks(rotation=20)
    ax_text = plt.subplot(212)
    ax_text.bar(x, y)
    plt.savefig(resultPath + "/" + file_n + '.png')
    plt.close()
    return resultInfo


if __name__ == '__main__':
    pass
