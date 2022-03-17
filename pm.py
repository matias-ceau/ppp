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
        self.status           = 0
        self.excluded_columns = ['description','links','created','log']

    def _getdata(self,path):
        if path not in os.listdir('.'):
            df = pd.DataFrame({i:[] for i in self.labels})
            df.set_index('ID')
            return df
        else:
            return pd.read_csv(path,index_col=0)

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
                   tail=False):
        df = self.data
        if exclude == 'default' : exclude = self.excluded_columns
        if exclude != None:
            df.drop(columns=exclude,inplace=True)
        if sort:
            df.sort_values(sort,ascending=False,inplace=True)
        if tail:
            df = df.tail(tail)
        elif tail:
            df = df.tail(tail)
        print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))

    def _calculate_urgency(self):
        pass

    def _format_date(self,date):
        try:
            if type(date) in [int,float]:
                return str(datetime.datetime.fromtimestamp(date)).split('.')[0]
            else:
                return [self._format_date(i) for i in date]
        except:
            return None

    def add(self):
        """Add practice session."""
        self._list_many(listlist=['category','name','instrument','tags','description','links','priority','status'])
        self.ID = [i for i in range(1,1000) if i not in self.data['ID']][0]
        t = {'ID'            : self.ID,
             'category'      : self.category,
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
        df = pd.DataFrame(t)
        df.set_index('ID')
        if (self.category[0] in self.categories.keys()) & (self.name!=None) & (self.instrument[0] in self.instruments.values()):
            self.data = pd.concat([self.data,df],ignore_index=True)
            self._save()
            self._niceprint(tail=10)
            print('\n',f"Practice {self.ID} successfully created!")
        else:
            print('Something went wrong!')


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
        for i in self.labels:
            print(i,' : ', self.__dict__[i])
        if self.category:
            pass#self.data.loc[]

    def view(self):
        """View practice."""
        if type(self.ID) == list:
            if len(self.ID) > 0:
                if self.ID[0] in self.data['ID']:
                    z = {k:v for k,v in list(zip(self.data.columns.tolist(),
                                                 self.data[self.data['ID'] == self.ID[0]].values[0].tolist()))}
                    print(f"""
{'=' * (len(str(self.ID[0]))+42+len(z['name']))}
{int(z['status'])} ({self.ID[0]}) {z['name']:>39}
{int(z['count'])}/{int(z['goal']):<10} {z['priority']} {z['urg']}
{'=' * (len(str(self.ID[0]))+42+len(z['name']))}

*CATEGORY*
{z['category']:<30}

*INSTRUMENT(S)*
{z['instrument']:<30}

*TAGS*
{z['tags']}
{'_' * (len(str(self.ID[0]))+42+len(z['name']))}

{z['description']}
{'_' * (len(str(self.ID[0]))+42+len(z['name']))}

*LINKS*
{z['links']}

*CREATED*
{self._format_date(z['created'])}

*LOG*
{self._format_date(z['log'])}""")


    def ls(self):
        """List practices."""
        pass

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
parser.add_argument('cmd',choices = practice.cmds,nargs='?',default='add')
parser.add_argument('-0', '--ID',nargs='*', type=int)
parser.add_argument('-c','--category',choices = practice.categories)
parser.add_argument('-n','--name')
parser.add_argument('-i','--instrument',choices = practice.instruments.values())
parser.add_argument('-t','--tags',nargs='+')
parser.add_argument('-d','--description',nargs='*') #nargs???
parser.add_argument('-l','--links',nargs='+')
parser.add_argument('-p','--priority',choices = practice.priorities.keys())
parser.add_argument('--verbose', '-v', action='count', default=0)
parser.add_argument('-s','--status',choices = practice.status_types.keys())
parser.add_argument('-g', '--goal',default=10,type=int)
parser.add_argument('-u','--urg', nargs='*',default='>')
parser.add_argument('--created',nargs='*')
parser.add_argument('--log',choices=['>','<'])
parser.add_argument('--count',nargs='*',default='>')

a = parser.parse_args(namespace=practice)
# print(practice.ID)
# print(practice.category)
# print(practice.name)
# print(practice.link)
# print(practice.instrument)
# print(practice.created)
# print(practice.count)
#print(practice.__dict__)
Practice.__dict__[practice.cmd](practice)
