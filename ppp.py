#! /bin/python3

import numpy as np
import pandas as pd
import sys
import os
import time
import datetime
import re
import subprocess
import argparse
import yaml
import random
from tabulate import tabulate
#==========================================================================================================

class Practice:
    """Blabla."""

    def __init__(self):
        with open('config.yaml') as f:
            config            = yaml.load(f, Loader=yaml.FullLoader)
            self.__dict__.update(config)
        self.data             = self._getdata("practices.csv")
        self.backup           = self._getdata("backup.csv")
        self.obj              = None
        self.excluded_columns = ['description','links','created','log']
        self._check_and_archive()
        self._update()

    def _getdata(self,path):
        if path not in os.listdir('.'):
            df = pd.DataFrame({i:[] for i in self.labels})
            df.index.name = 'ID'
            return df
        else:
            return pd.read_csv(path,index_col=0,converters={'ID':int})

    def _update(self):
        for i in self.data.index:
            self.data.loc[i,'urg'] = self._calculate_urgency(i,self.data)
            self._save()

    def _save(self):
        self.backup.to_csv('backup.csv')
        self.data.to_csv("practices.csv")

    def _list(self,thg):
        if type(thg) == list:
            if len(thg) >= 1:
                return [' '.join(thg)]
            else:
                return thg
        elif type(thg) in [str,float,int]:
            return [thg]
        elif not thg:
            return ['']

    def _list_many(self,listlist):
        for i in listlist:
            self.__dict__[i] = self._list(self.__dict__[i])

    def _niceprint(self,
                   df = 'default',
                   exclude='default',
                   sort=False,
                   head=False,
                   tail=False,
                   ascending=False,
                   drop_list=None,
                   one=False):
        if type(df) == str:
            if df == 'default':
                df = self.data.copy()
        if one:
            if one in df.index:
                df = df.loc[one,:]
        if drop_list:
            df.drop(drop_list,inplace=True)
        if exclude == 'default' : exclude = self.excluded_columns
        if exclude != None:
            df.drop(columns=exclude,inplace=True)
        if sort:
            df.sort_values(sort,ascending=ascending,inplace=True)
        if tail:
            df = df.tail(tail)
        if head:
            df = df.head(head)
        print(tabulate(df, headers='keys', tablefmt='psql', showindex=True))

    def _check_and_archive(self):
        self.backup = self.data.copy()
        for i in self.data.index:
            if self.data.loc[i,'status'] == 1:
                count = self.data.loc[i,'count']
                goal = self.data.loc[i,'goal']
                if count >= goal:
                    self.view(manual=i)
                    inp = input(f"[Archive practice? ({int(count)}/{int(goal)})]\nUpdate goal?\n")
                    if inp.isnumeric():
                        self.data.loc[i,'goal'] = int(inp)
                    else:
                        self.data.loc[i,'status'] = 2
                    self._save()
                    self._update()
                    self.view(manual=i)


    def _calculate_urgency(self,ID,df):
        if ID not in df.index:
            return
        urgency = 0
        p = df.loc[ID,:]
        if p['status'] != 1:
            return 0
        tags = p['tags']
        instr = p['instrument'].split(' ')
        if type(tags) == str:
            tags = tags.split(' ')
            for t in tags:
                if t in self.special_tags.keys():
                    urgency += self.special_tags[t]
        for i in instr:
            if i in self.instruments.keys():
                urgency += self.instruments[i]
        urgency += self.categories[p['category']]
        urgency *= 2-(abs(p['goal']-p['count'])/p['goal'])
        urgency *= self.priorities[p['priority']]
        urgency *= 1 + abs(time.time() - p['created'])/self.time_constant
        return round(urgency/100,3)

    def _format_date(self,date):
        try:
            if type(date) in [int,float,np.float64,np.int64]:
                return str(datetime.datetime.fromtimestamp(date)).split('.')[0]
            if type(date) == str:
                last = int(date.split(' ')[-1],16)
                return self._format_date(last)
            else:
                return [self._format_date(i) for i in date]
        except:
            return None

    def _calculate_inactive(self):
        df = self.data.copy()
        df.drop(df[df['status'] != 0].index,inplace=True)
        df['status'] = [1]*len(df)
        for i in df.index:
            df.loc[i,'urg'] = self._calculate_urgency(i,df)
        return df

    def _practice_picker(self):
        choosing_list = []
        df = self.data.copy()
        for i in df.index:
            if df.loc[i,'status'] == 1:
                for thing in ['instrument', 'category', 'length']:
                    if self.__dict__[thing]:
                        if df.loc[i,thing] != self.__dict__[thing]:
                            df.drop([i],inplace=True) 
                choosing_list += [i]*round(1000*self.data.loc[i,'urg'])
        pick = random.choice(choosing_list)
        return pick

    def next(self):
        """Find next practice to activate."""
        df = self._calculate_inactive()
        self._niceprint(df=df,exclude='default',
                       sort=['urg'],
                       head=self.verbosity[self.verbose],
                       tail=None)

    def add(self):
        """Add practice session."""
        self.backup = self.data.copy()
        if not self.category:
            print(f"You need to pick a category among {', '.join(self.categories)}.") ; return
        if not self.name:
            print("You need to pick a practice name.") ; return
        if not self.instrument:
            print("You need to choose an instrument.") ; return
        if not self.length:
            self.length = [2]
        self._list_many(listlist=['category','name','instrument','tags','description','links','priority','status'])
        self.ID = [i for i in range(1,1000) if i not in self.data.index][:1]
        if type(self.ID[0]) != int: self.ID = [1]
        for thing in ['goal','status','priority']:
            if self.__dict__[thing] in [[''],None]:
                self.__dict__[thing] = [self.__dict__['default_'+thing]]
        t = {'category'      : self.category,
             'name'          : self.name,
             'instrument'    : self.instrument,
             'tags'          : self.tags,
             'description'   : self.description,
             'links'         : self.links,
             'priority'      : self.priority,
             'status'        : self.status,
             'created'       : [round(time.time())],
             'count'         : [0],
             'goal'          : self.goal,
             'urg'           : [0],
             'length'        : self.length,
             'log'           : ['start']}
        df = pd.DataFrame(t,index=self.ID)
        df.index.name = 'ID'
        self.data = pd.concat([self.data,df])
        self._update()
        self._niceprint(tail=10)
        self.view()
        print('\n',f"Practice {self.ID} successfully created!")


    def delete(self):
        """Delete practice with inputed ID."""
        self.backup = self.data.copy()
        for i in self.ID:
            if i in self.data.index:
                self.data.drop(index=[i],inplace=True)
            else:
                print(f'No practice with ID {i}')
        self._save()
        self._niceprint(tail=10)

    def mod(self):
        """Modify practice."""
        self.backup = self.data.copy()
        for i in self.labels:
            print(i,' : ', self.__dict__[i])
        if self.ID:
            for ID in self.ID:
                if ID in self.data.index:
                    for value in self.modifiable:
                        if self.__dict__[value]:
                            new_value = self.__dict__[value]
                            if type(new_value) == list:
                                self.data.loc[ID,value] = ' '.join(new_value)
                            else:
                                self.data.loc[ID,value] = new_value
                            print('Successfully modified.')
                    self.view(manual=ID)
            self._save()

    def view(self,manual=False):
        """View practice."""
        if manual: ID = [int(manual)]
        else: ID = self.ID
        if type(ID) == list:
            if len(ID) > 0:
                if ID[0] in self.data.index:
                    self.obj = self.data.loc[ID[0],:]
                    print(f"""
{'=' * (len(str(ID[0]))+42+len(self.obj['name']))}
({ID[0]}) {int(self.obj['status'])} {self.obj['name']:>39}
{int(self.obj['count'])}/{int(self.obj['goal']):<10} priority: {self.obj['priority']} urgency: {self.obj['urg']}
lenght: {self.obj['length']}
{'=' * (len(str(ID[0]))+42+len(self.obj['name']))}

*CATEGORY*
{self.obj['category']:<30}

*INSTRUMENT(S)*
{self.obj['instrument']:<30}

*TAGS*
{self.obj['tags']}
{'_' * (len(str(ID[0]))+42+len(self.obj['name']))}

{self.obj['description']}
{'_' * (len(str(ID[0]))+42+len(self.obj['name']))}

*LINKS*
{self.obj['links']}

*CREATED*
{self._format_date(self.obj['created'])}

*LAST LOGGED*
{self._format_date(self.obj['log'])}
""")


    def ls(self,df=None):
        """List practices."""
        if df == None: df = self.data
        drop_list = []
        # MIGHT BE PUT INSIDE ANOTHER FUNCTION
        if self.ID:                                                             #ID
            drop_list += [i for i in df.index if i not in self.ID]
            print(drop_list)
        if self.category:
            for ID in df.index:
                if df.loc[ID,'category'] != self.category:
                    drop_list.append(ID)
        if self.tags:
            for tag in self.tags:
                for ID in df.index:
                    if type(df.loc[ID,'tags']) != str:
                        drop_list.append(ID)
                    else:
                        if tag not in df.loc[ID,'tags'].split(' '):
                            drop_list.append(ID)
        if self.name:
            for ID in df.index:
                if self.name[0] not in df.loc[ID,'name'].split(' '):
                    drop_list.append(ID)
        if self.instrument:
            for inst in self.instrument:
                for ID in df.index:
                    if inst not in df.loc[ID,'instrument'].split(' '):
                        drop_list.append(ID)
        if self.priority:
            for ID in df.index:
                if self.priority != df.loc[ID,'priority'] :
                    drop_list.append(ID)
        if self.status:
            for ID in df.index:
                if self.status != df.loc[ID,'status'] :
                    drop_list.append(ID)
        if self.length:
            for ID in df.index:
                if self.length > df.loc[ID,'length']:
                    drop_list.append(ID)
        # goal
        # log count created
        #################################################################
        drop_list = list(set(drop_list))
        self._niceprint(exclude='default',
                       sort=['urg'],
                       head=self.verbosity[self.verbose],
                       tail=None,
                       drop_list=drop_list)

    def practice(self,interactive=True):
        """Choose practice or get weighted random practice and launch it."""
        if interactive == False:
            if self.ID == None:
                print("You need to chose a practice.\n")
                return
        if self.ID == None:
            pid = self._practice_picker()
            self.ID = [pid]
            self.view()
            while input(f"Choose practice {pid}: {self.data.loc[pid,'name']}?\n").upper() not in 'Y':
                pid = self._practice_picker()
                self.ID = [pid]
                self.view()
        self.view()
        if interactive == True:
            if input("Confirm?\n") == 'n':
                return
        self.data.loc[self.ID,'log'] += ' '+str(hex(round(time.time())))
        self.data.loc[self.ID,'count'] += 1
        self._save()
        print(f"Session logged!\n")
        if interactive and self.data.loc[self.ID[0],'links'] != np.nan:
            if input('Open links?\n').upper() in 'Y':
                self.open()

    def open(self):
        """Open links without doing anything else."""
        for l in self.data.loc[self.ID[0],'links'].split(' '):
            if '://' in l:
                subprocess.run(f"xdg-open {l}".split(' '))
            elif l[0]=='@':
                print('Heloooooo')
                for f in os.listdir(f"{self.res_path}/{l[1:]}"):
                    print(f)
                    subprocess.run(f"xdg-open {self.res_path}/{l[1:]}/{f}".split(' '))
            else:
                subprocess.run(f"xdg-open {self.res_path}/{l}".split(' '))

    def on(self):
        """Activate practice."""
        if self.ID:
            for i in self.ID:
                self.data.loc[i,'status'] = 1
                self.view(manual=i)
            self._save()

    def off(self):
        """Inactivate practice."""
        if self.ID:
            for i in self.ID:
                self.data.loc[i,'status'] = 0
                self.view(manual=i)
            self._save()

    def archive(self):
        """Archive practice."""
        if self.ID:
            for i in self.ID:
                self.data.loc[i,'status'] = 2
                self.view(manual=i)
            self._save()

    def stats(self):
        """Give stats about practising."""
        return

    def undo(self):
        """Return to backup.csv."""
        subprocess.run('mv backup.csv temp.csv'.split(' '))
        subprocess.run('mv practices.csv backup.csv'.split(' '))
        subprocess.run('mv temp.csv practices.csv'.split(' '))

