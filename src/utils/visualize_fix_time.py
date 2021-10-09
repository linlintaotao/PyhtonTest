import os
import sys

from datetime import datetime
import matplotlib.dates as md
import matplotlib.pyplot as plt
import time
import dateutil

print('#' * 80)
print(" input the fix_time log file ")
print('#' * 80)


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


if __name__ == '__main__':
    if sys.argv.__len__() != 2:
        print('Please assign the log file')
        exit(-1)

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
    new_log = sys.argv[1].replace('.log', '_new.log')
    nmea_log = sys.argv[1].replace('.log', '_fix.nmea')
    valid_info_file = open(new_log, 'w')
    nmea_info_file = open(nmea_log, 'w')
    version = 'unknown'
    with open(sys.argv[1], 'r', errors='ignore') as log_file:
        lines = log_file.readlines()
        cold_reset = False
        for line in lines:
            if line.__contains__('GGA') and line.__contains__('E,4'):
                nmea_info_file.write(line)
            if version == 'unknown':
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
                elements = line.split(',')
                if elements.__len__() >= 4:
                    cur_time = int(float(elements[2]))
                    single_time = round(float(elements[3]), 1)
                    if not single_times.keys().__contains__(cur_time) and single_time > 2:
                        valid_info_file.write(line)
                        single_times[cur_time] = single_time
                        if single_time > single_time_threshold:
                            single_outlier = single_outlier + 1

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

            elif line.__contains__('warm reset'):
                warm_reset_times = warm_reset_times + 1
                if cold_reset:
                    cold_reset = False
                valid_info_file.write(line)

    valid_info_file.close()
    nmea_info_file.close()
    times = test_txt(new_log)

    common = fix_times.keys() & float_times.keys() & single_times.keys()
    # common = single_times.keys()
    dates = [datetime.fromtimestamp(s) for s in sorted(common)]
    single_ys = [single_times[s] for s in sorted(common)]
    fix_ys = [fix_times[s] for s in sorted(common)]
    float_ys = [float_times[s] for s in sorted(common)]

    # print('collect valid times: ', dates.__len__(), 'try warm_reset times:', warm_reset_times, 'try cold_reset times', cold_reset_times)
    # print('warm reset config exception', single_outlier, 'ratio: ', single_outlier/dates.__len__())
    # print('warm reset fix exception', fix_outlier, 'ratio: ', fix_outlier/dates.__len__())
    print(r'a.共统计有效次数：' + str(dates.__len__()) + r'，尝试发送warm reset次数：' + str(
        warm_reset_times) + r'，尝试发送cold reset次数：' + str(cold_reset_times))
    print(r'b.由于检测指令ACK失败导致config 时间过长或者重启次数：' + str(single_outlier) + r'，占比：' + str(
        round(100.0 * single_outlier / dates.__len__(), 2)) + '%')
    print(r'c.固定时间超过' + str(fix_time_threshold) + r's的次数：' + str(fix_outlier) + r'，占比：' + str(
        round(100.0 * fix_outlier / dates.__len__(), 2)) + '%')
    print(r'd.共检测到浮点解次数：' + str(times[0]) + r'，检测到固定解次数：' + str(times[1]) + r'(发送warm reset' + str(
        time_threshold) + r'min内)' +
          r'，浮点但未固定次数：' + str(times[2]) + r'，未经单点解状态进入浮点次数：' + str(times[3]) + r'，只有单点解次数：' + str(times[4]))

    file_n = os.path.basename(sys.argv[1])
    plt.title(file_n + '\n' + version)
    plt.grid(axis='y')
    plt.xlabel('(HHMMSS)' + str(dates[0]) + '~' + str(dates[-1]))
    plt.ylabel('time elapse (s)')
    plt.xticks(rotation=20)
    ax = plt.gca()
    xtick = []
    i = 0
    xtick_interval = round(dates.__len__() / 20.0)
    while i < dates.__len__():
        xtick.append(dates[i])
        i += xtick_interval
    ax.set_xticks(xtick)
    xfmt = md.DateFormatter('%H%M%S')
    ax.xaxis.set_major_formatter(xfmt)

    plt.plot(dates, fix_ys, "o-", label='fixed', color='green')
    plt.plot(dates, float_ys, "o-", label='float', color='blue')
    plt.plot(dates, single_ys, "o-", label='single', color='red')
    plt.legend()
    plt.savefig(sys.argv[1] + '.png')
    plt.show()
