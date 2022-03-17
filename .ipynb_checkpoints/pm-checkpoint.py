import numpy as np
import pandas as pd
import sys
import time
import datetime
import re
import subprocess
import argparse
#==========================================================================================================
#----------------VARIABLES-----------------
#------CONFIG
import config as cfg
instrument_dictionnary = cfg.instr
#---------------------------------------
data = pd.read_csv("data.csv",index_col='ID')

labels = ["ID", "practice", "instrument", "tags", "description", "links", "priority", "status", "creation_date", "log"]

parser = argparse.ArgumentParser(description='PracticeMakePerfect (pmp)')
parser.add_argument('-a','--add',
parser.add_argument('-d','--del',
parser.add_argument('-c','--change',
parser.add_argument('-m','--mod',
parser.add_argument('-l','--ls',
parser.add_argument('-p','--pr'
parser.add_argument('-r','--record'
parser.add_argument('-s','--stat',
parser.add_argument('-z','--undo',
parser.add_argument('-h','--help',
    
    
cmds = {"add": create_practice,
        "del": delete_practice,
        "switch": change_practice_status,
        "mod": modify_practice,
        "ls": list_practices,
        "p": practice,
        "rec": change_count,
        "stat": show_stats,
        "undo": undo_last_edit,
        "help": help_} 
'''    
=================================================================================           
 ==================================================================================
 ''')
#==========================================================================================================
#------------USER FUNCTIONS----------------

#create practice
def create_practice(f):
    '''self explanatory'''
    t = {i:[] for i in labels}
    t['ID'] = min([i for i in range(1,1000) if i not in list(data['ID'])])
    for element in {'practice':'Practice needs a name\n','instrument':'You need to chose an instrument\n'}.items():
        try:
            t[element[0]] = [f[element[0]]]
        except KeyError:
            print(element[1])
            return
    try:
        t['instrument'] = [' '.join(f['instrument'])]
    except KeyError:
        print('You need to chose an instrument\n')
        return
    for element in ['tags','description','links']:
        try:
            t[element] = f[element]
        except KeyError:
            t[element] = ['']
    t['status'] = [0]
    t['priority'] = [1]  
    t['creation_date'] = [time.time()]
    t['log'] = ['']
    df = pd.DataFrame(t)
    ndf = pd.concat([data,df],ignore_index=True)
    print(ndf.tail(10))
    if input("Confirm?\n").capitalize() in 'YES':
        df.to_csv('backup.csv',index=False)
        ndf.to_csv("data.csv",index=False)
        print(f"Practice {t['ID']} created\n")

def delete_practice(f):
    '''idem'''
    try:
        dd = data[data['ID']!=int(f['ID'])]
        print(data)
        if int(f['ID'] in list(data['ID'])):
            if input('Confirm?\n').capitalize() in 'YES':
                data.to_csv('backup.csv',index=False)
                dd.to_csv('data.csv',index=False)
                print(dd)
                print(f"Practice {f['ID']} deleted")
        else:
            print(f"Practice {f['ID']} doesn't exist")
    except:
        print('Invalid ID')


#list practices (based on filters, ranked by most done + priority)
def list_practices(f):
    '''list practices'''
    ls_data = data.sort_values(by=['priority'],ascending=False)
    if 'instrument' in f.keys():
        ls_data = ls_data[ls_data['instrument'] == f['instrument']]
    if 'tags' in f.keys():
        taglist =  f['tags']
    print(data)

#give random practice (filtered with tags,instrument) based on instrument type and number of practice from activated task (need to figure out a weight system)
#open link if accepted and mark as done
def practice(f):
    '''give assignment based on priority and/or filtering option, launch files if any and mark as done once'''
    return

#note practice session (ask if archive if >10 times)
def change_count(f):
    '''mark practice as done'''
    return

#practice status (active to inactive)
def change_practice_status(f):
    '''activate or inactivate practices'''
    return

def modify_practice(f):
    '''modify practice'''
    return

def show_stats(f):
    ''''''
    return

def undo_last_edit(f):
    subprocess.run('mv backup.csv temp.csv'.split(' '))
    subprocess.run('mv data.csv backup.csv'.split(' '))
    subprocess.run('mv temp.csv data.csv'.split(' '))
    
    
#-------PROGRAM FUNCTIONS
def update():
    pass
#==========================================================================================

