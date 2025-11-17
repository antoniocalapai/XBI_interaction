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

likelihood_window = 30000  # in milliseconds
# maximum_ITI = 60000  # in milliseconds
penalty_wrong = 5000  # in milliseconds

# ==============================================
# Initialize dataframe for all sessions across all experiments
trials_df = pd.DataFrame()
InterTrialIntervals = pd.DataFrame()

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
        manual_list = ['ivvy', 'durin', 'clia', 'intro', 'blake', 'almo']

        ITI_df = df.copy(deep=False)
        ITI_df = ITI_df.loc[ITI_df.monkey.isin(manual_list)]

        # Only take the AUT data
        ITI_df.loc[ITI_df['object'].str.contains('correct'), 'object'] = 'reward'
        ITI_df.loc[ITI_df['object'].str.contains('star'), 'object'] = 'start'
        ITI_df.loc[ITI_df['object'].str.contains('wrong'), 'object'] = 'wrong'

        ITI_df = ITI_df[(ITI_df['object'] == 'reward') |
                        (ITI_df['object'] == 'wrong') |
                        (ITI_df['object'] == 'start')]

        for m in manual_list:
            print('Processing animal ' + m)

            if 'AUT' in file:
                temp_df = ITI_df[(ITI_df['version'] > 9) & (ITI_df['monkey'] == m)]
                task = 'AUT'
            else:
                temp_df = ITI_df[(ITI_df['monkey'] == m)]
                task = 'experiment'

            counter = 0

            for fl in temp_df.filename.unique():
                counter += 1

                print('--> datafile ' + str(counter) + ' of ' + str(len(temp_df.filename.unique())))
                temp_df2 = temp_df[temp_df['filename'] == fl]

                for i in temp_df2.trial.unique():
                    if (i > 0) & (i + 1 in temp_df2.trial.unique()):

                        if ((sum(temp_df2[temp_df2['trial'] == i]['object'] == 'reward')) |
                            (sum(temp_df2[temp_df2['trial'] == i]['object'] == 'wrong'))) & \
                                (sum(temp_df2[temp_df2['trial'] == i + 1]['object'] == 'start')):

                            temp_df3 = temp_df2[temp_df2['trial'] == i]. \
                                append(temp_df2[temp_df2['trial'] == i + 1], ignore_index=True)

                            T1 = temp_df3[(temp_df3['trial'] == i) & ((temp_df3['object'] == 'reward') |
                                                                      (temp_df3['object'] == 'wrong'))][
                                'timestamp'].values

                            T2 = temp_df3[(temp_df3['trial'] == i + 1) & (temp_df3['object'] == 'start')][
                                'timestamp'].values

                            outcome = len(
                                temp_df3[(temp_df3['trial'] == i) & (temp_df3['object'] == 'reward')]) == 1

                            if (len(T2) == 1) & (len(T1) == 1):
                                InterTrialIntervals = InterTrialIntervals.append({
                                    'animal': m,
                                    'species': 'marmoset',
                                    'trial': i,
                                    'step': temp_df3['step'].unique()[0],
                                    'task': task,
                                    'outcome': int(outcome),
                                    'ITI': int(T2 - T1),
                                    'likelihood': int(int(T2 - T1) <= likelihood_window)},
                                    ignore_index=True)

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
        manual_list = ['bella', 'kuemmel', 'leni', 'granny', 'fenja']

        ITI_df = df.copy(deep=False)
        ITI_df = ITI_df.loc[ITI_df.monkey.isin(manual_list)]

        # Only take the AUT data
        ITI_df.loc[ITI_df['object'].str.contains('reward'), 'object'] = 'reward'
        ITI_df.loc[ITI_df['object'].str.contains('trigger'), 'object'] = 'start'
        ITI_df.loc[ITI_df['object'].str.contains('wrong'), 'object'] = 'wrong'

        ITI_df = ITI_df[(ITI_df['object'] == 'reward') |
                        (ITI_df['object'] == 'wrong') |
                        (ITI_df['object'] == 'start')]

        ITI_df = ITI_df.sort_values(by=['dateR', 'monkey', 'trial'])
        ITI_df = ITI_df.reset_index(drop=True)

        for m in manual_list:
            print('Processing animal ' + m)
            temp_df = ITI_df[(ITI_df['monkey'] == m)]

            experiment = 'AUT'
            counter = 0

            for fl in temp_df.dateR.unique():
                counter += 1

                print('--> datafile ' + str(counter) + ' of ' + str(len(temp_df.dateR.unique())))
                temp_df2 = temp_df[temp_df['dateR'] == fl]

                for i in temp_df2.trial.unique():
                    if (i > 0) & (i + 1 in temp_df2.trial.unique()):

                        if ((sum(temp_df2[temp_df2['trial'] == i]['object'] == 'reward')) |
                            (sum(temp_df2[temp_df2['trial'] == i]['object'] == 'wrong'))) & \
                                (sum(temp_df2[temp_df2['trial'] == i + 1]['object'] == 'start')):

                            temp_df3 = temp_df2[temp_df2['trial'] == i]. \
                                append(temp_df2[temp_df2['trial'] == i + 1], ignore_index=True)

                            T1 = temp_df3[(temp_df3['trial'] == i) & ((temp_df3['object'] == 'reward') |
                                                                      (temp_df3['object'] == 'wrong'))][
                                'timestamp'].values

                            T2 = temp_df3[(temp_df3['trial'] == i + 1) & (temp_df3['object'] == 'start')][
                                'timestamp'].values

                            outcome = len(
                                temp_df3[(temp_df3['trial'] == i) & (temp_df3['object'] == 'reward')]) == 1

                            if (len(T2) == 1) & (len(T1) == 1):
                                InterTrialIntervals = InterTrialIntervals.append({
                                    'animal': m,
                                    'species': 'long-tailed',
                                    'trial': i,
                                    'step': temp_df3['step'].unique()[0],
                                    'task': experiment,
                                    'outcome': int(outcome),
                                    'ITI': int(T2 - T1),
                                    'likelihood': int(int(T2 - T1) <= likelihood_window)},
                                    ignore_index=True)

    if 'RM' in file:
        print('===> Processing Rhesus Macaques data: ' + file)
        # ====================================================================
        # 1) Open and process the dataframe
        csv_file = directory_name / file
        df = pd.read_csv(csv_file, low_memory=False, decimal=',')
        df.rename(columns={"subjID": "monkey"}, inplace=True)
        df = df.loc[df.monkey.isin(list(df['monkey'].dropna().unique()))]

        df['date'] = pd.to_datetime(df.date, format='%Y%m%d')

        # === ITI
        ITI_df = df.copy(deep=False)
        manual_list = ITI_df.monkey.unique()

        ITI_df = ITI_df.sort_values(by=['date', 'monkey', 'trial'])
        ITI_df = ITI_df.reset_index(drop=True)

        for m in manual_list:
            print('Processing animal ' + m)
            temp_df = ITI_df[(ITI_df['monkey'] == m)]

            counter = 0

            for fl in temp_df.date.unique():
                counter += 1

                print('--> datafile ' + str(counter) + ' of ' + str(len(temp_df.date.unique())))
                temp_df2 = temp_df[temp_df['date'] == fl]

                for i in temp_df2.trial.unique():
                    if (i > 0) & (i + 1 in temp_df2.trial.unique()):

                        if ((sum(temp_df2[temp_df2['trial'] == i]['outcome'] == 1)) |
                            (sum(temp_df2[temp_df2['trial'] == i]['outcome'] == 0))) & \
                                (len(temp_df2[temp_df2['trial'] == i + 1]) == 1):
                            temp_df3 = temp_df2[temp_df2['trial'] == i]. \
                                append(temp_df2[temp_df2['trial'] == i + 1], ignore_index=True)

                            T1 = temp_df3[temp_df3['trial'] == i]['trialEnd'][0]

                            T2 = temp_df3[temp_df3['trial'] == i + 1]['trialEnd'].values

                            outcome = temp_df3[temp_df3['trial'] == i]['outcome'][0]

                            ITI = int(T2 - T1) / 1000

                            InterTrialIntervals = InterTrialIntervals.append({
                                'animal': m,
                                'species': 'rhesus',
                                'trial': i,
                                'step': temp_df3[temp_df3['trial'] == i]['step'][0],
                                'task': temp_df3[temp_df3['trial'] == i]['experiment'][0],
                                'outcome': int(outcome),
                                'ITI': ITI,
                                'likelihood': ITI <= likelihood_window},
                                ignore_index=True)

