import os
from os.path import join
import time
import json
import random
import pandas as pd
from collections import OrderedDict
from sklearn.utils import shuffle
from psychopy import core, visual, event, data, gui
from psychopy.hardware import keyboard  
from port_open_send import sendTrigger 

# === GUI Setup === #
dlg_info = OrderedDict([
    ('Participant ID', ''),
    ('Experiment Type', ['full', 'practice']),
    ('Fullscreen', False),
    ('Diode on?', True),
    ('Send triggers?', True),
    ('Auto respond?', False)
])
dlg = gui.DlgFromDict(dictionary=dlg_info, title='Experiment Settings')
if not dlg.OK:
    core.quit()

expt = 'ColorGreen'
debug = False
verbose = True
use_frame_rate = True
participant_name = dlg_info['Participant ID']
stimuli_select = dlg_info['Experiment Type']
fullscr = dlg_info['Fullscreen']
practice = True if stimuli_select == 'practice' else False
toggle_diode = dlg_info['Diode on?']
send_triggers = dlg_info['Send triggers?']
simulate_responses = dlg_info['Auto respond?']

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = DIR

trials = None
try:
    with open(join(DIR, 'config', 'colorgreen.json'), 'r') as f:
        config = json.load(f)
except Exception as e:
    print(f"Error loading config: {e}")
    core.quit()

# === Text Snippets === #

setup_text = config['text']['setup']
instruction_text = config['text']['instructions'] if not practice else config['text']['practice']
end_text = config['text']['end']

setup_proceed_key = config['keys']['setup_proceed']
instruction_proceed_keys = config['keys']['instruction_proceed']

# === Trigger Mapping === #
trigger_map = config['send_triggers']['map']

# === Load Stimuli === #
try:
    stimuli_fn = join('stimuli', config['experiment']['stimuli']['full']) if stimuli_select == 'full' else join('stimuli', config['experiment']['stimuli']['practice'])
    stimuli_path = join(ROOT, stimuli_fn)
    trials = pd.read_csv(stimuli_path)
except Exception as e:
    print(f"Error loading stimuli: {e}")
    core.quit()

# === Block Setup === #
if stimuli_select == 'full':
    n_blocks, n_trials_per_block = config['blocks']['count'], config['blocks']['trials_per_block']
else:
    n_blocks, n_trials_per_block = 1, 6

