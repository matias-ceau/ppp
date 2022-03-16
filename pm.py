import numpy as np
import pandas as pd
import sys
import os
import time
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
            config  = yaml.load(f, Loader=yaml.FullLoader)
            self.__dict__.update(config)
        self.data   = self._getdata("practices.csv")
        self.backup = self._getdata("backup.csv")
        self.status = 0

    def _getdata(self,path):
        if path not in os.listdir('.'):
            return pd.DataFrame({i:[] for i in self.labels})
        else:
            return pd.read_csv(path)

    def _save(self):
        self.backup.to_csv('backup.csv',index=False)
        self.data.to_csv("practices.csv",index=False)

    def _niceprint(self,exclude=None,
                   sort=False,
                   head=False,
                   tail=False):
        df = self.data.drop(columns=exclude)
        if sort:
            df.sort_values(sort,ascending=False,inplace=True)
        if tail:
            df = df.tail(tail)
        elif tail:
            df = df.tail(tail)
        print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))

    def add(self):
        """Add practice session."""
        self.ID = [i for i in range(1,1000) if i not in self.data['ID']][0]
        t = {'ID'            : self.ID,
             'category'      : self.category,
             'name'          : self.name,
             'instrument'    : self.instrument,
             'tags'          : self.tags,
             'description'   : self.description,
             'link'          : self.link,
             'priority'      : self.priority,
             'status'        : self.status,
             'created'       : [time.time()],
             'log'           : [''],
             'count'         : [0],
             'goal'          : self.goal,
             'urg'           : ['???????????']}
        df = pd.DataFrame(t)
        if (self.category in self.categories) & (self.name!=None) & (self.instrument!=None):
            self.data = pd.concat([self.data,df],ignore_index=True)
            self._save()
            self._niceprint(exclude=['description','link','created','log'],
                            tail=10)
            print('\n',f"Practice {self.ID} successfully created!")
        else:
            print('Something went wrong!')


    def delete(self):
        """Delete practice with inputed ID."""
        self.backup = self.data.copy()
        for i in self.ID:
            if i in self.data['ID']:
                self.data = self.data[self.data['ID'] != self.ID]
            else:
                print(f'No practice with ID {i}')
        self._save()
        print(self.data.tail(10))

    def mod(self):
        """Modify practice."""
        return

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
parser.add_argument('-0', '--ID', type=int)
parser.add_argument('-c','--category',choices = practice.categories)
parser.add_argument('-n','--name')
parser.add_argument('-i','--instrument',choices = practice.instruments.values())
parser.add_argument('-t','--tags')
parser.add_argument('-d','--description') #nargs???
parser.add_argument('-l','--link')
parser.add_argument('-p','--priority')
parser.add_argument('-v', '--verbose')
parser.add_argument('-s','--status')
parser.add_argument('-g', '--goal')
parser.add_argument('-u','--urgency')
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
#Practice.__dict__[practice.cmd](practice)
