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
            self.data.loc[i,'urg'] = self._calculate_urgency(i)
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

    def _niceprint(self,exclude='default',
                   sort=False,
                   head=False,
                   tail=False,
                   ascending=False,
                   drop_list=None,
                   one=False):
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

    def _calculate_urgency(self,ID):
        if ID not in self.data.index:
            return
        urgency = 0
        p = self.data.loc[ID,:]
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
        urgency *= 1+(abs(p['goal']-p['count'])/p['goal'])
        urgency *= self.priorities[p['priority']]
        urgency *= 1 + abs(time.time() - p['created'])/self.time_constant
        return urgency/100

    def _format_date(self,date):
        try:
            if type(date) in [int,float,np.float64]:
                return str(datetime.datetime.fromtimestamp(date)).split('.')[0]
            else:
                return [self._format_date(i) for i in date]
        except:
            return None

    def add(self):
        """Add practice session."""
        self.backup = self.data.copy()
        if not self.category:
            print(f"You need to pick a category among {', '.join(self.categories)}.") ; return
        if not self.name:
            print("You need to pick a practice name.") ; return
        if not self.instrument:
            print("You need to choose an instrument.") ; return
        self._list_many(listlist=['category','name','instrument','tags','description','links','priority','status'])
        self.ID = [i for i in range(1,1000) if i not in self.data.index][:1]
        print(type(self.ID[0]))
        if type(self.ID[0]) != int: self.ID = [1]
        for thing in ['goal','status','priority']:
            print(vars(self)[thing])
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
             'created'       : [time.time()],
             'log'           : [''],
             'count'         : [0],
             'goal'          : self.goal,
             'urg'           : ['???']}
        print(t)
        df = pd.DataFrame(t,index=self.ID)
        df.index.name = 'ID'
        self.data = pd.concat([self.data,df])
        self._save()
        self._niceprint(tail=10)
        print('\n',f"Practice {self.ID} successfully created!")


    def delete(self):
        """Delete practice with inputed ID."""
        self.backup = self.data.copy()
        for i in self.ID:
            if i in self.data['ID']:
                self.data = self.data[self.data['ID'] != i]
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
{'=' * (len(str(self.ID[0]))+42+len(self.obj['name']))}
({self.ID[0]}) {int(self.obj['status'])} {self.obj['name']:>39}
{int(self.obj['count'])}/{int(self.obj['goal']):<10} {self.obj['priority']} {self.obj['urg']}
{'=' * (len(str(self.ID[0]))+42+len(self.obj['name']))}

*CATEGORY*
{self.obj['category']:<30}

*INSTRUMENT(S)*
{self.obj['instrument']:<30}

*TAGS*
{self.obj['tags']}
{'_' * (len(str(self.ID[0]))+42+len(self.obj['name']))}

{self.obj['description']}
{'_' * (len(str(self.ID[0]))+42+len(self.obj['name']))}

*LINKS*
{self.obj['links']}

*CREATED*
{self._format_date(self.obj['created'])}

*LOG*
{self._format_date(self.obj['log'])}""")


    def ls(self):
        """List practices."""
        drop_list = []
        # MIGHT BE PUT INSIDE ANOTHER FUNCTION
        if self.ID:                                                             #ID
            drop_list += [i for i in self.data.index if i not in self.ID]
            print(drop_list)
        if self.category:
            for ID in self.data.index:
                if self.data.loc[ID,'category'] != self.category:
                    drop_list.append(ID)
        if self.tags:
            for tag in self.tags:
                for ID in self.data.index:
                    if type(self.data.loc[ID,'tags']) != str:
                        drop_list.append(ID)
                    else:
                        if tag not in self.data.loc[ID,'tags'].split(' '):
                            drop_list.append(ID)
        if self.name:
            for ID in self.data.index:
                if self.name[0] not in self.data.loc[ID,'name'].split(' '):
                    drop_list.append(ID)
        if self.instrument:
            for inst in self.instrument:
                for ID in self.data.index:
                    if inst not in self.data.loc[ID,'instrument'].split(' '):
                        drop_list.append(ID)
        if self.priority:
            for ID in self.data.index:
                if self.priority != self.data.loc[ID,'priority'] :
                    drop_list.append(ID)
        if self.status:
            for ID in self.data.index:
                if self.status != self.data.loc[ID,'status'] :
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

    def practice(self):
        """Choose practice or get weighted random practice and launch it."""
        if input('Choose practice?\n').upper() in 'YES':
            subprocess.run(f'xdg-open {self.link}'.split(' '))

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
parser.add_argument('cmd',choices = practice.cmds,nargs='?',default='ls')
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
parser.add_argument('--created')
parser.add_argument('--log')
parser.add_argument('--count')

a = parser.parse_args(namespace=practice)
# print(practice.ID)
# print(practice.category)
# print(practice.name)
# print(practice.link)
# print(practice.instrument)
# print(practice.created)
# print(practice.count)
print(practice.__dict__)
print("#"*50)
Practice.__dict__[practice.cmd](practice)
print("#"*50)
# print(practice.data.loc[practice.ID[0],:])
print("#"*50)
# print(practice.data)
