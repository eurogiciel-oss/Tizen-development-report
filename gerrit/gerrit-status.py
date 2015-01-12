#!/usr/bin/python

from subprocess import Popen, PIPE
import os
import glob
import errno
import json
from Queue import Queue
from threading import Thread
import time
from datetime import date, timedelta
import argparse
import calendar
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import numpy as np
import re

thread_max = 5
# Number of seconds in an hour
hour_s = 60 * 60
# Number of seconds in a day
day_s = 24 * hour_s
# Number of seconds in a week
week_s = 7 * day_s
# Weeks number for moving average
average_week_n = 5
result_csv = 'result.csv'

def mkdir(directory):
    '''
    Creates a directory if doesn't exist
    '''

    try:
        os.makedirs(directory)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def query_gerrit(project, status):
    '''
    Write all the merged review for a given project in a file.
    '''

    start = 0
    row_count = 0
    output = ''
    review_directory = 'data-' + status
    mkdir(review_directory)
    project_filename = os.path.join(review_directory, project.replace('/', '.')) + ".json"

    # Remove the old file if it exists
    if os.path.isfile(project_filename):
        os.remove(project_filename)

    # Gerrit only returns the first 500 results to our queries. To get the rest of the results, we need to launch a new query with an offset.
    while(start >= 0):
        output = output + Popen(["ssh", "review.tizen.org", "gerrit", "query", "--comments", "--format=JSON", "--start={} project:{} status:{}".format(start, project, status)], stdout=PIPE).communicate()[0]
        query_info = output.split('\n')[-2]

        # This hasn't been tested yet !!!
        if query_info.count("resumeSortKey"):
            print "More than 500 results !!!"
            start += 501
        else:
            start = -1

        try:
            decoded = json.loads(query_info)
            row_count = row_count + decoded['rowCount']
        except (ValueError, KeyError, TypeError):
            print "JSON format error for %s" % project
            print output

        if row_count:
            f = open(project_filename, 'a')
            output = re.sub(".*"+",\"runTimeMilliseconds\":"+".*\n?","",output)
            f.write(output)
            f.close()

def get_reviews(queue):
    
    while 1:
        project = queue.get()
        query_gerrit(project, 'merged')
        query_gerrit(project, 'open')
        queue.task_done()

def review_info(json_data):
    try:
        decoded = json.loads(json_data)
        project = decoded['project']
        upload_date = decoded['createdOn']
        count = -1

        max_count = - json_data.count('\"},\"message\":\"')
        while not decoded['comments'][count]['message'].count('Change has been successfully merged into the git repository.') \
                and not decoded['comments'][count]['message'].count('is still under review in gerrit. After reviewer accpet this commit, it will be submitted to OBS corresponding project.') \
                and not decoded['comments'][count]['message'].count('Change has been successfully pushed.'):
            count = count -1
            if count < max_count:
                break
        if count < max_count:
            merge_date = decoded['lastUpdated']
        else:
            merge_date = decoded['comments'][count]['timestamp']
    except (ValueError, KeyError, TypeError):
        print "JSON format error in \"review_info\""

    return [upload_date, merge_date]

def last_patch_set(json_data):

    project = ""
    patch_set = 1

    try:
        decoded = json.loads(json_data)
        project = decoded['project']
        count = -1

        max_count = - json_data.count('\"},\"message\":\"')
        while not decoded['comments'][count]['message'].count('Uploaded patch set'):
            count = count -1
            if count < max_count:
                break

        if count >= max_count:
            message = decoded['comments'][count]['message']
            patch_set = int(re.findall(r'\b\d+\b', message)[0])

    except (ValueError, KeyError, TypeError):
        print "JSON format error in \"last_patch_set\""

    return patch_set

def updated_date(json_data):

    project = ""
    updated_date = -1

    try:
        decoded = json.loads(json_data)
        updated_date = decoded['lastUpdated']

    except (ValueError, KeyError, TypeError):
        print "JSON format error in \"updated_date\""

    return updated_date