#==========================================================================================

practice = Practice()
parser = argparse.ArgumentParser(prog=('PPP'),
                                 description='PracticePracticePractice (ppp)',
                                 epilog='this is the epilog')
parser.add_argument('cmd',choices = [i for i in Practice.__dict__.keys() if i[:1] != '_'],nargs='?',default='ls')
parser.add_argument('-i', '--ID',nargs='+', type=int)
parser.add_argument('-C','--category',choices = practice.categories)
parser.add_argument('-N','--name',nargs='+')
parser.add_argument('-I','--instrument',nargs='+',choices = practice.instruments.keys())
parser.add_argument('-t','--tags',nargs='+')
parser.add_argument('-d','--description',nargs='*') #nargs???
parser.add_argument('-l','--links',nargs='+')
parser.add_argument('-f','--file')
parser.add_argument('-p','--priority',choices = practice.priorities.keys())
parser.add_argument('--verbose', '-v', action='count', default=0)
parser.add_argument('-s','--status',choices = practice.status_types.keys(), type=int)
parser.add_argument('-g', '--goal',type=int)
parser.add_argument('-u','--urg')
parser.add_argument('--length', '-L', action='count')
parser.add_argument('--created')
parser.add_argument('--log')
parser.add_argument('--count',type=int)

a = parser.parse_args(namespace=practice)
Practice.__dict__[practice.cmd](practice)
