import sqlite3
import os

def maketables(subject_id):
    """Creates or connects to a database for given subject_id
    and creates various tables in that database that holds data
    pulled from the patients chart

    Args:
        subject_id (str): Unique ID for the subject

    Returns:
        conn (sqlit3 connection): connection to the created database
    """
    #Connects or creates database
    conn = sqlite3.connect(subject_id+".db")
    cur = conn.cursor()
    #vitals table
    cur.execute('DROP TABLE IF EXISTS vitals')
    cur.execute('CREATE TABLE vitals (time,bp,temp,heart_rate,resp,spo2,\
pain_score)')

    #cbc table
    cur.execute('DROP TABLE IF EXISTS cbc')
    cur.execute('CREATE TABLE cbc (time,white_blood_cell_count,\
red_blood_cell_count,hemoglobin,hematocrit,platelet_count)')

    #cmp table
    cur.execute('DROP TABLE IF EXISTS cmp')
    cur.execute('CREATE TABLE cmp (time,sodium,potassium,chloride,\
carbon_dioxide,urea_nitrogen,creatinine_serum,glucose,albumin,bilirubin_total)')

    #influenza test table
    cur.execute('DROP TABLE IF EXISTS influenza')
    cur.execute('CREATE TABLE influenza (time,influenza_a_nat,influenza_b_nat,\
rsv_nat)')    
    return conn   

         
def main():
    maketables('testing')


if __name__ == "__main__":
    main()  
