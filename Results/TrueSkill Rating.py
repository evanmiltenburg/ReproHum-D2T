import copy

from trueskill import Rating, quality_1vs1, rate_1vs1
import os
import csv
import numpy as np
import itertools
from sklearn.utils import resample
import random
from statsmodels.stats.multitest import multipletests
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd

##  Since the performance of some systems may be very similar and a total ordering would not reflect this,
## we adopt the practice used in machine translation of presenting a partial ordering into significance clusters
## established by bootstrap resampling. The TrueSkill algorithm is run 200 times, producing slightly different rankings
## each time as pairs of system outputs for comparison are randomly sampled. This way we can determine the range of
## ranks where each system is placed 95% of the time or more often. Clusters are then formed of systems whose rank ranges overlap.

def winnerloser(record):
    systemdict = {'sys0': 'Gold', 'sys1': 'Template', 'sys2': 'ed_cc', 'sys3': 'hier', 'sys4': 'macro'}

    #First shown system is record[29], second shown is record[31], best rating is record[32], worst rating is record[37]
    system_a = systemdict[record[29]]
    system_b = systemdict[record[31]]

    if (record[32] == 'A') and (record[37] == 'B'):
        outcomedict = {'best': system_a, 'worst': system_b}
    elif (record[32] == 'B') and (record[37] == 'A'):
        outcomedict = {'best': system_b, 'worst': system_a}
    else:
        outcomedict = 'error'
        #print(record[32], record[37])

    return outcomedict

def is_overlapping(x1,x2,y1,y2):
    return max(x1,y1) <= min(x2,y2)


def import_csvs():
    repetitionlist = []
    coherencelist = []
    grammaticalitylist = []

    for file in os.listdir('.'):
        if 'Repetition' in file:
            with open('./' + file, mode='r') as f:
                batch_csv = csv.reader(f)
                for idx, record in enumerate(batch_csv):
                    if idx > 0:
                        repetitionlist.append(record)
        elif 'Coherence' in file:
            with open('./' + file, mode='r') as f:
                batch_csv = csv.reader(f)
                for idx, record in enumerate(batch_csv):
                    if idx > 0:
                        coherencelist.append(record)
        elif 'Grammaticality' in file:
            with open('./' + file, mode='r') as f:
                batch_csv = csv.reader(f)
                for idx, record in enumerate(batch_csv):
                    if idx > 0:
                        grammaticalitylist.append(record)

    return repetitionlist, coherencelist, grammaticalitylist



def trueskill_scores(recordlist):
    # Defining number of iterations for bootstrap resample
    n_iterations = 1000

    bootstrapscores = {'Gold': [], 'Template': [], 'ed_cc': [], 'hier': [], 'macro': []}

    random.seed(42069)
    seedlist = random.sample(range(1000000000), 1000)

    # Each loop iteration is a single bootstrap resample and model fit
    for i in range(n_iterations):
        #print(i)
        # All the systems used in this experiment, we're going to start them off with no rating.
        iterationratescoredict = {'Gold': Rating(), 'Template': Rating(), 'ed_cc': Rating(), 'hier': Rating(), 'macro': Rating()}
        # Sampling n_samples from data, with replacement
        bootstrap_sample = resample(recordlist, replace=True, n_samples=len(recordlist), random_state=seedlist[i])

        #Update the rating for the systems based on the best and worst system for each record
        for record in bootstrap_sample:
            windict = winnerloser(record)
            if windict != 'error':
                iterationratescoredict[windict['best']], iterationratescoredict[windict['worst']] = rate_1vs1(iterationratescoredict[windict['best']], iterationratescoredict[windict['worst']])

        #And add the final scores of each iteration to the bootstrapscores dict
        for iterationsystem in iterationratescoredict:
            bootstrapscores[iterationsystem].append(iterationratescoredict[iterationsystem])

    #Trueskill rating contains two values: mu (the actual score) and sigma (the certainty of the score). We only use mu for our calculations.
    newbootstrapscores = copy.deepcopy(bootstrapscores)
    for key in newbootstrapscores:
        newbootstrapscores[key] = [x.mu for x in newbootstrapscores[key]]

    #Calculate the confidence intervals
    intervaldict = {}
    for key in newbootstrapscores:
        intervaldict.update({key: list(np.percentile(newbootstrapscores[key], [2.5, 97.5]))})

    print(intervaldict)

    # Now, we'll make clusters as discussed in the original paper.
    allclusters = []
    for system in intervaldict:
        clusterlist = [system]
        # We compare each system to the other systems in the intervaldict
        for compare in intervaldict:
            if system == compare:
                continue
            # If the two intervals overlap, make a cluster
            if is_overlapping(intervaldict[system][0], intervaldict[system][1], intervaldict[compare][0],
                              intervaldict[compare][1]):
                clusterlist.append(compare)

        #Check if the cluster did not exist before
        sortedcluster = sorted(clusterlist)
        if sortedcluster not in allclusters:
            allclusters.append(sortedcluster)

    print(allclusters)

    #The clusters seem to be lacking explicit information. I want to know which systems do not have overlapping intervals. So if pairs have non-overlapping intervals, we mark them here.
    pairwise_comparisons = list(itertools.combinations(intervaldict.keys(), 2))
    for combi in pairwise_comparisons:
        if not is_overlapping(intervaldict[combi[0]][0], intervaldict[combi[0]][1], intervaldict[combi[1]][0], intervaldict[combi[1]][1]):
            print(combi[0] + ' differs from ' + combi[1])


repetitionlist, coherencelist, grammaticalitylist = import_csvs()

print('Repetition:')
trueskill_scores(repetitionlist)

print('Coherence:')
trueskill_scores(coherencelist)

print('Grammaticality:')
trueskill_scores(grammaticalitylist)