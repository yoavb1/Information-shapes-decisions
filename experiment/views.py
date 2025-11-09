from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .models import Participant, Classification, PaymentCode, Block
import random as random
import string
import pandas as pd
import time
from datetime import datetime

# Add to the log file the ID of the user and the stimulus


# The function read from a csv file the experiment's parameters and return a parameters dictionary
def set_parameters():
    param = pd.read_csv("parameters/parameters.csv").rename(columns={'Unnamed: 0': 'parameter', '0': 'value'})
    blocks = param[param['parameter'] == 'blocks']['value'].iloc[0]
    events = param[param['parameter'] == 'events']['value'].iloc[0] + 1
    test_events = int(param[param['parameter'] == 'test_events']['value'].iloc[0]) + 1
    ps = param[param['parameter'] == 'ps']['value'].iloc[0]
    v_tp = param[param['parameter'] == 'v_tp']['value'].iloc[0]
    v_fp = param[param['parameter'] == 'v_fp']['value'].iloc[0]
    v_fn = param[param['parameter'] == 'v_fn']['value'].iloc[0]
    v_tn = param[param['parameter'] == 'v_tn']['value'].iloc[0]
    param = {'B': blocks, 'N': events, 'N_test': test_events, 'ps': ps,
             'v_tp': v_tp, 'v_fp': v_fp, 'v_tn': v_tn, 'v_fn': v_fn}
    return param


# The function generate payment code to the participant
def payment_code():
    all_char = string.ascii_letters + string.digits
    code = "".join(random.choice(all_char) for x in range(8))
    return code


