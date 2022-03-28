#!/usr/bin/python

import re
import datetime
import os
import sys
import requests

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
dateobj = datetime.date(2021, 6, 19)
delta = datetime.date.today()-dateobj
wordle_no = delta.days
todays_word = words[wordle_no]

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

##############################################################
#                 Wordle
##############################################################
def get_coloured(word):
    # return word with letters coloured according to today's word
    buff = '  '
    for i in range(5):
        if word[i] == todays_word[i]:
            buff += Colour.REVERSE + Colour.GREEN + word[i].upper() + ' ' + Colour.RESET
        elif word[i] in todays_word:
            buff += Colour.REVERSE + Colour.YELLOW + word[i].upper()  + ' '+ Colour.RESET
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
        print(get_coloured(attempts[i]))

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
    print('\nGame Over!\n')
