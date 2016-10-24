import re
import logging

Log_FILENAME = 'logging_out.txt'
logging.basicConfig(filename=Log_FILENAME,level=logging.DEBUG)

def makeNumPattern(word):
    """Helper function to create patterns used to find numerical results.

    Args:
        word (str): result to search for
    """
    #re structure finds - White Blood Count: 3.78 or Neutrophil: 97
    template = r"(%s:\s*)(\d+\W{0,1}\d*)|(%s:\s+$)"
    return re.compile(template % (word, word))

def makeSearchPattern(word):
    """Helper function to make patterns used tostart result search

    Args:
        word (str): word that triggers search
    """
    #re structure finds - 12:38  Vitals Assessment or 12:39:12  Assessment
    template = r"(\d+:\d+:\d+\s*)(%s)|(\d+:\d+\s*)(%s)"
    return re.compile(template % (word,word))

def makeStringPattern(word):
    """Helper function to create patterns used to find string results

    Args:
        word (str): result to search for
    """
    #re structure finds - Influenza A NAT: No Detected
    template = r"(%s:\s*)([\w\s]+)"
    return re.compile(template % (word,))

def makeEndPattern(word):
    """Helper function to create patterns used to find results at end of line

    Args:
        word (str): result to search for
    """
    #re structure finds = Temp:
    template = r'(%s:\s+$)'
    return re.compile(template % (word,))

class InsertData(object):
    """Base Class for inserting data into the databse created for each subject

    Attr:
        matchpatterns (list): re pattern objects to identify results
        headerpatterns (list): re pattern objects used to start result search
        stop (str): determines when to stop result search
        tablename (str): table data should be inserted into
    Args:
        cur (sqlite3 cursor): cur connected to database to insert data into
        data (list): lines from text file containing subject information
    """
        
    def __init__(self,conn,data):
        #connection to the database for a unique subject
        self.conn = conn
        #cursor in that database connection
        self.cur = self.conn.cursor()
        #list of data create from the text file containing subjects data
        self.data = data
        #words that indicate a result was found
        self.matchpatterns = []
        #words that indicate to start search for reseults
        self.headerpatterns = []
        #word that indicates to stop result search
        self.stop = ""
        #table name used in create and update functions
        self.tablename = ""

    def create_row(self, row_id):
        """Creates base entry into the table to be updated as results are found

        Args:
            row_id (str): uniqe timepoint for the result
        """
        template = '''
        Insert INTO %s
        (time)
        VALUES (?)''' % self.tablename
        self.cur.execute(template, (row_id,))
        self.conn.commit()

    def update_row(self,field,value,row_id):
        """Updates the row with given paramaters with given value

        Args:
            field (str): field to update
            value (str): value to update field to
            row_id (str): record to update
        """
        #insert given field and value into the template
        template = '''
        Update %s
        Set %s= ?
        Where time= ?''' %\
        (self.tablename,
         field.lower().strip().replace(" ","_").replace(":","").replace(",","_")
         )
        self.cur.execute(template,(value, row_id))
        self.conn.commit()

class InsertOtherData(InsertData):
    """Base class for inserting non lab value results like vitals"""

    def __init__(self,conn,data):
        InsertData.__init__(self,conn,data)
    
    def insert_data(self):
        """Inserts data into the appropriate table for the inheriting class"""
        #create iterator of data so we can move through lines as we want
        data = iter(self.data)
        #loop through each line of the file to seach for relevant words
        for line in data:
            #look for a line that indicates to start search
            for pattern in self.headerpatterns:
                match1 = pattern.search(line)
                #found a word - start search
                if match1 != None:
                    #uniqe timepoint for the entry
                    row_id = match1.group(3)
                    self.create_row(row_id)
                    #look for results until you see stop keyword
                    while line.find(self.stop) == -1:
                        new_line = False
                        for pattern2 in self.matchpatterns:
                            match2 = pattern2.search(line)
                            #determine which match group the pattern found
                            if match2 != None:
                                #Temp: 37.4
                                if match2.group(1) and match2.group(2):
                                    logging.debug(str(match2.group(1)) +\
                                                  " " + str(match2.group(2)))
                                    self.update_row(match2.group(1),
                                                    match2.group(2),
                                                    row_id)
                                #Temp: end of line
                                elif match2.group(3):
                                    valuept = re.compile(r'(^\s*\d+\S{0,1}\d*)')
                                    field_name = match2.group(3).strip()
                                    if new_line == False:
                                        next_line = data.next()
                                        new_line = True
                                    valuesearch = valuept.search(next_line)
                                    if valuesearch != None:
                                        value = valuesearch.group(1).strip()
                                        self.update_row(field_name,value,row_id)
                            #move to next line if you didn't see stop keyword
                        if new_line == False:
                            line = data.next()
                        else:
                            line = next_line

