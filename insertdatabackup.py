import re
import logging

Log_FILENAME = 'logging_out.txt'
logging.basicConfig(filename=Log_FILENAME,level=logging.DEBUG)

def makeRePattern(word):
    """Helper function to create patterns used to find numerical results.

    Args:
        word (str): result to search for
    """
    #re structure finds - White Blood Count: 3.78 or Neutrophil: 97
    template = r"(%s:\s*)(\d+\W\d+)|(%s:\s*)(\d+)"
    return re.compile(template % (word, word))

def makeRePattern2(word):
    """Helper function to make patterns used tostart result search

    Args:
        word (str): word that triggers search
    """
    #re structure finds - 12:38  Vitals Assessment or 12:39:12  Assessment
    template = r"(\d+:\d+:\d+\s*)(%s)|(\d+:\d+\s*)(%s)"
    return re.compile(template % (word,word))

def makeRePattern3(word):
    """Helper function to create patterns used to find string results

    Args:
        word (str): result to search for
    """
    #re structure finds - Influenza A NAT: No Detected
    template = r"(%s:\s*)([\w\s]+)"
    return re.compile(template % (word,))

class InsertData(object):
    """Base Class for inserting data into the databse created for each subject
    Args:
        cur (sqlite3 cursor): cur connected to database to insert data into
        data (list): collection of line from data file
        matchpatters (list): re pattern objects to identify data in a line
        headerpatterns (list): re pattern objects to identify lines with data
        stop (str): determines when to stop while loop
    """
        
    def __init__(self,conn,data):
        self.conn = conn
        self.cur = self.conn.cursor()
        self.data = data
        #overidden in each base class
        self.matchpatterns = []
        #overidden in each base class
        self.headerpatterns = []
        #overidden in each base class
        self.stop = ""

    def insert_data(self):
        data = iter(self.data)
        for line in data:
            for pattern in self.headerpatterns:
                match1 = pattern.search(line)
                if match1 != None:
                    #lab results
                    if self.stop == 'Collected':
                        row_id = match1.group(1)
                        toadd = []
                        stopmatch = re.compile(
                            r'(Collected:\s*)(\d+/\d+/\d+\s*\d+:\d+)')
                        while line.find(self.stop) == -1:
                            for pattern2 in self.matchpatterns:
                                match2 = pattern2.search(line)
                                if match2 != None:
                                    if match2.group(1) and match2.group(2):
                                        logging.debug(str(match2.group(1)) +\
                                                      " " + str(match2.group(2)))                                       
                                        toadd.append((match2.group(1),
                                                      match2.group(2)))
                                    else:
                                        logging.debug(str(match2.group(3)) +\
                                                      " " + str(match2.group(4)))
                                        toadd.append((match2.group(3),
                                                      match2.group(4)))
                            line = data.next()
                            stop = stopmatch.search(line)
                            if stop:
                                row_id = stop.group(2)
                                self.create_row(row_id)
                                for field, value in toadd:
                                    self.update_row(field, value, row_id)
                    #vital results
                    if self.stop == 'Custom Formula':
                        row_id = match1.group(3)
                        self.create_row(row_id)
                        while line.find(self.stop) == -1:
                            for pattern2 in self.matchpatterns:
                                match2 = pattern2.search(line)
                                if match2 != None:
                                    if match2.group(1) and match2.group(2):
                                        logging.debug(str(match2.group(1)) +\
                                                      " " + str(match2.group(2)))
                                        self.update_row(match2.group(1),
                                                        match2.group(2),
                                                        row_id)
                                    else:
                                        logging.debug(str(match2.group(3)) +\
                                                      " " + str(match2.group(4)))
                                        self.update_row(match2.group(3),
                                                        match2.group(4),
                                                        row_id)
                            #print line
                            line = data.next()



class InsertCBCData(InsertData):
    datatype = 'cbc'
    def __init__(self,cur,data):
        InsertData.__init__(self,cur,data)
        self.matchpatterns = [makeRePattern(word)
                              for word in ['White Blood Cell Count',
                                           'Red Blood Cell Count','Hemoglobin',
                                           'Hematocrit','Platelet Count']]

        self.headerpatterns = [makeRePattern(word)
                               for word in ['White Blood Cell Count']]
        
        self.stop = 'Collected'

    def create_row(self, row_id):
        self.cur.execute('''
        Insert INTO cbc
        (time)
        VALUES (?)''',
        (row_id,))
        self.conn.commit()

    def update_row(self,field,value,row_id):
        template = '''
        Update cbc
        Set %s= ?
        Where time= ?''' %\
        field.lower().strip().replace(" ","_").replace(":","").replace(",","_")
        
        self.cur.execute(template,(value, row_id))
        self.conn.commit()
        
class InsertVitalData(InsertData):

    def __init__(self,cur,data):
        InsertData.__init__(self,cur,data)
        
        self.matchpatterns = [makeRePattern(word)
                              for word in ['BP','Temp','Heart Rate','Resp',
                                           'SpO2','Pain Score']]
        
        self.headerpatterns = [makeRePattern2(word)
                               for word in ['Vitals Assessment']]
        self.stop = 'Custom Formula'
        

    def create_row(self, row_id):
        self.cur.execute('''
        Insert INTO vitals
        (time)
        VALUES (?)''',
        (row_id,))
        self.conn.commit()

    def update_row(self,field,value,row_id):
        template = '''
        Update vitals
        Set %s= ?
        Where time= ?''' %\
        field.lower().strip().replace(" ","_").replace(":","").replace(",","_")
        
        self.cur.execute(template,(value, row_id))
        self.conn.commit()

class InsertCMPData(InsertData):
    def __init__(self,cur,data):
        InsertData.__init__(self,cur,data)
        self.matchpatterns = [makeRePattern(word)
                              for word in ['Sodium','Potassium','Chloride',
                                           'Carbon Dioxide','Urea Nitrogen',
                                           'Creatinine,Serum',
                                           'Creatinine, Serum','Glucose',
                                           'Albumin','Bilirubin,Total',
                                           'Bilirubin,Total']]

        self.headerpatterns = [makeRePattern2(word)
                               for word in ['CMP']]
        
        self.stop = 'Collected'
        
    def create_row(self, row_id):
        self.cur.execute('''
        Insert INTO cmp
        (time)
        VALUES (?)''',
        (row_id,))
        self.conn.commit()

    def update_row(self,field,value,row_id):
        template = '''
        Update cmp
        Set %s= ?
        Where time= ?''' %\
        field.lower().strip().replace(" ","_").replace(":","").replace(",","_")
        
        self.cur.execute(template,(value, row_id))
        self.conn.commit()

class InsertInfluenza(InsertData):
    def __init__(self,cur,data):
        InsertData.__init__(self,cur,data)
        self.headerpatterns = [makeRePattern3(word)
                              for word in ['Influenza A NAT']]

        self.matchpatterns = [makeRePattern3(word)
                               for word in ['Influenza A NAT',
                                            'Influenza B NAT','RSV NAT']]
        self.stop = 'Collected'

    def create_row(self, row_id):
        self.cur.execute('''
        Insert INTO influenza
        (time)
        VALUES (?)''',
        (row_id,))
        self.conn.commit()

    def update_row(self,field,value,row_id):
        template = '''
        Update influenza
        Set %s= ?
        Where time= ?''' %\
        field.lower().strip().replace(" ","_").replace(":","").replace(",","_")
        
        self.cur.execute(template,(value, row_id))
        self.conn.commit()