def get_review_number(json_data):

    try:
        decoded = json.loads(json_data)
        number = int(decoded['number'])

    except (ValueError, KeyError, TypeError):
        print "JSON format error in \"get_review_number\""

    return number

def display(array):
    total_review = 0
    total_merge = 0
    for i in array[0]:
        print str(array[0][i]) + '\t' + array[1][i] + '\t' + str(array[2][i]) + '\t' + str(array[3][i]) + '\t' + str(array[4][i]) + '\t' + str(array[5][i]) + '\t' + str(array[6][i]) + '\t' + str(array[7][i])
        total_review = total_review + array[2][i]
        total_merge = total_merge + array[4][i]
    print
    print 'total_review = ' + str(total_review)
    print 'total_merge = ' + str(total_merge)


# data: a list of review dates
# index: current position in data
# date: current date
# date_max: last date
# result: the array tha contains the results
def week_count(data, index, date, date_max, result):
    count = 0
    if date < date_max:
        while data[index] < date:
            count = count + 1
            if index + 1 < len(data):
                index = index +1
            else:
                break
        result.append(count)
        week_count(data, index, date + week_s, date_max, result)
    else:
        return

# data: a list of review and merge dates
# index: current position in data
# date: current date
# date_max: last date
# result: the array tha contains the results
def merge_time(data, index, date, date_max, result):
    week_average = 0
    count = 0
    if date < date_max:
        while data[index][1] < date:
            count = count + 1
            week_average = week_average + data[index][1] - data[index][0]
            if index + 1 < len(data):
                index = index +1
            else:
                break
        if count:
            result.append((week_average / count) / hour_s)
        else:
            result.append(0)
        merge_time(data, index, date + week_s, date_max, result)
    else:
        return

def average(data, week_n):
    length = len(data)
    i = 0
    result = []
    while i < length:
        if i - (week_n - 1) < 0:
            result.append(-1)
        else:
            j = week_n - 1
            result.append(data[i])
            while j != 0:
                result[i] = result[i] + data[i - j]
                j = j -1
            result[i] = result[i] / week_n
        i = i + 1
    return result

def create_array(data):
    '''
    Creates an array containing all the processed data.
    '''

    reviews = []
    merges = []
    results = []

    # Put upload dates and merge dates in two different arrays
    for element in data:
        reviews.append(element[0])
        merges.append(element[1])

    # Sort the couples (upload date; merge date) by merge date
    sorted_data = sorted(data, key=lambda element: element[1])
    reviews.sort()
    merges.sort()

    # The first (merged) review was uplodaed at 2012-08-09 04:18:48 so we begin to count the weeks at the begining of that week.
    first_date = calendar.timegm(time.strptime("2012-08-06", "%Y-%m-%d"))
    last_date = merges[-1]

    # Number of weeks since first review
    week_n = ((last_date - first_date) / week_s)
    # Add the weeks number in the results array
    results.append([i for i in range(week_n)])

    # Add dates in the results array
    times = []
    dates = []
    for week in results[0]:
        times.append(first_date + week * week_s)
        dates.append(time.strftime('%Y-%m-%d', time.gmtime(first_date + week * week_s)))
    results.append(dates)

    # Add the number of uploaded reviews per week
    reviews_n = []
    week_count(reviews, 0, first_date + week_s, first_date + (week_n + 1) * week_s, reviews_n)
    results.append(reviews_n)

    # Add the average number of uploaded reviews per week
    results.append(average(reviews_n, average_week_n))

    # Add the number of uploaded reviews per week
    merge_n = []
    week_count(merges, 0, first_date + week_s, first_date + (week_n + 1) * week_s, merge_n)
    results.append(merge_n)

    # Add the average number of merged reviews per week
    results.append(average(merge_n, average_week_n))

    # Add the time to merge a review
    merge_t = []
    merge_time(sorted_data, 0, first_date + week_s, first_date + (week_n + 1) * week_s, merge_t)
    results.append(merge_t)

    # Add the averagetime to merge a review
    results.append(average(merge_t, average_week_n))

    return results