InterTrialIntervals.to_csv('./data/ITI_DF.csv', sep=',', index=False)

# ==========================================================================================================
# Computed likelihood
trials_df = InterTrialIntervals.copy(deep=False)
trials_df = trials_df.sort_values(['species', 'animal', 'task', 'trial'])
trials_df = trials_df.reset_index(drop=True)

# changes the scale of the ITI to seconds
trials_df['corrected_ITI'] = trials_df['ITI'] / 1000

monkeys_list = trials_df['animal'].unique()

likelihood_df = pd.DataFrame()
for m in monkeys_list:
    temp_df = trials_df[trials_df['animal'] == m]

    for t in temp_df['task'].unique():
        temp_df_2 = temp_df[temp_df['task'] == t]

        # print(str(m) + ' ' + str(t) + ' ' + str(len(temp_df_2[temp_df_2['likelihood'] == 1]) / len(temp_df_2)))

        # likelihood of starting another trial (in 30 seconds) after correct response (outcome == 1)
        likelihood = temp_df_2[temp_df_2['outcome'] == 1]['likelihood'].sum() / len(temp_df_2)

        likelihood_df = likelihood_df.append({
            'animal': m,
            'species': temp_df_2['species'].unique()[0],
            'experiment': t,
            'outcome': 'correct',
            'likelihood': likelihood},
            ignore_index=True)

        # likelihood of starting another trial (in 30 seconds) after wrong response (outcome == 0)
        likelihood = temp_df_2[temp_df_2['outcome'] == 0]['likelihood'].sum() / len(temp_df_2)

        likelihood_df = likelihood_df.append({
            'animal': m,
            'species': temp_df_2['species'].unique()[0],
            'experiment': t,
            'outcome': 'wrong',
            'likelihood': likelihood},
            ignore_index=True)

