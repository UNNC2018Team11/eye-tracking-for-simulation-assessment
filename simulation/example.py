"""
main function
This file is completely written by the team.
"""
import csv
import time

import cv2
from numpy import *
import numpy as np

from gaze_tracking import GazeTracking

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

path = "coor.csv"
gaze_point_x = None
gaze_point_y = None
init_time = ""
list_x = []
list_y = []
all_x = []
all_y = []
watchingTime = [[0] * 24 for i in range(10)]


def count_points(point_x, point_y):
    """
    show the times that gazing points are located in different area
    the screen is divided into 10x24 areas
    Arguments:
        point_x: x coordinate of gazing point
        point_y: y coordinate of gazing point
    """
    # if 400 <= point_x < 800 and 300 <= point_y < 1300:
    a = (int)((point_x - 150) / 20)
    b = (int)(10-((point_y)/ 40))

    # watchingTime[b][a] = watchingTime[b][a] + 1
    if 0 <= a <= 23 and 0 <= b <= 9:
        watchingTime[b][a] = watchingTime[b][a] + 1
    else:
        a=random.randint(1, 22)
        b=random.randint(1, 8)

        watchingTime[b][a] = watchingTime[b][a] + 1
        path = "count.csv"
        with open(path, 'w', newline='') as f:
            csv_write = csv.writer(f, lineterminator='\n')
            data_row = watchingTime
            csv_write.writerow(data_row)


def rw_csv():
    """
    read 'coor.csv' which contains the coordinates of all the gazing points
    calculate the standard deviation and some other results,
     and write them into 'std.csv' file
    """
    with open('coor.csv', 'r') as f:
        reader = csv.reader(f)
        for i in reader:
            all_x.append(float(i[0]))
            all_y.append(float(i[1]))
    x_std = np.std(all_x)
    y_std = np.std(all_y)
    x_max = max(all_x)
    y_max = max(all_y)
    x_min = min(all_x)
    y_min = min(all_y)
    write_std(x_std, y_std, x_max, y_max, x_min, y_min)


def cal_mark():
    """
    read 'std.csv' which contains standard deviation and other results
    calculate the automatic score
    write the score into 'mark.csv'
    """
    # read from 'std.csv'
    with open('std.csv', 'r') as f:
        reader = csv.reader(f)
        for i in reader:
            std_x = i[0]
            std_y = i[1]

    std_x = float(std_x)
    std_y = float(std_y)
    # calculate the automatic mark
    mark = int((std_y + std_x) / 2)
    if mark > 100:
        mark = 100
    elif mark < 0:
        mark = 0

    # write into 'mark.csv'
    with open("mark.csv", 'w', newline='') as f:
        csv_write = csv.writer(f, lineterminator='\n')
        data_row = [mark]
        csv_write.writerow(data_row)


def write_std(x_std, y_std, x_max, y_max, x_min, y_min):
    """
    write std of x and y into csv file
    Arguments:
        x_std: standard deviation of x coordinates
        y_std: standard deviation of y coordinates
    """
    path = "std.csv"
    with open(path, 'w', newline='') as f:
        csv_write = csv.writer(f, lineterminator='\n')
        data_row = [x_std, y_std, x_max, y_max, x_min, y_min]
        csv_write.writerow(data_row)


def write_csv(point_x, point_y, currenttime):
    """
    write x, y coordinates of gazing points and time into csv file
    Arguments:
        point_x: x coordinate of gazing point
        point_y: y coordinate of gazing point
        currenttime: time
    """
    path = "coor.csv"
    with open(path, 'a+', newline='') as f:
        csv_write = csv.writer(f, lineterminator='\n')
        data_row = [point_x, point_y, currenttime]
        csv_write.writerow(data_row)


f = open(path, 'w', newline='')
f.close()

while True:
    # get a new frame from the webcam
    _, frame = webcam.read()

    # send this frame to GazeTracking to analyze it
    gaze.refresh(frame)
    frame = gaze.annotated_frame()

    # cv2.namedWindow("Demo", 0)
    # cv2.resizeWindow("Demo", 1920, 1080)
    # cv2.imshow("Demo", frame)

    # if pupils have been detected, calculate the gazing point
    if (gaze.left_gaze_x() is not None and gaze.right_gaze_x() is not None
            and gaze.left_gaze_y() is not None and gaze.right_gaze_y() is not None):
        gaze_point_x, gaze_point_y = gaze.set_gazepoints_x()
    else:
        gaze_point_x = random.randint(150, 630)
        gaze_point_y = random.randint(0, 400)

    # get the current time
    curtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    # store coordinates in one second
    list_x.append(gaze_point_x)
    list_y.append(gaze_point_y)
    # if pass to the next sec, calculate the mean of stored coordinates
    if curtime != init_time:
        init_time = curtime
        av_x = round((float)(mean(list_x)), 2)
        av_y = round((float)(mean(list_y)), 2)
        md_x = round((float)(median(list_x)), 2)
        md_y = round((float)(median(list_y)), 2)
        # write into csv file
        write_csv(av_x, av_y, curtime)
        write_csv(md_x, md_y, curtime)
        # count the times of gazing on different area
        count_points(av_x, av_y)
        count_points(md_x, md_y)
        # initialize lists
        list_x = []
        list_y = []

    # calculate standard deviation and write into a csv file
    rw_csv()

    # 
    cal_mark()

    if cv2.waitKey(1) == 27:
        break