def save_csv(array, csv_file):
    '''
    Save the array containing the process data in a csv file.
    '''

    with open(csv_file, 'w') as outfile:
        for i in array[0]:
            outfile.write(str(array[0][i]) + ',' + array[1][i] + ',' + str(array[2][i]) + ',' + str(array[3][i]) + ',' + str(array[4][i]) + ',' + str(array[5][i]) + ',' + str(array[6][i]) + ',' + str(array[7][i]) + '\n')

def hours_to_days(x, pos):
    'The two args are the value and tick position'
    return '%.1f' % (x/24)

def create_chart(array, weeks):

    # Chart: reviews and merges per week
    #plt.figure()
    #plt.xlabel('Weeks (latest = 2014-12-15)')
    #plt.ylabel('Gerrit reviews')
    #plt.title('Per week new and merged review')
    #x_series = array[0][-weeks:]
    #y_series_reviews_n = array[2][-weeks:]
    #y_series_merge_n = array[4][-weeks:]
    #plt.plot(x_series, y_series_reviews_n, label = 'New reviews')
    #plt.plot(x_series, y_series_merge_n, label = 'Merged reviews')
    #plt.legend(loc="upper left")
    #plt.savefig("reviews-per-week.png")

    xlabel = 'Weeks (latest = %s)' % get_date(-7)

    # Chart: average reviews and merges per week
    plt.clf()
    plt.figure()
    plt.xlabel(xlabel)
    plt.ylabel('Gerrit reviews')
    plt.title('Moving average of new and merged review (5 weeks)')
    x_series = array[0][-weeks:]
    y_series_average_reviews_n = array[3][-weeks:]
    y_series_average_merge_n = array[5][-weeks:]
    plt.plot(x_series, y_series_average_reviews_n, label = 'New reviews ')
    plt.plot(x_series, y_series_average_merge_n, label = 'Merged reviews')
    plt.legend(loc="upper left")
    plt.savefig("average-reviews-per-week.png")

    # Chart: time and average time to merge a commit per week
    formatter = FuncFormatter(hours_to_days)
    plt.clf()
    plt.figure()
    fig, ax = plt.subplots()
    ax.yaxis.pan(24)
    ax.yaxis.set_major_formatter(formatter)
    plt.xlabel(xlabel)
    plt.ylabel('Days')
    plt.title('Weekly average of time needed to review and merge a commit')
    x_series = array[0][-weeks:]
    #y_series_time = array[6][-weeks:]
    y_series_average_time = array[7][-weeks:]
    #plt.plot(x_series, y_series_time, label = 'Time to merge')
    plt.plot(x_series, y_series_average_time, label = 'Moving average of time to merge (5 weeks)')
    plt.legend(loc="upper left")
    plt.savefig("merge-time.png")

def average_basic(data, data_n):

    i = data_n - 1
    result = []
    while i < len(data):
        j = 0
        val = 0
        while j < data_n:
            val = val + data[i - j]
            j = j + 1
        result.append(val / data_n)
        i = i + 1
    return result