# ==========================================================================================================
# Computed difference in likelihood
trials_df = InterTrialIntervals.copy(deep=False)
trials_df = trials_df.sort_values(['species', 'animal', 'task', 'trial'])
trials_df = trials_df.reset_index(drop=True)

# changes the scale of the ITI to seconds
trials_df['corrected_ITI'] = trials_df['ITI'] / 1000

monkeys_list = trials_df['animal'].unique()

diff_df = pd.DataFrame()
for m in monkeys_list:
    temp_df = trials_df[trials_df['animal'] == m]

    for t in temp_df['task'].unique():
        temp_df_2 = temp_df[temp_df['task'] == t]

        # likelihood of starting another trial (in 30 seconds) after correct (outcome == 1)
        correct = temp_df_2[temp_df_2['outcome'] == 1]['likelihood'].sum() / len(temp_df_2)
        wrong = temp_df_2[temp_df_2['outcome'] == 0]['likelihood'].sum() / len(temp_df_2)

        diff_df = diff_df.append({
            'animal': m,
            'species': temp_df_2['species'].unique()[0],
            'experiment': temp_df_2['task'].unique()[0],
            'difference': correct - wrong},
            ignore_index=True)

# ==========================================================================================================
# Computed difference in likelihood across steps
trials_df = InterTrialIntervals.copy(deep=False)
trials_df = trials_df.sort_values(['species', 'animal', 'task', 'trial'])
trials_df = trials_df.reset_index(drop=True)

# changes the scale of the ITI to seconds
trials_df['corrected_ITI'] = trials_df['ITI'] / 1000
trials_df = trials_df[trials_df['task'] == 'AUT']

monkeys_list = trials_df['animal'].unique()

