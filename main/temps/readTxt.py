import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import operator


projectDir = os.path.dirname(os.path.realpath(__file__))

print(projectDir)

# set up time for column name
col_name = []
for h in range (24):
    for m in range (60):
        if (m % 10 == 0):
            if (m == 0):
                col_name.append(str(h) + ':00')
            else:
                col_name.append( str(h) + ':' + str(m) )


#read file
data_row = []
list_files = os.listdir(projectDir + '/txt/')

#sort date
list_files.sort()
#remove .DS file
list_files = list_files[1:]

df = pd.DataFrame([], columns = col_name).rename_axis('Date')

for file in list_files:

    #get date and time from file name
    date = file.split("-")[0]
    time = file.split("-")[1]
    time = time[:2] + ":" + time[2:]

    index_start_time = col_name.index(time) + 1

    row = []
    with open(projectDir+'/txt/'+file, 'r') as filehandle:
        for line in filehandle:
            # remove linebreak which is the last character of the string
            currentPlace = line[:-1]

            # add item to the list
            row.append(int(currentPlace))

        # find how many of period is
        index_end_time = index_start_time + len(row)

        # create dataframe with time
        col_name_selected = col_name[index_start_time:index_end_time]
        temp_df = pd.DataFrame([row], columns = col_name_selected, index = [date]).rename_axis('Date')

        # append to main df
        df = df.append(temp_df)

    #remove txt file
    os.remove(projectDir+'/txt/'+file)

print(df)

# update csv file

# import previous csv file
list_csv = os.listdir(projectDir + '/csv/')

# check exiting file
if len(list_csv) > 0:
    old_df = pd.read_csv(projectDir + "/csv/db.csv")
    old_df = old_df.set_index('Date')
else:
    old_df = pd.DataFrame([], columns=col_name).rename_axis('Date')

updated_df = pd.concat([old_df, df])
updated_df = updated_df.groupby(level=0).sum()

print(updated_df)

updated_df.to_csv(projectDir + '/csv/db.csv')