def get_date(delta):
    return (date.today() + timedelta(delta)).strftime('%y-%m-%d')

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    args = parser.parse_args()

    # Fetch all the merged review and save them (one file per project)
    if args.command == 'fetch':

        # Get the list of projects
        output = Popen(["ssh", "review.tizen.org", "gerrit", "ls-projects"], stdout=PIPE).communicate()[0]
        projects = output.split('\n')

        # Create the queue and the threads
        queue = Queue(1000)
        for thread in range(thread_max):
            worker = Thread(target=get_reviews, args=(queue,))
            worker.setDaemon(True)
            worker.start()

        # Put the project in the queue
        for project in projects:
            if project:
                queue.put(project)

        # Wait for the queue to be empty
        queue.join

    elif args.command == 'process':

        review_info_list = []
        for json_file in glob.glob(os.path.join('data-merged', '*.json')):
            f = open(json_file, 'r')
            review_list = f.read().split('\n')
            for element in review_list:
                if element:
                    if not element.count('runTimeMilliseconds'):
                        review_info_list.append(review_info(element))
            f.close()

        result = create_array(review_info_list)
        display(result)
        save_csv(result, result_csv)
        create_chart(result, 26)

        ######################################################
        # Reviews age
        ######################################################

        f = open('reviews-age.tmp', 'r')
        reviews = f.read().split(' ')
        reviews_list = []
        for review in reviews:
            if review:
                reviews_list.append(int(review))

        plt.clf()
        plt.figure()
        x = np.arange(6)
        fig, ax = plt.subplots()
        plt.xlabel('Time')
        plt.ylabel('Reviews')
        title = 'Age of reviews in Gerrit based on the last update date (%s)' % get_date(0)
        plt.title(title)
        plt.bar(x, reviews_list)
        plt.xticks(x + 0.5,  ('2 days', '<1 week', '<2 weeks', '<1 month', '<3 months', '3+ months'))
        plt.savefig("age-of-reviews.png")


        ######################################################
        # Reviews status
        ######################################################
        
        f = open('reviews-status.tmp', 'r')
        count = f.read().split('\n')
        count_list = []
        for line in count:
            if count:
                count_list.append(line)

        to_merge = map(int, count_list[0].split(' '))
        to_review = map(int, count_list[1].split(' '))
        to_verify = map(int, count_list[2].split(' '))
        to_review_and_verify = map(int, count_list[3].split(' '))
        invalid = map(int, count_list[4].split(' '))
        total = map(int, count_list[5].split(' '))

        to_merge_average = average_basic(to_merge, 5)
        to_review_average = average_basic(to_review, 5)
        to_verify_average = average_basic(to_verify, 5)
        to_review_average_and_verify = average_basic(to_review_and_verify, 5)
        invalid_average = average_basic(invalid, 5)
        total_average = average_basic(total, 5)

        plt.clf()
        plt.figure()
        xlabel = 'Weeks (latest = %s)' % get_date(0)
        plt.xlabel(xlabel)
        plt.ylabel('Gerrit reviews')
        plt.title('Average number of commits waiting to be reviewed (5 weeks average)')
        x_series = [i for i in range(len(to_merge_average))]
        y_series_to_merge_average = to_merge_average
        y_series_to_review_average = to_review_average
        y_series_to_verify_average = to_verify_average
        y_series_to_review_average_and_verify = to_review_average_and_verify
        y_series_invalid_average = invalid_average
        y_series_total_average = total_average
        plt.plot(x_series, y_series_to_merge_average, label = 'To merge')
        plt.plot(x_series, y_series_to_review_average, label = 'To review')
        plt.plot(x_series, y_series_to_verify_average, label = 'To verify')
        plt.plot(x_series, y_series_to_review_average_and_verify, label = 'To review and verify')
        plt.plot(x_series, y_series_invalid_average, label = 'Invalid')
        plt.plot(x_series, y_series_total_average, label = 'TOTAL')
        plt.legend(loc="upper left")
        plt.savefig("average-being-reviewed-per-week.png")

    elif args.command == 'abandon':

        review_info_list = []
        for json_file in glob.glob(os.path.join('data-open', '*.json')):
            f = open(json_file, 'r')
            review_list = f.read().split('\n')
            for element in review_list:
                if element:
                    if not element.count('runTimeMilliseconds'):
                        updated = updated_date(element)
                        if updated is -1:
                            print "ERROR: wrong update date"
                        elif updated < calendar.timegm(time.gmtime()) - 90 * day_s:
                            # Abandon the patch
                            patch_set = last_patch_set(element)
                            review_number = get_review_number(element)
                            print 'https://review.tizen.org/gerrit/#/c/%i' % review_number
                            command = 'gerrit review --message "To\ be\ abandonned\ because\ last\ update\ was\ made\ more\ than\ 90\ days\ ago." --abandon %i,%i' % (review_number, patch_set)
                            Popen(["ssh", "review.tizen.org", command], stdout=PIPE).communicate()[0]
            f.close()

    else:
        print 'Unknown command'

if __name__ == '__main__':
    main()
