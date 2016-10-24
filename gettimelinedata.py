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
     if myfile.endswith('.txt') and myfile.startswith('11_A'):
          print "Gathering data for Subject %s" % myfile
          with open(myfile,'rb') as subjectfile:
               subjectfile = list(subjectfile)
               conn = maketables.maketables(myfile.replace(".txt",""))
               vitals = insertdata.InsertVitalData(conn,subjectfile)
               vitals.insert_data()
               cbc = insertdata.InsertCBCData(conn, subjectfile)
               cbc.insert_data()
               cmp_data = insertdata.InsertCMPData(conn, subjectfile)
               cmp_data.insert_data()
               influenza = insertdata.InsertInfluenza(conn, subjectfile)
               influenza.insert_data()
          print "Finished data collection for Subject %s" % myfile