# The function get the participant's IP
def get_client_ip(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
    except:
        ip = ''
    return ip


# The function get the user events' data for a specific block and return it as dictionary
def get_events(condition, block):
    events = pd.read_csv("blocks data/condition {}/block {}.csv".format(condition, block))
    return events.to_dict()


# The Function extract the event data for single event (classification type, alarm output and stimulus) and return
def get_event_data(data, trial_number):
    try:
        signal_or_noise = data['signal_or_noise'][str(trial_number - 1)]
        alarm_or_not = data['alarm_or_not'][str(trial_number - 1)]
        stimulus = data['stimulus'][str(trial_number - 1)]
    except:
        signal_or_noise = data['signal_or_noise'][trial_number - 1]
        alarm_or_not = data['alarm_or_not'][trial_number - 1]
        stimulus = data['stimulus'][trial_number - 1]
    return signal_or_noise, alarm_or_not, stimulus


# The function set the user id to be 1 more than the last user
def set_user_id():
    user_id = 1
    if Participant.objects.all().count() != 0:
        for user in Participant.objects.all():
            if int(user.user_id) >= user_id:
                user_id = int(user.user_id) + 1
    return user_id


# The function set the condition of the user to be the condition with the minimum participants
def set_condition():
    if PaymentCode.objects.all().count() != 0:
        d = {1: 0, 2: 0, 3: 0}
        for user in PaymentCode.objects.all():
            d[int(user.condition)] += 1
        return min(d, key=d.get)
    return random.randint(1, 3)


# Registration Screen, display the term and privacy form,
# set initial variables and parameters and create user object in the DB
def registration(request):
    ip = get_client_ip(request)
    # /?aid=testWorker&tptest=test
    request.session['aid'] = request.GET.get('aid', '') if request.GET.get('aid', '') is not None else 'test'

    request.session['experiment_start_time'] = time.time()
    request.session['code'] = payment_code()
    request.session['user_id'] = set_user_id()
    request.session['condition'] = set_condition()

    if request.session['condition'] == 1:           # Low cost Low d' - buy alert system
        request.session['cost'] = 5
    elif request.session['condition'] == 2:         # High cost High d' - buy alert system
        request.session['cost'] = 14
    elif request.session['condition'] == 3:         # High cost low d' - not but alert system
        request.session['cost'] = 14

    # Set Initial Values
    request.session['parameters'] = set_parameters()
    request.session['Alert System'] = 0
    request.session['score'] = 30
    request.session['alarm_or_not'] = 'No Alarm'
    request.session['default'] = 1
    request.session['block_number'] = 1
    request.session['trial_number'] = 1
    request.session['block_data'] = {}
    request.session['block_summary'] = {}
    request.session['instruction_page'] = 1
    request.session['logs'] = []

    if request.method == "POST":
        if request.POST['Continue'] == 'Continue':
            date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            Participant.objects.create(user_id=request.session['user_id'], date=date,
                                       condition=request.session['condition'], ip=ip, aid=request.session['aid'])
            return redirect('/consent_form/')
        if request.POST['Continue'] == 'End the experiment':
            return redirect('/end/')

    return render(request=request,
                  template_name='main/Registration.html')


# Payment screen
def consent_form(request):
    if request.method == "POST":
        if request.POST['Continue'] == 'Begin the experiment':
            return redirect('/instructions/')
        if request.POST['Continue'] == 'End the experiment':
            return redirect('/end/')

    return render(request=request,
                  template_name='main/Registration(2).html')


# Instruction Screen, display the relevant instruction page according to the participant progress
def instructions(request):
    if request.method == "POST":
        if request.POST['Continue'] == 'Continue':
            request.session['logs'].append('{} - POST: Instruction page {} Continue Button'.
                                           format(datetime.now(), request.session['instruction_page']))
            request.session['instruction_page'] += 1
            return redirect('/instructions/')
        if request.POST['Continue'] == 'Back':
            request.session['logs'].append('{} - POST: Instruction page {} Back Button'.
                                           format(datetime.now(), request.session['instruction_page']))
            request.session['instruction_page'] -= 1
            return redirect('/instructions/')
    if request.method == "GET":
        request.session['logs'].append('{} - GET: Instruction Page'.format(datetime.now()))
        if request.session['instruction_page'] == 4:
            request.session['trial_number'] = 1
            request.session['block_number'] = 1
            return redirect('/game/')
        elif request.session['instruction_page'] == 7:
            request.session['trial_number'] = 1
            request.session['block_number'] = 2
            return redirect('/game/')
        elif request.session['instruction_page'] == 9:
            request.session['trial_number'] = 1
            request.session['block_number'] = 3
            request.session['Alert System'] = 0
            request.session['default'] = 0
            return redirect('/alert_system/')
        request.session['parameters']['v_tp']
        return render(request=request,
                      template_name='main/Instructions({}).html'.format(request.session['instruction_page']),
                      context={'v_tp': int(request.session['parameters']['v_tp']),
                               'v_fp': -1*int(request.session['parameters']['v_fp']),
                               'v_tn': int(request.session['parameters']['v_tn']),
                               'v_fn': -1*int(request.session['parameters']['v_fn']),
                               'budget': 30-request.session['cost'],
                               'cost': request.session['cost']})


# Game Screen, Display events - number, alarm output (if exist), score, event number etc.
# and the user should classify the events
def game(request):
    param = request.session['parameters']

    # No use of the alerting system in the first test block
    if request.session['block_number'] == 1:
        request.session['Alert System'] = 0
    # Mandatory use of alerting system in the second test block
    elif request.session['block_number'] == 2:
        request.session['Alert System'] = 1
    if request.session['block_number'] == 2 and request.session['trial_number'] == 1:
        request.session['score'] = 30 - request.session['cost']

    # If first event in the block - get the block data
    if request.session['trial_number'] == 1:
        # Get events' data
        events = get_events(request.session['condition'], request.session['block_number'])
        request.session['events'] = events

    # Get the single event data (classification type, alarm output and stimulus)
    signal_or_noise, alarm_or_not, stimulus = get_event_data(request.session['events'], request.session['trial_number'])

    # Participant See the Screen
    if request.method == "GET":
        request.session['start_time'] = time.time()

    # Participant classify the event
    if request.method == "POST":
        request.session['classification_time'] = time.time() - request.session['start_time']

        if request.POST['Classification'] == "No intervention":                     # Classification
            classification = 'N'
            time.sleep(1)
            if signal_or_noise == 'noise':                                          # Noise event
                request.session['logs'].append('{} - POST: True Negative trial {}'.
                                               format(datetime.now(), request.session['trial_number']))
                request.session['score'] += param['v_tn']
            else:                                                                   # Signal event
                request.session['score'] += param['v_fn']
                request.session['logs'].append('{} - POST: False Negative {}'.
                                               format(datetime.now(), request.session['trial_number']))
        elif request.POST['Classification'] == 'Intervention':                      # Signal Classification
            classification = 'S'
            time.sleep(1)
            if signal_or_noise == 'noise':                                          # Noise event
                request.session['score'] += param['v_fp']
                request.session['logs'].append('{} - POST: False Positive {}'.
                                               format(datetime.now(), request.session['trial_number']))
            else:                                                                   # Signal event
                request.session['logs'].append('{} - POST: True Positive {}'.
                                               format(datetime.now(), request.session['trial_number']))
                request.session['score'] += param['v_tp']

        # Update the user classification data
        index = request.session['block_number'] * 100 + request.session['trial_number']
        request.session['block_data'][index] = \
            [request.session['user_id'], request.session['block_number'], request.session['trial_number'],
             signal_or_noise, alarm_or_not, stimulus, request.session['score'], request.session['Alert System'],
             request.session['condition'], classification, request.session['classification_time'], str(datetime.now())]

        # Raise the trial number in 1
        request.session['trial_number'] += 1

        # End of the block
        if request.session['trial_number'] == param['N_test']:
            request.session['logs'].append('{} - POST: Finish Block {}'.
                                           format(datetime.now(), int(request.session['block_number'])))
            # Convert dictionary to pandas and save the user action until this block (including) to CSV file
            df = pd.DataFrame.from_dict(request.session['block_data'], orient='index',
                                        columns=['ID', 'Block', 'Trial', 'Event Type', 'Alarm Output',
                                                 'Stimulus', 'Score', 'Alert System', 'Condition',
                                                 'User Action', 'Classification Time', 'Event Time'])
            df = df[['ID', 'Block', 'Alert System', 'Condition', 'Trial', 'Event Type', 'Stimulus', 'Alarm Output',
                     'User Action', 'Score', 'Classification Time', 'Event Time']]

            df.to_csv('data/per_user/user_{}.csv'.format(request.session['user_id']), index=False)

            # Data for Block Summary Screen (block_points)
            request.session['block_summary'][request.session['block_number']] = \
                [int(request.session['user_id']), int(request.session['block_number']),
                 int(request.session['score']), int(request.session['Alert System']),
                 int(request.session['condition'])]

            # Set Initial values - raise block number in 1, set trial number to 1 and score to 30
            request.session['block_number'] += 1
            request.session['trial_number'] = 1
            request.session['score'] = 30

            # End of Experiment
            if request.session['block_number'] > param['B']:
                return redirect('/end/')
            # End of Block
            elif request.session['block_number'] == 2:
                # Instruction about alerting system
                request.session['instruction_page'] += 1
                return redirect('/block_points/')
            elif request.session['block_number'] == 3:
                # Instruction about purchase alerting system
                request.session['instruction_page'] += 1
                return redirect('/block_points/')
            elif request.session['block_number'] >= 4:
                # Instruction about purchase alerting system
                return redirect('/block_points/')

        signal_or_noise, alarm_or_not, stimulus = get_event_data(request.session['events'],
                                                                 request.session['trial_number'])

    request.session['start_time'] = time.time()

    # Last Trial
    if request.session['block_number'] == request.session['parameters']['B'] and\
       request.session['trial_number'] == request.session['parameters']['N'] - 1:
        saving_alert = 'True'
    else:
        saving_alert = 'False'

    return render(request=request,
                  template_name='main/Game.html',
                  context={'score': int(request.session['score']), 'saving_alert': saving_alert,
                           'Numeric_Value': stimulus,
                           'alert_system':  request.session['Alert System'], 'signal_or_noise': signal_or_noise,
                           'alarm_or_not': alarm_or_not, 'event': int(request.session['trial_number'])})


def block_points(request):
    blocks = request.session['block_summary']
    request.session['logs'].append('{} - Display Points in each Block'.format(datetime.now()))
    if request.method == "POST":
        if request.session['instruction_page'] <= 8:
            return redirect('/instructions/')
        else:
            request.session['Alert System'] = 0
            request.session['default'] = 0
            return redirect('/alert_system/')

    if request.session['instruction_page'] == 5:
        first = 1
    else:
        first = 0
    return render(request=request,
                  template_name='main/BlockPoints.html',
                  context={'blocks': blocks.values(), 'first': first})


def alert_system(request):
    request.session['logs'].append('{} - Alert System Purchase Screen'.format(datetime.now()))

    decision = request.session['Alert System']
    score = request.session['score']
    cost = request.session['cost']
    if request.method == "POST":
        request.session['default'] = 1
        if request.POST['Settings'] == 'Purchase the alert system':
            request.session['logs'].append('{} - Alert System Purchase Screen - Purchase'.format(datetime.now()))
            request.session['Alert System'] = 1
            request.session['score'] = 30 - cost
            return redirect('/alert_system/')
        if request.POST['Settings'] == 'Do not purchase the alert system':
            request.session['logs'].append('{} - Alert System Purchase Screen - not Purchase'.format(datetime.now()))
            request.session['Alert System'] = 0
            request.session['score'] = 30
            return redirect('/alert_system/')
        if request.POST['Settings'] == 'Confirm':
            request.session['logs'].append('{} - Alert System Purchase Screen - Confirm button'.format(datetime.now()))
            request.session['default'] = 0
            request.session['start_time'] = time.time()
            return redirect('/game/')
    if request.method == "GET":
        default = request.session['default']
        return render(request=request,
                      template_name='main/Alert_System.html',
                      context={'Alert_System': decision, 'score': score, 'cost': cost, 'default': default})


def end(request):
    request.session['logs'].append('{} - End Screen'.format(datetime.now()))

    if request.session['block_number'] > request.session['parameters']['B']:
        request.session['finish'] = True
    else:
        request.session['finish'] = False

    user_id = request.session['user_id']
    condition = request.session['condition']
    code = request.session['code']
    experiment_start_time = request.session['experiment_start_time']
    experiment_time = round((time.time() - experiment_start_time)/60, 4)

    with open("data/log files/user {} logs file.txt".format(user_id), "w") as output:
        output.write(str(request.session['logs']))

    if request.session['finish']:
        # Payment
        PaymentCode.objects.create(user_id=user_id, time=experiment_time, condition=condition, payment_code=code)
        # Classification data
        data = request.session['block_data']
        df = pd.DataFrame.from_dict(data, orient='index',
                                    columns=['ID', 'Block', 'Trial', 'Event Type', 'Alarm Output',
                                             'Stimulus', 'Score', 'Alert System', 'Condition',
                                             'User Action', 'Classification Time', 'Event Time'])
        df = df[['ID', 'Block', 'Alert System', 'Condition', 'Trial', 'Event Type', 'Stimulus', 'Alarm Output',
                 'User Action', 'Score', 'Classification Time', 'Event Time']]
        df = df.drop_duplicates(['ID', 'Block', 'Alert System', 'Condition', 'Trial', 'Event Type', 'Stimulus',
                                 'Alarm Output', 'User Action', 'Score', 'Classification Time', 'Event Time'])

        for index, row in df.iterrows():
            Classification.objects.create(user_id=row['ID'], block=row['Block'], trial=row['Trial'],
                                          event_type=row['Event Type'], stimulus=row['Stimulus'],
                                          alarm_output=row['Alarm Output'], user_action=row['User Action'],
                                          score=row['Score'], alert_system=row['Alert System'],
                                          condition=row['Condition'], classification_time=row['Classification Time'],
                                          event_time=row['Event Time'])

    aid = request.session['aid']
    return render(request=request,
                  template_name='main/End.html',
                  context={'finish': request.session['finish'], 'code': code, 'aid': aid})


def server(request):
    if request.method == "POST":
        user_name = request.POST['user name']
        password = request.POST['password']
        if user_name == 'Administrator' and password == '0571JyY':
            if request.POST['setting'] == 'DB':
                save_db()
                return render(request=request, template_name='main/Successful.html')
            elif request.POST['setting'] == 'Parameters':
                return redirect('/parameters/')
            elif request.POST['setting'] == 'Progress':
                return redirect('/progress/')
            elif request.POST['setting'] == 'Other':
                return render(request=request,
                              template_name='main/Server.html',
                              context={'flag': 1})
            elif request.POST['setting'] == 'ok':
                for participant in Participant.objects.all():
                    participant.delete()
                for block in Block.objects.all():
                    block.delete()
                for classification in Classification.objects.all():
                    classification.delete()
                for code in PaymentCode.objects.all():
                    code.delete()

    return render(request=request,
                  template_name='main/Server.html',
                  context={'flag': 0})


def parameters(request):
    if request.method == "POST":
        user_name = request.POST['user name']
        password = request.POST['password']
        if user_name == 'Administrator' and password == '0571JyY':
            if request.POST['Set parameters'] == 'Set parameters':
                blocks = request.POST['number of blocks']
                events = request.POST['number of events']
                test_events = request.POST['number of test events']
                ps = request.POST['probability to signal']
                v_tp = request.POST['v_tp']
                v_fp = request.POST['v_fp']
                v_fn = request.POST['v_fn']
                v_tn = request.POST['v_tn']
                d = request.POST["d'"]
                parameters_dict = {'blocks': blocks, 'events': events, 'test_events': test_events, 'ps': ps,
                                   'v_tp': v_tp, 'v_fp': v_fp, 'v_fn': v_fn, 'v_tn': v_tn, 'dprime': d}
                save_parameters = pd.DataFrame.from_dict(parameters_dict, orient='index')
                save_parameters.to_csv('parameters/parameters.csv', index=True)
                return render(request=request, template_name='main/Successful.html')
    return render(request=request,
                  template_name='main/Parameters.html')


def save_db():
    users_dict = {}
    payment_dict = {}
    actions_dict = {}
    blocks_dict = {}

    index = 0
    for user in Participant.objects.all():
        users_dict[index] = [user.user_id, user.condition, user.date, user.ip, user.aid]
        index += 1
    users = pd.DataFrame.from_dict(users_dict, orient='index', columns=['ID', 'condition', 'date', 'ip', 'aid'])
    users = users.drop_duplicates(['ID', 'condition', 'date', 'ip', 'aid'])
    users = users[['ID', 'aid', 'condition', 'date', 'ip']]

    index = 0
    for user in PaymentCode.objects.all():
        payment_dict[index] = [user.user_id, user.time, user.condition, user.payment_code]
        index += 1
    payments = pd.DataFrame.from_dict(payment_dict, orient='index', columns=['ID', 'time', 'condition', 'payment_code'])
    payments = payments.drop_duplicates(['ID', 'payment_code'])

    index = 0
    for action in Classification.objects.all():
        actions_dict[index] = [action.user_id, action.block, action.alert_system, action.condition,
                               action.trial, action.event_type, action.alarm_output,
                               action.stimulus, action.score, action.user_action,
                               action.classification_time, action.event_time]
        index += 1
    actions = pd.DataFrame.from_dict(actions_dict, orient='index',
                                     columns=['ID', 'Block', 'Alert System', 'Condition', 'Trial', 'Event Type',
                                              'Alarm Output', 'Stimulus', 'Score', 'User Action', 'Classification Time',
                                              'Event Time'])
    actions = actions.drop_duplicates(['ID', 'Block', 'Alert System', 'Condition', 'Trial', 'Event Type',
                                       'Alarm Output', 'Stimulus', 'Score', 'User Action', 'Classification Time',
                                       'Event Time'])

    index = 0
    for block in Block.objects.all():
        blocks_dict[index] = [block.user_id, block.block, block.score, block.alert_system, block.condition]
        index += 1
    blocks = pd.DataFrame.from_dict(blocks_dict, orient='index',
                                    columns=['ID', 'Block', 'Score', 'Alert System', 'Condition'])
    blocks = blocks.drop_duplicates(['ID', 'Block', 'Score', 'Alert System', 'Condition'])

    users.to_csv('data/users.csv', index=False)
    payments.to_csv('data/payments.csv', index=False)
    actions.to_csv('data/actions.csv', index=False)
    blocks.to_csv('data/blocks.csv', index=False)


def progress(request):
    payments = pd.read_csv('data/payments.csv')
    users = pd.read_csv('data/users.csv').shape[0]
    users_completed = payments.shape[0]
    condition_1 = payments[payments['condition'] == 1].shape[0]
    condition_2 = payments[payments['condition'] == 2].shape[0]
    condition_3 = payments[payments['condition'] == 3].shape[0]
    mean_time = round(payments.time.mean(), 2)
    std_time = round(payments.time.std(), 2)

    return render(request=request,
                  template_name='main/Progress.html',
                  context={'users': users, 'completed_users': users_completed, 'mean_time': mean_time,
                           'std_time': std_time,
                           'condition_1': condition_1, 'condition_2': condition_2, 'condition_3': condition_3})
