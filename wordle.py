#!/usr/bin/python

import re
import datetime
import os
import sys
import json
import clipboard
import requests

#############################################################
#                    Coloured Print
#############################################################
class Colour:
    RED = '\033[31m'
    GREEN = "\033[32m"
    YELLOW = '\033[33m'
    BOLD = '\033[1m'
    RESET = "\033[0;0m"
    REVERSE = "\033[7m"

def cprint(text, col):
    # print coloured output to terminal
    if col.lower() == 'green':
        modifier = Colour.GREEN
    elif col.lower() == 'yellow':
        modifier = Colour.YELLOW
    elif col.lower() == 'red':
        modifier = Colour.RED
    else:
        print('Error printing colours, exitting.')
        sys.exit(-1)

    print(modifier + text + Colour.RESET)

#############################################################
#               Functions to check history
#############################################################
HISTORY_DIR = os.path.expanduser('~/.cache') + '/terminal-wordle/'
HISTORY_FILE = HISTORY_DIR + 'history'

def show_stats(hist_arr, end=False):
    # Show stats in aa bar graph
    # end=True means close script
    solves = [0,0,0,0,0,0]
    for i in hist_arr:
        if isinstance(i['attempt'], int):
            solves[int(i['attempt']) -1] += 1

    print('\nResult:')
    total_solved = sum(solves)
    if total_solved == 0:
        total_solved = 1
    for i in range(len(solves)):
        if not isinstance(i, int):
            continue
        print(Colour.BOLD + f'{i+1}:  ' + Colour.RESET, end='')
        for j in range(int(solves[i] *15/total_solved)):
            print(Colour.GREEN + Colour.REVERSE + ' ' + Colour.RESET, end='')

        print('')

    if end:
        sys.exit(0)

#############################################################
#                   Check if solved today
#############################################################
history = ''
file_exists = True
if not os.path.exists(HISTORY_FILE):
    os.system(f'mkdir -p {HISTORY_DIR}')
    os.system(f'touch {HISTORY_FILE}')
    file_exists = False

if file_exists:
    with open(HISTORY_FILE, 'r') as f:
        history = f.read()
        if history != '':
            try:
                hist_arr = json.loads(history)
                if isinstance(hist_arr, dict):
                    #convert to array
                    hist_arr = [hist_arr]
                for i in hist_arr:
                    if i['date'] == str(datetime.date.today()):
                        print(f'It seems you already played it today. Solved in {i["attempt"]} attempt(s).')
                        show_stats(hist_arr, end=True)
            except json.JSONDecodeError:
                #corrupted data, clear it
                history = ''

#############################################################
#                    Getting Wordle Word
#############################################################

# parsing js and getting all words, allowed words
mainjs = 'https://www.nytimes.com/games/wordle/main.3d28ac0c.js'

r = requests.get(mainjs)

quotes = re.compile(r'\"')

# variables in js
varma = 'var Ma=['
oa = '],Oa=['
ra = '],Ra='

content = str(r.content)

start_ma = content.find(varma) + len(varma)
end_ma = content.find(oa)
start_oa = end_ma + len(oa)
end_oa = content.find(ra)

# words = list of all wordle words
# allowed = list of allowed words
words = content[start_ma:end_ma].split(",")
allowed_words = content[start_oa:end_oa].split(",")

for i in range(len(words)):
    word = words[i]
    words[i] = re.sub(quotes, '', word)

for i in range(len(allowed_words)):
    word = allowed_words[i]
    allowed_words[i] = re.sub(quotes, '', word)

# getting today's word
dateobj = datetime.date(2021, 6, 19) #first wordle
delta = datetime.date.today()-dateobj
wordle_no = delta.days
todays_word = words[wordle_no]

##############################################################
#                 Wordle
##############################################################
def get_coloured(word, emoji):
    GREEN_EMOJI = '🟩'
    YELLOW_EMOJI = '🟨'
    BLACK_EMOJI = '⬛'
    buff = '  ' #2 spaces so it is visible aligned

    # return word with letters coloured according to today's word
    for i in range(5):
        if word[i] == todays_word[i]:
            if emoji:
                buff += GREEN_EMOJI
            else:
                buff += Colour.REVERSE + Colour.GREEN + word[i].upper() + ' ' + Colour.RESET
        elif word[i] in todays_word:
            if emoji:
                buff += YELLOW_EMOJI
            else:
                buff += Colour.REVERSE + Colour.YELLOW + word[i].upper()  + ' '+ Colour.RESET
        else:
            if emoji:
                buff += BLACK_EMOJI
            else:
                buff += word[i].upper() + ' '

    return buff

wrong_len = False
solved = False
not_allowed = False
attempts = []
while True:
    os.system('clear')
    if wrong_len:
        print(Colour.RED + 'Enter a 5 letter word!\n' + Colour.RESET)
        wrong_len = False
        not_allowed = False

    if not_allowed:
        print(Colour.RED + 'Not a valid word!\n' + Colour.RESET)
        not_allowed = False

    print(Colour.BOLD + f'  Wordle {wordle_no}' + Colour.RESET + '\n\n')

    for i in range(len(attempts)):
        print(get_coloured(attempts[i], emoji=False))

    if solved:
        print(f'\nCongrats!\nSolved in {len(attempts)}/6 attempts\n')
        break

    if len(attempts) >= 6:
        print('')
        break

    for i in range(6 - len(attempts) ):
        print(Colour.BOLD + '  _ _ _ _ _\n' + Colour.RESET)

    inp_word = input('> ').lower()
    if len(inp_word) != 5:
        wrong_len = True
        continue

    if inp_word not in allowed_words and inp_word not in words:
        not_allowed = True
        continue

    attempts.append(inp_word)
    if inp_word == todays_word:
        solved = True

if not solved:
    print(f'\nGame Over!\nCorrect Word: {Colour.BOLD}{todays_word.upper()}{Colour.RESET}')

# Copy result in Wordle format
if solved:
    no_attempts = len(attempts)
else:
    no_attempts = 'X'

clip_data = f'Wordle {wordle_no} {no_attempts}/6\n\n'
for attempt in attempts:
    clip_data += get_coloured(attempt, emoji=True) + '\n'

clipboard.copy(clip_data)
print('Copied result to clipboard!')

#############################################################
#                   Saving data
#############################################################

current = dict()
current['date'] = str(datetime.date.today())
current['attempt'] = no_attempts

history += json.dumps(current)
with open(HISTORY_FILE, 'w') as f:
    f.write(history)

hist_arr = json.loads(history)
if isinstance(hist_arr, dict):
    hist_arr = [hist_arr]
show_stats(hist_arr, end=True)
