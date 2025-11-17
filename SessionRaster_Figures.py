# -*- coding: utf-8 -*-
"""
Add description
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os

# =============================================
# Setting plotting parameters
sizeMult = 1
saveplot = 0
savetable = 0

tickFontSize = 10
labelFontSize = 12
titleFontSize = 14

sns.set(style="whitegrid")
sns.set_context("paper")

# =============================================
# Parameters for the analysis
CRT_minimumTrials = 10
CRT_minimumTrials_TS = 3000

# ==============================================
# Initialize dataframe for all sessions across all experiments
sessions_df = pd.DataFrame()
crashed_df = pd.DataFrame()

LT_group1 = ['bella', 'kuemmel', 'renate', 'leni']
LT_group2 = ['fenja', 'granny']

order = ['marmoset', 'rhesus', 'long-tailed']

# =============================================
# Open the csv file and import the DATA
# Animals_metaData = 'Animals_metaData.csv'
result_filename = "./analysis_output/Figure_1.txt"
directory_name = Path("data/")

data_files = os.listdir(directory_name)
data_files = sorted(list(filter(lambda f: f.endswith('.csv'), data_files)))

# Cycle through the data files
for file in data_files:
    if 'CM' in file:
        print('===> Processing marmoset data: ' + file)
        # ====================================================================
        # 1) Open and process the dataframe
        csv_file = directory_name / file
        df = pd.read_csv(csv_file, low_memory=False, decimal=',')

        # Remove rows with non assigned animals, with one animal that left early, and from testing sessions
        df['monkey'] = df['monkey'].loc[~df['monkey'].isin(['nn', 'nan', 'closina', 'test'])]
        df = df.loc[df.monkey.isin(list(df['monkey'].dropna().unique()))]

        # Reformat a few column names
        df.rename(columns={"animalsExpectedPerMxbi": "animalsExpected"}, inplace=True)
        df.rename(columns={"session": "sessionNumber"}, inplace=True)
        df.rename(columns={"animal": "monkey"}, inplace=True)

        # Fix one animal's name inconsistencies
        df['animalsExpected'] = df['animalsExpected'].replace('innotiza', 'innotizia', regex=True)

        # fix date and timestamp formatting
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['timestamp'] = df['timestamp'].astype(float)

        # Convert date into day and time of each session
        df['day'] = pd.to_datetime(df['date'], format='%Y:%M:%D').dt.date
        df['time'] = pd.to_datetime(df['date'], format='%Y:%M:%D').dt.time

        # Check if exists and format the column animalsExpected
        df["animalsExpected"] = df["animalsExpected"].apply(eval)

        # reset the index
        df = df.reset_index(drop=True)

        # ====================================================================
        df['date'] = pd.to_datetime(df.date, format='%Y-%m-%d')
        df['date'] = df['date'].dt.normalize()

        for device in df.mxbi.unique():
            for date in df[df['mxbi'] == device].date.unique():

                # cycle through each session of each device
                if len(df[(df['mxbi'] == device) & (df['date'] == date)]) > 0:
                    unique_animals = df[(df['mxbi'] == device) & (df['date'] == date)]['animalsExpected'].values[0]

                    # cycle through the animals expected in the session
                    for monkey in unique_animals:
                        if monkey != 'closina':  # this makes sure that the animal closina is not considered

                            if (monkey == 'dualina') | (monkey == 'elero'):
                                group = 'A'
                            elif (monkey == 'almo') | (monkey == 'blake'):
                                group = 'B'
                            elif (monkey == 'ivvy') | (monkey == 'durin'):
                                group = 'C'
                            elif monkey == 'duchesse':
                                group = 'D'
                            elif monkey == 'cloudy':
                                group = 'E'
                            elif (monkey == 'bremer') | (monkey == 'brillux'):
                                group = 'F'
                            elif (monkey == 'intro') | (monkey == 'clia'):
                                group = 'G'
                            elif (monkey == 'wolfgang') | (monkey == 'innotizia'):
                                group = 'H'

                            # create a table (A) with the animal information
                            A = df[(df['mxbi'] == device) & (df['date'] == date) & (df['monkey'] == monkey)]

                            # create a table (B) with the session information
                            B = df[(df['mxbi'] == device) & (df['date'] == date)]

                            # Assign sessions specific parameters
                            experiment = df[(df['mxbi'] == device) & (df['date'] == date)]['experiment'].unique()[0]
                            task = df[(df['mxbi'] == device) & (df['date'] == date)]['task'].unique()[0]

                            # look for trials initiated by the animal in table A
                            if len(A[A['object'].str.contains('start')]) > 0:
                                sessionNumber = A['sessionNumber'].unique()[0]

                                # check if there is the information regarding the end and assign it as end time
                                if len(B[B['action'] == 'stop']) > 0:
                                    lastEvent = B[B['action'] == 'stop']['timestamp'].values[-1]

                                # ... or use the last trial start (from either animals) as sessions end
                                else:
                                    lastEvent = B[B['object'].str.contains('start')]['timestamp'].values[-1]

                                # Compute session duration in minutes
                                duration = lastEvent / 60000

                                # extract all trial start times
                                times = list(A[A['object'].str.contains('start')]['timestamp'] / lastEvent)

                                # calculate the median of all start trial times
                                medianTimes = np.median(list(A[A['object'].str.contains('start')]['timestamp'] / lastEvent))

                            # if there are no trials from animal A in this session
                            else:
                                # set the session duration with the session end information
                                if len(B[B['action'] == 'stop']) > 0:
                                    lastEvent = B[B['action'] == 'stop']['timestamp'].values[-1]
                                    duration = lastEvent / 60000

                                # or with the latest trial performed (by either animals)
                                elif len(B[B['object'].str.contains('start')]) > 0:
                                    lastEvent = B[B['object'].str.contains('start')]['timestamp'].values[-1]
                                    duration = lastEvent / 60000

                                # or assign nan if none of the animals interacted
                                else:
                                    duration = np.nan

                                # assign nans to missing information
                                times = np.nan
                                medianTimes = np.nan
                                sessionNumber = np.nan

                            # flag the session as crashed if there are two or more datafiles in the current day
                            crashed = (len(df[(df['mxbi'] == device) & (df['date'] == date)]['filename'].unique()) > 1)

                            # flag the session as switched (to another group) if there are other animals expected
                            switched = (len(df[(df['mxbi'] == device) &
                                              (df['date'] == date)]['animalsExpected'].astype(str).unique()) > 1)

                            sessions_df = sessions_df.append({
                                'device': device,
                                'date': date,
                                'session': sessionNumber,
                                'duration': duration,
                                'crashed': crashed,
                                'switched': switched,
                                'experiment': experiment,
                                'task': task,
                                'animal': monkey,
                                'group': group,
                                'species': 'marmoset',
                                'trials': sum(A['object'].str.contains('start')),
                                'times': times,
                                'medianTimes': medianTimes},
                                ignore_index=True)

        # sort the new dataframe and reset its index
        sessions_df = sessions_df.sort_values(by=['species', 'date'])
        sessions_df = sessions_df.reset_index(drop=True)

    if 'LT' in file:
        print('===> Processing long-tailed data:' + file)
        # ====================================================================
        # 1) Open and process the dataframe
        csv_file = directory_name / file
        df = pd.read_csv(csv_file, low_memory=False, decimal=',')

        # create animalsExpected column
        df['animalsExpected'] = np.nan
        df['animalsExpected'].loc[df['monkey'].isin(LT_group1)] = str(LT_group1)
        df['animalsExpected'].loc[df['monkey'].isin(LT_group2)] = str(LT_group2)

        # Reformat a few column names
        df.rename(columns={"session": "sessionNumber"}, inplace=True)
        df.rename(columns={"animal": "monkey"}, inplace=True)

        # Check if exists and format the column animalsExpected
        df["animalsExpected"] = df["animalsExpected"].apply(eval)

        # Reformat date column
        df['dateR'] = df['date'].astype(str).str[:-6].astype(np.int64)
        df['dateR'] = pd.to_datetime(df.dateR, format='%Y%m%d')

        # Sort by date
        df = df.sort_values(by=['dateR'])

        # reset the index
        df = df.reset_index(drop=True)

        # ====================================================================
        for date in df.dateR.unique():
            unique_animals = df[df['dateR'] == date]['animalsExpected'].values[0]

            # cycle through the animals expected in the session
            for monkey in unique_animals:
                # create a table (A) with the animal information
                A = df[(df['dateR'] == date) & (df['monkey'] == monkey)]

                # create a table (B) with the session information
                B = df[df['dateR'] == date]

                # Assign sessions specific parameters
                device = 'lxbi1'
                experiment = 'AUT'
                task = 'Acoustic Discrimination'
                switched = False

                if (monkey == 'fenja') | (monkey == 'granny'):
                    last_session = df.loc[df['monkey'].isin(LT_group1)]['sessionNumber'].values[-1]
                    sessionNumber = df[df['dateR'] == date]['sessionNumber'].unique()[0] - last_session
                    group = 'B'

                else:
                    sessionNumber = df[df['dateR'] == date]['sessionNumber'].unique()[0]
                    group = 'A'

                # flag the session as crashed if there are two or more datafiles in the current day
                crashed = (len(B[B['action'] == 'stop']) > 0) == 0

                # look for trials initiated by the animal in table A
                if len(A[A['object'].str.contains('trigger')]) > 0:

                    # check if there is the information regarding the session end and assign it as end time ...
                    if len(B[B['action'] == 'stop']) > 0:
                        lastEvent = B[B['action'] == 'stop']['timestamp'].values[-1]

                    # ... or use the last trial start (from either animals) as sessions end
                    else:
                        lastEvent = B[B['object'].str.contains('trigger')]['timestamp'].values[-1]

                    # Compute session duration in minutes
                    duration = lastEvent / 60000

                    # extract all trial start times
                    times = list(A[A['object'].str.contains('trigger')]['timestamp'] / lastEvent)

                    # calculate the median of all start trial times
                    medianTimes = np.median(list(A[A['object'].str.contains('trigger')]['timestamp'] / lastEvent))

                # if there are no trials from animal A in this session
                else:
                    # set the session duration with the session end information
                    if len(B[B['action'] == 'stop']) > 0:
                        lastEvent = B[B['action'] == 'stop']['timestamp'].values[-1]
                        duration = lastEvent / 60000

                    # or with the latest trial performed (by either animals)
                    elif len(B[B['object'].str.contains('trigger')]) > 0:
                        lastEvent = B[B['object'].str.contains('trigger')]['timestamp'].values[-1]
                        duration = lastEvent / 60000

                    # or assign nan if none of the animals interacted
                    else:
                        duration = np.nan

                    # assign nans to missing information
                    times = np.nan
                    medianTimes = np.nan

                sessions_df = sessions_df.append({
                    'device': device,
                    'date': date,
                    'session': sessionNumber,
                    'duration': duration,
                    'crashed': crashed,
                    'switched': switched,
                    'experiment': experiment,
                    'task': task,
                    'animal': monkey,
                    'species': 'long-tailed',
                    'group': group,
                    'trials': sum(A['object'].str.contains('trigger')),
                    'times': times,
                    'medianTimes': medianTimes},
                    ignore_index=True)

        # sort the new dataframe and reset its index
        sessions_df = sessions_df.sort_values(by=['species', 'date'])
        sessions_df = sessions_df.reset_index(drop=True)

    if 'RM' in file:
        print('===> Processing Rhesus Macaques data: ' + file)
        # ====================================================================
        # 1) Open and process the dataframe
        csv_file = directory_name / file
        df = pd.read_csv(csv_file, low_memory=False, decimal=',')
        df.rename(columns={"subjID": "monkey"}, inplace=True)
        df = df.loc[df.monkey.isin(list(df['monkey'].dropna().unique()))]

        df['date'] = pd.to_datetime(df.date, format='%Y%m%d')

        for monkey in df['monkey'].unique():
            unique_dates = df[df['monkey'] == monkey]['date'].unique()

            for idx in range(0, len(unique_dates)):
                A = df[(df['date'] == unique_dates[idx]) & (df['monkey'] == monkey)]

                # Assign sessions specific parameters
                device = 'xbi'
                task = 'Reversal Learning'
                sessionNumber = idx+1
                switched = False
                crashed = False
                lastEvent = A.sessionEnd.values[-1]
                duration = lastEvent / 60000000

                unique_experiments = A.experiment.unique()
                for exp in unique_experiments:
                    B = A[A['experiment'] == exp]
                    experiment = exp

                    # look for trials initiated by the animal in table A
                    if len(B) > 0:
                        # extract all trial start times
                        times = list(B['trialStart'] / lastEvent)

                        # calculate the median of all start trial times
                        medianTimes = np.median(times)

                    else:
                        times = np.nan
                        medianTimes = np.nan

                    sessions_df = sessions_df.append({
                        'device': device,
                        'date': unique_dates[idx],
                        'session': sessionNumber,
                        'duration': duration,
                        'crashed': crashed,
                        'switched': switched,
                        'experiment': experiment,
                        'task': task,
                        'animal': monkey,
                        'species': 'rhesus',
                        'group': monkey,
                        'trials': len(B),
                        'times': times,
                        'medianTimes': medianTimes},
                        ignore_index=True)

        # sort the new dataframe and reset its index
        sessions_df = sessions_df.sort_values(by=['species', 'date'])
        sessions_df = sessions_df.reset_index(drop=True)

# ===============================================================
# FIGURE 1D - Distribution of relative trial start across animals
figure3_height = (140 / 25.4) * sizeMult
figure3_width = (70 / 25.4) * sizeMult

for species in order:
    plot_df = sessions_df.copy(deep=False)
    plot_df = plot_df[plot_df['species'] == species]
    plot_df = plot_df[(plot_df['crashed'] == 0) & (plot_df['switched'] == 0)]

    if species == 'marmoset':
        monkeys_list = ['elero', 'dualina', 'almo', 'blake']

    if species == 'rhesus':
        monkeys_list = ['elm', 'cor', 'pin', 'lin']

    if species == 'long-tailed':
        monkeys_list = ['bella', 'kuemmel', 'leni', 'granny']

    fig, ax = plt.subplots(len(monkeys_list), 1, constrained_layout=False, sharex=True, figsize=(figure3_width, figure3_height))
    ax = ax.flatten()

    # ax = [None] * (len(monkeys_list) + 1)

    for i in range(0, len(monkeys_list)):
        # ax[i] = fig.add_subplot(gs[i, 0])
        label = str(monkeys_list[i][0:3]) + ', sessions ' + str(
            len(plot_df[(plot_df['animal'] == monkeys_list[i]) &
                        (plot_df['trials'] > 10)]['times']))

        ax[i].eventplot(plot_df[(plot_df['animal'] == monkeys_list[i]) &
                                (plot_df['trials'] > 10)]['times'].to_numpy(),
                        color="grey", lineoffsets=1, linelengths=1)

        ax[i].set_xlim(0, 1)
        ax[i].set_ylim(0, )
        # ax[i].set_xticks([])
        # ax[i].set_yticks([])
        ax[i].set_title(label, y=0.95, loc='center', fontsize=labelFontSize)

        if i == len(monkeys_list) - 1:
            plt.xlabel('Session Proportion', fontsize=labelFontSize)
            ax[i].set_xticks([0.25, 0.5, 0.75])

    if saveplot:
        plt.savefig('./analysis_output/Figure_Rasters_' + species + '.pdf', format='pdf')
        plt.close()