trials = shuffle(trials).reset_index(drop=True)
trials['blockID'] = [i // n_trials_per_block for i in range(len(trials))]
block_order = list(range(n_blocks))

# === Logging === #
exp = None
if participant_name:
    dir_logs = join(ROOT, 'logs', participant_name)
    if not os.path.exists(dir_logs):
        os.makedirs(dir_logs)
    log_fn = join(dir_logs, f'{participant_name}_{expt}_logfile')
    exp = data.ExperimentHandler(dataFileName=log_fn, autoLog=False, savePickle=False)

# === Display Setup === #
win = visual.Window(monitor='default', units='pix', checkTiming=True, fullscr=fullscr, colorSpace='rgb255', color=(127,127,127))
sentence = visual.TextStim(win, text='', height=20, font='Courier New', wrapWidth=700, alignText='center', color=(1,1,1))
answer_text = visual.TextStim(win, text='', font='Courier New', alignText='center', color=(1,1,1))
fixation = visual.TextStim(win, text='+', height=35, color=(1,1,1))
photodiode = visual.Rect(win, width=57, height=57, pos=[-483,355], fillColor=[255,255,255], fillColorSpace='rgb255')
instructions = visual.TextStim(win, text='', font='Courier New', wrapWidth=700, alignText='center', height=18, color=(1,1,1))

proceed = keyboard.Keyboard()
trialClock = core.Clock()
clock = core.Clock()
win.mouseVisible = False

# === Timing Setup === #

frame_time_ms = win.monitorFramePeriod * 1000

fixation_ON_ms = config['timing']['fixation_ON_ms']
fixation_OFF_ms = config['timing']['fixation_OFF_ms']
sent_ON_ms = config['timing']['prime_ON_ms']
sent_OFF_ms = config['timing']['prime_OFF_ms']

fixation_ON_s = fixation_ON_ms / 1000
fixation_OFF_s = fixation_OFF_ms / 1000
sent_ON_s = sent_ON_ms / 1000
sent_OFF_s = sent_OFF_ms / 1000

# === Helper Functions === #
def present_text(text='', proceed_keys=['s'], simulate_responses=False, allow_pause=False):
    instructions.setText(text)
    instructions.draw()
    win.flip()
    keys = event.waitKeys(keyList=proceed_keys + (['p', 'q'] if allow_pause else []))
    if keys[0] == 'q': 
        present_text(end_text, ['s'])
        core.quit()
    if keys[0] == 'p': pause()
    return keys[0]

def pause():
    present_text("Experiment paused. Wait for experimenter to continue.", proceed_keys=['s'], allow_pause=False)

def is_match_trial(trial):
    return trial['match_manip'] == 'SAME'

def after_trial_pause(jitter, use_frame_rate=True):
    if use_frame_rate:
        jitter_frames = int(jitter / frame_time_ms + 1)
        for _ in range(jitter_frames):
            win.flip()
    else:
        win.flip()
        core.wait(jitter / 1000)

def present_fixation(use_frame_rate, verbose=True):
    start_time = time.time()
    
    if use_frame_rate:
        for _ in range(int(fixation_ON_ms / frame_time_ms + 1)):
            fixation.draw()
            win.flip()
        for _ in range(int(fixation_OFF_ms / frame_time_ms + 1)):
            win.flip()
    else:
        fixation.draw()
        win.flip()
        core.wait(fixation_ON_s)
        win.flip()
        core.wait(fixation_OFF_s)

    if verbose:
        end_time = time.time()
        onscreen_time_ms = (end_time - start_time) * 1000
        print(f'Fixation onscreen time: {onscreen_time_ms:.2f} ms')
        print(f"Fixation presented using {'frame rate' if use_frame_rate else 'core.wait'}")

def map_condition_to_trigger(condition_code):
    return trigger_map[condition_code]

def present_sentence(trial, use_frame_rate=True, send_trigger=True, verbose=True):
    try:
        
        sentence.setText(trial['prime'])
        sentence.draw()
        if toggle_diode:
            photodiode.draw()

        if send_trigger:
            current_trigger = map_condition_to_trigger(trial['condition_label'])
            win.callOnFlip(trialClock.reset)
            win.callOnFlip(sendTrigger, channel=current_trigger, duration=0.02)
            if verbose:
                print(f"Sending trigger: {current_trigger} for condition: {trial['condition_label']}")

        start_time = time.time()

        if use_frame_rate:
            win.flip()
            for _ in range(int(sent_ON_ms / frame_time_ms)):
                sentence.draw()
                if toggle_diode:
                    photodiode.draw()
                win.flip()
            for _ in range(int(sent_OFF_ms / frame_time_ms + 1)):
                win.flip()
        else:
            win.flip()
            core.wait(sent_ON_s)
            win.flip()
            core.wait(sent_OFF_s)

        if verbose:
            end_time = time.time()
            total_time_ms = (end_time - start_time) * 1000
            print(f'Total stimulus presentation time: {total_time_ms:.2f} ms')

    except Exception as e:
        print(f"Error in present_sentence: {e}")
        raise

def present_answer(trial, simulate_responses=False):
    try:
        display_text = trial['prime'] if is_match_trial(trial) else trial['target']
        
        answer_text.setText(display_text)
        answer_text.draw()
        photodiode.draw()
        win.flip()
        response_start = time.time()

        if simulate_responses:
            answer = str(random.randint(1, 2))
            core.wait(random.uniform(0.5, 0.9))
            response_end = time.time()
            return answer, response_end - response_start

        answer = event.waitKeys(maxWait=0.3, keyList=['1', '2', 'q', 'p'])
        
        if answer is None:
            win.flip()
            answer = event.waitKeys(keyList=['1', '2', 'q', 'p'])
            if not answer or answer[0] == 'q':
                present_text(end_text, ['s'])
                core.quit()
            elif answer[0] == 'p':
                pause()
                print('Experiment paused...')
                return ('p', time.time() - response_start)
            response_end = time.time()
            return answer[0], response_end - response_start
            
        response_end = time.time()
        return answer[0], response_end - response_start

    except Exception as e:
        print(f"Error in present_answer: {e}")
        raise

def run_block(block_trials):
    global trial_num, total_correct
    for _, trial in block_trials.iterrows():
        present_fixation(use_frame_rate)
        present_sentence(trial)
        answer, rt = present_answer(trial)
        
        # Generate jitter value first, then use it
        jitter_time = random.uniform(0.5, 0.9)
        trial['jitter'] = jitter_time  # Store the value for data logging
        
        # Use the jitter value for waiting
        after_trial_pause(jitter_time * 1000, use_frame_rate)  # Convert to ms
        
        correct = (is_match_trial(trial) and answer == '2') or (not is_match_trial(trial) and answer == '1')
        total_correct += int(correct)
        
        if verbose:
            print(f"Current Trial: {trial_num} / {trials.shape[0]}")
            print(f"Original Stimulus: {trial['prime']}")
            print(f"Presented Stimulus: {trial['target'] if not is_match_trial(trial) else trial['prime']}")
            print(f"Answer Given: {answer}")
            print(f"Correct? {correct}")
            print(f"Reaction Time: {rt}")
            print(f"Cumulative Accuracy: {total_correct / (trial_num + 1)}")
            print()
            
        if exp:
            # Add basic data fields
            exp.addData('Participant', participant_name)
            exp.addData('Trial_num', trial_num)
            exp.addData('Answer', answer)
            exp.addData('Correct', correct)
            exp.addData('RT', rt)
            exp.addData('Jitter', trial['jitter'])
            
            # Dynamically add all fields from the trial dataframe
            for column in trial.index:
                exp.addData(column, trial[column])
                
            exp.nextEntry()
        trial_num += 1

# === Run Experiment === #
present_text(setup_text, setup_proceed_key)
present_text(instruction_text, instruction_proceed_keys)

trial_num = 0
block_num = 0
total_correct = 0
experiment_start = time.time()

for block_id in block_order:
    try:
        run_block(trials[trials.blockID == block_id])
        block_num += 1
        if block_num == 4:
            present_text("End of block 4. Wait for experimenter to continue.", ['s'])
        present_text(f"End of block {block_num}. Press any key to continue.", ['1', '2', 's', 'q'])

        experiment_time_s = time.time() - experiment_start
        accuracy = (total_correct / trials.shape[0]) * 100
        present_text(end_text, ['s'])

        core.quit()

    except Exception as e:
        print(f"Error in experiment: {e}")
    finally:
        # Calculate and display final statistics
        experiment_end = time.time()
        experiment_time_s = experiment_end - experiment_start
        experiment_time_min = experiment_time_s / 60.0
        accuracy = (total_correct / trials.shape[0]) * 100
        
        if verbose:
            print(f"Total Experiment Time in seconds: {experiment_time_s}")
            print(f"Total Experiment Time in minutes: {experiment_time_min}")
            print(f"Accuracy: {accuracy}%")