class InsertLabData(InsertData):
    """Base class for inserting lab data with numerical results"""

    def __init__(self,conn,data):
        InsertData.__init__(self,conn,data)
    
    def insert_data(self):
        """Inserts data into the appropriate table for the inheriting class"""
        #create iterator of data so we can move through lines as we want
        data = iter(self.data)
        #loop through each line of the file to seach for relevant words
        for line in data:
            #look for a line that indicates to start search
            for pattern in self.headerpatterns:
                match1 = pattern.search(line)
                #found a word - start search
                if match1 != None:
                    #container for results to add once you identify row_id
                    toadd = []
                    #Pulls row_id when you see the collected key word
                    stopmatch = re.compile(
                        r'(Collected:\s*)(\d+/\d+/\d+\s*\d+:\d+)')
                    #start looking for results until you reach stop keyword
                    while line.find(self.stop) == -1:
                        for pattern2 in self.matchpatterns:
                            match2 = pattern2.search(line)
                            #White Blood Count: 3.78
                            if match2 != None:
                                if match2.group(1) and match2.group(2):
                                    logging.debug(str(match2.group(1)) +\
                                                  " " + str(match2.group(2)))                                       
                                    toadd.append((match2.group(1),
                                                  match2.group(2)))
                        #move to next line for while loop
                        line = data.next()
                        #determine if next line has collected keyword
                        stop = stopmatch.search(line)
                        if stop:
                            #Found stop keyword and row_id
                            #create entry and add results for that entry
                            row_id = stop.group(2)
                            self.create_row(row_id)
                            for field, value in toadd:
                                self.update_row(field, value, row_id)


class InsertCBCData(InsertLabData):
    """Insert data from CBC labs"""
    datatype = 'cbc'
    def __init__(self,cur,data):
        InsertLabData.__init__(self,cur,data)
        self.matchpatterns = [makeNumPattern(word)
                              for word in ['White Blood Cell Count',
                                           'Red Blood Cell Count','Hemoglobin',
                                           'Hematocrit','Platelet Count']]
        self.headerpatterns = [makeNumPattern(word)
                               for word in ['White Blood Cell Count']]        
        self.stop = 'Collected'
        self.tablename = 'cbc'


        
class InsertVitalData(InsertOtherData):
    """Insert Data from Vital Sign Assessements"""

    def __init__(self,cur,data):
        InsertOtherData.__init__(self,cur,data)        
        self.matchpatterns = [makeNumPattern(word)
                              for word in ['BP','Temp','Heart Rate','Resp',
                                           'SpO2','Pain Score']]        
        self.headerpatterns = [makeSearchPattern(word)
                               for word in ['Vitals Assessment']]
        self.stop = 'Custom Formula'
        self.tablename = 'vitals'        


class InsertCMPData(InsertLabData):
    """Insert Data from CMP lab test"""
    def __init__(self,cur,data):
        InsertLabData.__init__(self,cur,data)
        self.matchpatterns = [makeNumPattern(word)
                              for word in ['Sodium','Potassium','Chloride',
                                           'Carbon Dioxide','Urea Nitrogen',
                                           'Creatinine,Serum',
                                           'Creatinine, Serum','Glucose',
                                           'Albumin','Bilirubin,Total',
                                           'Bilirubin,Total']]
        self.headerpatterns = [makeSearchPattern(word)
                               for word in ['CMP','Comprehensive','BMP',
                                            'Basic']]        
        self.stop = 'Collected'
        self.tablename = 'cmp'
        
class InsertInfluenza(InsertLabData):
    """Inserts data on Influenza Testing"""
    def __init__(self,cur,data):
        InsertData.__init__(self,cur,data)
        self.headerpatterns = [makeStringPattern(word)
                              for word in ['Influenza A NAT']]
        self.matchpatterns = [makeStringPattern(word)
                               for word in ['Influenza A NAT',
                                            'Influenza B NAT','RSV NAT']]
        self.stop = 'Collected'
        self.tablename = 'influenza'