steps_df = pd.DataFrame()
for m in monkeys_list:
    temp_df = trials_df[trials_df['animal'] == m]

    for s in temp_df['step'].unique():
        temp_df_2 = temp_df[temp_df['step'] == s]

        # likelihood of starting another trial (in 30 seconds) after correct (outcome == 1)
        correct = temp_df_2[temp_df_2['outcome'] == 1]['likelihood'].sum() / len(temp_df_2)
        wrong = temp_df_2[temp_df_2['outcome'] == 0]['likelihood'].sum() / len(temp_df_2)

        steps_df = steps_df.append({
            'animal': m,
            'species': temp_df_2['species'].unique()[0],
            'step': s,
            'difference': correct - wrong,
            'total': correct + wrong,
            'N': len(temp_df_2)},
            ignore_index=True)

# ==================================================================
# Figure 1
plot_df = likelihood_df.copy(deep=False)
plot_df['species'] = plot_df['species'].replace('Rhesus', 'rhesus', regex=True)
plot_df['ID'] = plot_df['animal'].astype(str).str[0:2]

pal = ['pink', 'grey']

g = sns.FacetGrid(plot_df, col="experiment", row="species",
                  row_order=order, col_order=['AUT', 'experiment'], sharex=False)
g.map_dataframe(sns.barplot, x="ID", y="likelihood", hue='outcome', palette=pal, edgecolor="black")
g.set_titles('')
g.axes[0, 0].set_ylabel('Likelihood', fontsize=labelFontSize)
g.axes[1, 0].set_ylabel('Likelihood', fontsize=labelFontSize)
g.axes[2, 0].set_ylabel('Likelihood', fontsize=labelFontSize)

g.axes[0, 0].set_title('AUT', fontsize=labelFontSize)
g.axes[0, 1].set_title('Experiment', fontsize=labelFontSize)

g.axes[0, 0].tick_params(labelsize=tickFontSize)
g.axes[1, 0].tick_params(labelsize=tickFontSize)
g.axes[2, 0].tick_params(labelsize=tickFontSize)
g.axes[0, 1].tick_params(labelsize=tickFontSize)
g.axes[1, 1].tick_params(labelsize=tickFontSize)
g.axes[2, 1].tick_params(labelsize=tickFontSize)

plt.tight_layout()

if saveplot:
    plt.savefig('./analysis_output/Figure_ITI_1.pdf', format='pdf')
    plt.close()

# ==================================================================
# Figure 2
figure2_height = (85 / 25.4) * sizeMult
figure2_width = (120 / 25.4) * sizeMult

plot_df = likelihood_df.copy(deep=False)
plot_df['species'] = plot_df['species'].replace('Rhesus', 'rhesus', regex=True)
plot_df['ID'] = plot_df['animal'].astype(str).str[0:3]

pal = ['pink', 'grey']

fig, ax = plt.subplots(1, 2, constrained_layout=True, sharex=True, sharey=True,
                       figsize=(figure2_width, figure2_height))

g = sns.boxplot(data=plot_df[plot_df['experiment'] == 'AUT'],
                x="species", y="likelihood", hue="outcome", order=order,
                showfliers=False, palette=pal, ax=ax[0])

g = sns.boxplot(data=plot_df[plot_df['experiment'] == 'experiment'],
                x="species", y="likelihood", hue="outcome", order=order,
                showfliers=False, palette=pal, ax=ax[1])

sns.stripplot(data=plot_df[plot_df['experiment'] == 'AUT'],
              x="species", y="likelihood", hue="outcome", order=order,
              color='black', alpha=.3, dodge=True, jitter=0, ax=ax[0])

sns.stripplot(data=plot_df[plot_df['experiment'] == 'experiment'],
              x="species", y="likelihood", hue="outcome", order=order,
              color='black', alpha=.3, dodge=True, jitter=0, ax=ax[1])

ax[0].set_xlabel(xlabel=None)
ax[1].set_xlabel(xlabel=None)
ax[1].set_ylabel(ylabel=None)
ax[0].tick_params(labelsize=tickFontSize)
ax[1].tick_params(labelsize=tickFontSize)
ax[0].set_ylabel(ylabel='Likelihood', fontsize=labelFontSize)

handles, labels = ax[0].get_legend_handles_labels()
l = plt.legend(handles[0:2], labels[0:2], loc=2, borderaxespad=0.)

