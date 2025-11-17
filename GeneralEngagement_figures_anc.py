from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats


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

order = ['marmoset', 'rhesus', 'long-tailed']


# ============================================
# Load the Data Frame
def dataload():
    sessions_df = pd.read_csv('./data/ALL_SessionDF.csv', low_memory=False, decimal=',')

    sessions_df['crashed'] = sessions_df['crashed'].astype(float)
    sessions_df['switched'] = sessions_df['switched'].astype(float)
    sessions_df['trials'] = sessions_df['trials'].astype(float)
    sessions_df['duration'] = sessions_df['duration'].astype(float)
    sessions_df['session'] = sessions_df['session'].astype(float)

    sessions_df = sessions_df[(sessions_df['crashed'] == 0) & (sessions_df['switched'] == 0)]

    return sessions_df


# ==========================================================================================
# FIGURE 1 - Total trials across sessions for each animal
sessions_df = dataload()

for species in order:

    figure1_height = (120 / 25.4) * sizeMult
    figure1_width = (120 / 25.4) * sizeMult

    plot_df = sessions_df.copy(deep=False)
    plot_df = plot_df[plot_df['species'] == species]
    plot_df['animal'] = plot_df['animal'].str[:3]
    plot_df.sort_values(by=['animal'])

    zerotrials = []
    all_sess = []
    animals_id = []

    for m in plot_df['animal'].unique():
        zerotrials.append(len(plot_df[(plot_df['animal'] == m) & (plot_df['trials'] == 0)]['session'].unique()))
        all_sess.append(len(plot_df[plot_df['animal'] == m]['session'].unique()))
        animals_id.append(m)

    f, ax = plt.subplots(2, sharex='col',
                         gridspec_kw={'height_ratios': [3, 1]}, constrained_layout=True,
                         figsize=(figure1_width, figure1_height))

    f.suptitle('Total trials: ' + species, fontsize=titleFontSize)

    for_plot = plot_df.groupby(['animal'], as_index=False)['session'].count()

    g = sns.barplot(x=animals_id,
                    y=all_sess,
                    ax=ax[1], color="gray", edgecolor="gray")

    f = sns.barplot(x=animals_id,
                    y=zerotrials,
                    ax=ax[1], color="black", edgecolor="black")

    sns.boxenplot(x='animal', y='trials', data=plot_df, color="grey", showfliers=False, ax=ax[0])
    sns.stripplot(x='animal', y='trials', data=plot_df, color="black", alpha=.3, ax=ax[0])

    ax[0].set_ylabel(ylabel='Trials', fontsize=labelFontSize)
    ax[1].set_ylabel(ylabel='Sessions', fontsize=labelFontSize)

    ax[0].set_xlabel(xlabel=None)
    ax[0].tick_params(labelsize=tickFontSize)
    ax[1].tick_params(labelsize=tickFontSize)

    if saveplot:
        plt.savefig('./analysis_output/Figure_GE_1_' + species + '.pdf', format='pdf')
        plt.close()

# ========================================================================
# FIGURE 2 - Session Duration in hours and trials across sessions (lineplot)
for species in order:

    figure2_height = (120 / 25.4) * sizeMult
    figure2_width = (120 / 25.4) * sizeMult

    sessions_df = dataload()
    plot_df = sessions_df.copy(deep=False)
    plot_df = plot_df[plot_df['species'] == species]
    plot_df['duration'] = plot_df['duration'] / 60
    plot_df = plot_df[plot_df['duration'] < 10]
    plot_df = plot_df[plot_df['trials'] > 0]
    plot_df['Trials / Hour'] = plot_df['trials'] / plot_df['duration']

    f, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 1]}, constrained_layout=True,
                         figsize=(figure2_width, figure2_height))

    bygroup_df = plot_df.groupby(['group', 'session'], as_index=False)['Trials / Hour'].sum()

    sns.regplot(x='session', y='Trials / Hour', data=bygroup_df, ax=ax[0])
    ax[0].set_xlabel(xlabel='Sessions', fontsize=labelFontSize)
    ax[0].set_ylabel(ylabel='Trials / Hour', fontsize=labelFontSize)

    g = sns.histplot(plot_df['duration'], color="grey", bins=30, ax=ax[1])

    ax[1].set_xlabel(xlabel='Hours', fontsize=labelFontSize)
    ax[1].set_ylabel(ylabel='#', fontsize=labelFontSize)
    ax[1].set_title('Distribution of sessions duration', y=1, fontsize=titleFontSize)

    if saveplot:
        plt.savefig('./analysis_output/Figure_GE_2_' + species + '.pdf', format='pdf')
        plt.close()

