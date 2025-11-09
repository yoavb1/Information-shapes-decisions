from django.test import TestCase

import random
import math
from scipy.stats import norm
import numpy as np
import pandas as pd
# Create your tests here.


# parse log file
def parse_log_file(user_id):
    with open("../data/log files/user {} logs file.txt".format(user_id), 'r') as file:
        data = file.read().replace('\n', '')
    for log in (data[1:-1].split(',')):
        print(log)

# parse_log_file(1)


def create_event_dict(d_sys, mu_noise=5, d=1.5):
    # Parameters
    mu_signal = mu_noise + d
    ps = 0.4
    v_fp, v_tn, v_fn, v_tp = -2, 2, -4, 2
    u = (v_fp - v_tn) / (v_fn - v_tp)
    threshold = ((1 - ps) / ps) * u
    data = {}
    index = 0
    for i in range(20):
        index += 1
        # Stimulus and event type
        signal_or_noise = np.random.uniform(0, 1)
        if signal_or_noise < ps:
            signal_or_noise = 'signal'
            stimulus = random.gauss(mu_signal, 1)
        else:
            signal_or_noise = 'noise'
            stimulus = random.gauss(mu_noise, 1)
        if stimulus > 10:
            stimulus = 10
        elif stimulus < 1:
            stimulus = 1
        stimulus = round(stimulus, 1)

        # Alarm Probabilities
        z_tp = (d_sys ** 2 - 2.0 * math.log(threshold)) / (2.0 * d_sys)
        z_fp = z_tp - d_sys
        p_tp = norm.cdf(z_tp)
        p_fp = norm.cdf(z_fp)

        # Alarm indication
        alarm_or_not = np.random.uniform(0, 1)
        # Signal event
        if signal_or_noise == 'signal':
            # Raise Alarm
            if alarm_or_not < p_tp:
                alarm_or_not = 'Alarm'
            # Don't raise alarm
            else:
                alarm_or_not = 'No Alarm'
        # Noise Event
        else:
            # Raise Alarm
            if alarm_or_not < p_fp:
                alarm_or_not = 'Alarm'
            # Don't raise Alarm
            else:
                alarm_or_not = 'No Alarm'

        data[index] = [index, signal_or_noise, stimulus, alarm_or_not]
    return data


def check_experiment(data):
    tp, fp, tn, fn = 0, 0, 0, 0
    for event in data.keys():
        event_type = data[event][1]
        alarm_output = data[event][3]

        if alarm_output == 'No Alarm' and event_type == 'noise':
            tn += 1
        elif alarm_output == 'Alarm' and event_type == 'noise':
            fp += 1
        elif alarm_output == 'No Alarm' and event_type == 'signal':
            fn += 1
        elif alarm_output == 'Alarm' and event_type == 'signal':
            tp += 1

    p_tp = tp/(tp+fn)
    p_fp = fp/(fp+tn)
    z_tp = norm.ppf(p_tp)
    z_fp = norm.ppf(p_fp)
    return z_tp - z_fp


def events(condition, d_sys):
    index = 1
    while index <= 10:
        data = create_event_dict(d_sys, mu_noise=5, d=1.5)
        df = pd.DataFrame.from_dict(data, orient='index', columns=['event', 'signal_or_noise', 'stimulus', 'alarm_or_not'])
        d = round(check_experiment(data), 2)
        if d_sys-0.05 < d < d_sys + 0.05 and df[df['signal_or_noise'] == 'signal'].shape[0] == 7:
            signal = df[df['signal_or_noise'] == 'signal']
            noise = df[df['signal_or_noise'] == 'noise']
            d_human = round(signal.stimulus.mean() - noise.stimulus.mean(), 2)
            std_signal = round(signal.stimulus.std(), 2)
            std_noise = round(noise.stimulus.std(), 2)
            if 1.4 < d_human < 1.6:
                if 0.7 < std_signal < 1.3 and 0.7 < std_noise < 1.3:
                    print("d'_sys =_sys {}".format(d))
                    df.to_csv('../blocks data/condition {}/block {}.csv'.format(condition, index), index=False)
                    index += 1
            # print("d'_sys = {}, d'_human = {}, std_signal = {}, std_noise = {}".format(d, d_human, std_signal, std_noise))


# events(3, 1.6)


def check_events(condition, block):
    events = pd.read_csv("../blocks data/condition {}/block {}.csv".format(condition, block))
    print('max noise: {}'.format(events[events['signal_or_noise'] == 'noise'].stimulus.max()))
    print('min signal: {}'.format(events[events['signal_or_noise'] == 'signal'].stimulus.min()))
    print('{} unique stimulus'.format(len(events.stimulus.unique())))
    for s in events.stimulus.unique():
        if events[(events['stimulus'] == s)].shape[0] > 1:
            print(s)


def check_d_sys(condition, block):
    events = pd.read_csv("../blocks data/condition {}/block {}.csv".format(condition, block))
    tp, fp, tn, fn = 0, 0, 0, 0
    for index, row in events.iterrows():
        if row['signal_or_noise'] == 'signal' and row['alarm_or_not'] == 'Alarm':
            tp += 1
        elif row['signal_or_noise'] == 'signal' and row['alarm_or_not'] == 'No Alarm':
            fn += 1
        elif row['signal_or_noise'] == 'noise' and row['alarm_or_not'] == 'Alarm':
            fp += 1
        elif row['signal_or_noise'] == 'noise' and row['alarm_or_not'] == 'No Alarm':
            tn += 1
        else:
            print('now')
    p_tp = tp/(tp+fn)
    p_fp = fp/(fp+tn)
    z_tp = norm.ppf(p_tp)
    z_fp = norm.ppf(p_fp)
    print("condition: {} Block {} d'={}".format(condition, block, z_tp - z_fp))

def check_mean_std(condition, block):
    events = pd.read_csv("../blocks data/condition {}/block {}.csv".format(condition, block))
    signal = events[events['signal_or_noise'] == 'signal']
    noise = events[events['signal_or_noise'] == 'noise']
    print('Signal - M={}, SD={}'.format(round(signal.stimulus.mean(), 2), round(signal.stimulus.std(), 2)))
    print('Noise - M={}, SD={}'.format(round(noise.stimulus.mean(), 2), round(noise.stimulus.std(), 2)))
    print("d' = {}".format((round(signal.stimulus.mean() - noise.stimulus.mean(), 2))))


# check_mean_std(1, 1)

# events(3, 1.6)
# check_events(1, 1)

# condition = 2
# for block in range(1, 10):
#     check_d_sys(condition, block)
#     check_mean_std(condition, block)
#     print('----------')

