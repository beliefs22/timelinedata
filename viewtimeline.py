import os
import collections
import insertdata

import maketables


class OrderedCounter(collections.Counter, collections.OrderedDict):
     'Counter that remembers the order elements are first encountered'

     def __repr__(self):
         return '%s(%r)' % (self.__class__.__name__, OrderedDict(self))

     def __reduce__(self):
         return self.__class__, (OrderedDict(self),)

currentfiles = os.listdir(os.getcwd())
mycounters = []


for myfile in currentfiles:
     if myfile.endswith('.txt') and myfile.startswith('Example'):
          print myfile
          with open(myfile,'r') as thefile:
               thefile = list(thefile)
               conn = maketables.maketables(myfile.replace(".txt",""))
               a = insertdata.InsertVitalData(conn,thefile)
               a.insert_data()
               b = insertdata.InsertCBCData(conn, thefile)
               b.insert_data()
               c = insertdata.InsertCMPData(conn, thefile)
               c.insert_data()
               d = insertdata.InsertInfluenza(conn, thefile)
               d.insert_data()