# ========================================================================
# FIGURE 3 - Trials / Hour across species
sessions_df = dataload()

figure3_height = (90 / 25.4) * sizeMult
figure3_width = (90 / 25.4) * sizeMult

plot_df = sessions_df.copy(deep=False)
plot_df['duration'] = plot_df['duration'] / 60
plot_df = plot_df[plot_df['duration'] < 10]
# plot_df = plot_df[plot_df['trials'] > 0]
plot_df['Trials / Hour'] = plot_df['trials'] / plot_df['duration']

f, ax = plt.subplots(constrained_layout=True, figsize=(figure3_width, figure3_height))
bygroup_df = plot_df.groupby(['species', 'group', 'session'], as_index=False)['Trials / Hour'].sum()
sns.stripplot(x='species', y='Trials / Hour', order=order, color='black', alpha=.15, data=bygroup_df, ax=ax)
sns.boxenplot(x='species', y='Trials / Hour', order=order, data=bygroup_df, showfliers=False, ax=ax)

ax.set_xlabel(xlabel=None)
ax.set_ylabel(ylabel='Trials / Hour', fontsize=labelFontSize)
ax.tick_params(labelsize=tickFontSize)

data1 = bygroup_df[bygroup_df['species'] == 'long-tailed']['Trials / Hour'].values
data2 = bygroup_df[bygroup_df['species'] == 'long-tailed']['session'].values
# calculate Pearson's correlation
corr, p = pearsonr(data1, data2)
print('Pearsons correlation: %.3f' % corr)
print('Pearsons correlation: %.3f' % p)

if saveplot:
    plt.savefig('./analysis_output/Figure_GE_3.pdf', format='pdf')
    plt.close()

# ===================================================================
# FIGURE 4 - Change in trials / hour across sessions
figure4_height = (90 / 25.4) * sizeMult
figure4_width = (120 / 25.4) * sizeMult

f, ax = plt.subplots(constrained_layout=True, figsize=(figure3_width, figure3_height))

sessions_df = dataload()
plot_df = sessions_df.copy(deep=False)
plot_df['duration'] = plot_df['duration'] / 60
plot_df = plot_df[plot_df['duration'] < 10]
plot_df = plot_df[plot_df['trials'] > 0]
plot_df['Trials / Hour'] = plot_df['trials'] / plot_df['duration']

reg_df = pd.DataFrame()
for m in plot_df.animal.unique():
    A = plot_df[plot_df['animal'] == m]

    slope, intercept, r_value, p_value, std_err = \
        stats.linregress(A['session'].values, A['Trials / Hour'].values)

    reg_df = reg_df.append({
        'animal': m,
        'group': A['group'].unique()[0],
        'species': A['species'].unique()[0],
        'r_value': r_value,
        'N': len(A)},
        ignore_index=True)

sns.stripplot(x='species', y='r_value', order=order, s=15, alpha=.65, dodge=True, data=reg_df, ax=ax)
ax.axhspan(ymin=-0.2, ymax=0.2, facecolor='gray', alpha=0.2)
ax.set_xlabel(xlabel=None)
ax.set_ylabel(ylabel='R-squared', fontsize=labelFontSize)
ax.tick_params(labelsize=tickFontSize)

if saveplot:
    plt.savefig('./analysis_output/Figure_GE_4.pdf', format='pdf')
    plt.close()