ax[0].get_legend().remove()

if saveplot:
    plt.savefig('./analysis_output/Figure_ITI_2.pdf', format='pdf')
    plt.close()

# ==================================================================
# Figure 3
figure3_height = (80 / 25.4) * sizeMult
figure3_width = (80 / 25.4) * sizeMult

plot_df = diff_df.copy(deep=False)
plot_df['species'] = plot_df['species'].replace('Rhesus', 'rhesus', regex=True)
plot_df['ID'] = plot_df['animal'].astype(str).str[0:3]

pal = ['cyan', 'green']

fig, ax = plt.subplots(1, 1, constrained_layout=True, sharex=True,
                       figsize=(figure3_width, figure3_height))

g = sns.boxplot(data=plot_df, x="species", y="difference", hue="experiment", order=order,
                showfliers=False, palette=pal, ax=ax)

sns.stripplot(data=plot_df, x="species", y="difference", hue="experiment", order=order,
              color='black', alpha=.3, dodge=True, jitter=0, ax=ax)

ax.set_xlabel(xlabel=None)
ax.tick_params(labelsize=tickFontSize)
ax.set_ylabel(ylabel='Difference in likelihood [correct - wrong]', fontsize=labelFontSize)

handles, labels = ax.get_legend_handles_labels()
l = plt.legend(handles[0:2], labels[0:2], loc=2, borderaxespad=0.)

if saveplot:
    plt.savefig('./analysis_output/Figure_ITI_3.pdf', format='pdf')
    plt.close()

# ==================================================================
# Figure 4
figure4_height = (180 / 25.4) * sizeMult
figure4_width = (180 / 25.4) * sizeMult

plot_df = steps_df.copy(deep=False)
plot_df['species'] = plot_df['species'].replace('Rhesus', 'rhesus', regex=True)
plot_df['ID'] = plot_df['animal'].astype(str).str[0:3]
plot_df['step'] = plot_df['step'].astype('int64')

fig, ax = plt.subplots(len(order), 3, constrained_layout=True, sharex=False, sharey='col',
                       figsize=(figure4_width, figure4_height))

for s in range(0, len(order)):
    for_plot = plot_df[plot_df['species'] == order[s]]

    if order[s] == 'marmoset':
        for_plot = for_plot[for_plot['step'] > 10]

    g = sns.lineplot(data=for_plot, x="step", y="N", ax=ax[s, 0], color='C'+str(s))
    g = sns.lineplot(data=for_plot, x="step", y="total", ax=ax[s, 1], color='C'+str(s))
    g = sns.lineplot(data=for_plot, x="step", y="difference", ax=ax[s, 2], color='C'+str(s))

    if s != 2:
        ax[s, 0].set_xlabel(xlabel=None)
        ax[s, 1].set_xlabel(xlabel=None)
        ax[s, 2].set_xlabel(xlabel=None)

        ax[s, 0].set_xticklabels([])
        ax[s, 1].set_xticklabels([])
        ax[s, 2].set_xticklabels([])
    else:
        ax[s, 0].set_xlabel(xlabel='Steps', fontsize=labelFontSize)
        ax[s, 1].set_xlabel(xlabel='Steps', fontsize=labelFontSize)
        ax[s, 2].set_xlabel(xlabel='Steps', fontsize=labelFontSize)

    ax[s, 1].set_ylim(0, 1)
    ax[s, 2].set_ylim(-1, 1)

    if s == 0:
        ax[s, 0].set_title(label='AUT progression', fontsize=labelFontSize)
        ax[s, 1].set_title(label='Likelihood', fontsize=labelFontSize)
        ax[s, 2].set_title(label='\u0394 Likelihood', fontsize=labelFontSize)

    ax[s, 1].set_ylabel(ylabel=None)
    ax[s, 2].set_ylabel(ylabel=None)

    ax[s, 0].set_ylabel(ylabel='Trials', fontsize=labelFontSize)
    ax[s, 2].axhline(0, color='black', linestyle='--')

if saveplot:
    plt.savefig('./analysis_output/Figure_ITI_4.pdf', format='pdf')
    plt.close()

