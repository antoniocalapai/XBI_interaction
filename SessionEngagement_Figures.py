import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# =============================================
# Setting plotting parameters
sizeMult = 1
saveplot = 0

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
    sessions_df['medianTimes'] = sessions_df['medianTimes'].astype(float)
    sessions_df = sessions_df[(sessions_df['crashed'] == 0) & (sessions_df['switched'] == 0)]
    sessions_df = sessions_df[sessions_df['experiment'] == 'AUT']

    return sessions_df


# ===============================================================
# FIGURE 1
sessions_df = dataload()
plot_df = sessions_df.copy(deep=False)
plot_df = plot_df[plot_df['experiment'] == 'AUT']

figure1_height = (135 / 25.4) * sizeMult
figure1_width = (90 / 25.4) * sizeMult

f, ax = plt.subplots(3, sharex=True, sharey=False, figsize=(figure1_width, figure1_height), constrained_layout=True)

for idx in range(0, len(order)):
    for_plot = plot_df[(plot_df['species'] == order[idx]) & (plot_df['trials'] > 10)]['medianTimes']
    ax[idx].hist(for_plot, color='C' + str(idx))
    ax[idx].set_xlim(0, 1)
    ax[idx].set_ylabel(ylabel='#', fontsize=labelFontSize)

    if idx == len(order) - 1:
        ax[idx].set_xlabel('Session Proportion', fontsize=labelFontSize)

    if idx == 0:
        ax[idx].set_title('Time of the median trial', y=1.0, fontsize=titleFontSize)

    med = np.median(for_plot)
    label = '-- = ' + str(round(med, 2)) + '\nN = ' + str(len(for_plot))
    ax[idx].text(0.95, 0, label, color='black', fontsize=10, va="bottom", ha="right",
                 bbox=dict(facecolor='white', edgecolor='black', alpha=0.8, boxstyle='round'))
    ax[idx].axvline(med, color='black', linestyle='--')
    ax[idx].set_xticks([0.25, 0.5, 0.75])

if saveplot:
    plt.savefig('./analysis_output/Figure_SE_1.pdf', format='pdf')
    plt.close()

# ===============================================================
# # FIGURE 2
# sessions_df = dataload()
# plot_df = sessions_df.copy(deep=False)
# plot_df = plot_df[plot_df['experiment'] != 'AUT']
#
# figure2_height = (90 / 25.4) * sizeMult
# figure2_width = (90 / 25.4) * sizeMult
#
# f, ax = plt.subplots(2, sharex=True, sharey=False, figsize=(figure2_width, figure2_height), constrained_layout=True)
#
# for idx in range(0, len(order) - 1):
#     for_plot = plot_df[(plot_df['species'] == order[idx]) & (plot_df['trials'] > 10)]['medianTimes']
#     ax[idx].hist(for_plot, color='C' + str(idx))
#     ax[idx].set_xlim(0, 1)
#     ax[idx].set_ylabel(ylabel='#', fontsize=labelFontSize)
#
#     if idx == len(order) - 2:
#         ax[idx].set_xlabel('Session Proportion', fontsize=labelFontSize)
#
#     if idx == 0:
#         ax[idx].set_title('Time of the median trial', y=1.0, fontsize=titleFontSize)
#
#     med = np.median(for_plot)
#     label = '-- = ' + str(round(med, 2)) + '\nN = ' + str(len(for_plot))
#     ax[idx].text(0.95, 0, label, color='black', fontsize=10, va="bottom", ha="right",
#                  bbox=dict(facecolor='white', edgecolor='black', alpha=0.8, boxstyle='round'))
#     ax[idx].axvline(med, color='black', linestyle='--')
#     ax[idx].set_xticks([0.25, 0.5, 0.75])
#
# if saveplot:
#     plt.savefig('./analysis_output/Figure_SE_2.pdf', format='pdf')
#     plt.close()

