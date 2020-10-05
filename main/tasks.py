import string

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from celery import shared_task
import os
import pandas as pd
from datetime import datetime


@shared_task
# def create_random_user_accounts(total):
def create_db_csv():
    projectDir = os.path.dirname(os.path.realpath(__file__))

    ####### create temp file for show processing status############
    with open(projectDir + '/temps/isProcessing', 'w') as filehandle:
        filehandle.write('isProcessing')
        print("======= temp file is exported =======")
    ###############################################################

    vidDir = projectDir.replace("/main", "")
    vidDir = vidDir + '/media/videos'

    # scan footage file
    list_files = os.listdir(vidDir)

    # run openCV for each file
    for file in list_files:
        os.system(
            'time python "' + projectDir + '/crowd_counting.py" --input "' + vidDir + '/' + file + '" --display 1')

    # set up time for column name
    col_name = []
    for h in range(24):
        for m in range(60):
            if (m % 10 == 0):
                if (m == 0):
                    col_name.append(str(h) + ':00')
                else:
                    col_name.append(str(h) + ':' + str(m))

    ######## generated csv file #############
    # read file

    data_row = []
    list_txt_files = os.listdir(projectDir + '/txt/')

    print(list_txt_files)

    # sort date
    # list_txt_files.sort()

    df = pd.DataFrame([], columns=col_name).rename_axis('Date')

    for file in list_txt_files:

        # get date and time from file name
        date = datetime.strptime(file.split("-")[0], '%d%b%Y')
        time = file.split("-")[1]
        time = time[:2] + ":" + time[2:]

        index_start_time = col_name.index(time) + 1

        row = []
        with open(projectDir + '/txt/' + file, 'r') as filehandle:
            for line in filehandle:
                # remove linebreak which is the last character of the string
                currentPlace = line[:-1]

                # add item to the list
                row.append(int(currentPlace))

            # find how many of period is
            index_end_time = index_start_time + len(row)

            # create dataframe with time
            col_name_selected = col_name[index_start_time:index_end_time]
            temp_df = pd.DataFrame([row], columns=col_name_selected, index=[date]).rename_axis('Date')

            # append to main df
            df = df.append(temp_df)

        # remove txt file
        os.remove(projectDir + '/txt/' + file)

    print(df)

    # update csv file

    # import previous csv file
    list_csv = os.listdir(projectDir + '/csv/')

    # check exiting file
    if len(list_csv) > 0:
        old_df = pd.read_csv(projectDir + "/csv/db.csv")
        old_df = old_df.set_index('Date')
        old_df.index = pd.to_datetime(old_df.index)

    else:
        old_df = pd.DataFrame([], columns=col_name).rename_axis('Date')
        old_df.index = pd.to_datetime(old_df.index)

    updated_df = pd.concat([old_df, df])
    updated_df = updated_df.groupby(level=0).sum()

    updated_df.to_csv(projectDir + '/csv/db.csv')

    print(updated_df)

    print('Footage reading complete')

    ################# delete temp file to show the processing is completed ################
    os.remove(projectDir + '/temps/isProcessing')
    print('Temp file is deleted')
    #######################################################################################

    return 'done'
