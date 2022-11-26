import pandas as pd
import sqlite3
from datetime import datetime
from datetime import date

table_list = {
    "tbl_items":"id INTEGER PRIMARY KEY,barcode,name,valid_from,valid_to",
    "tbl_places":"id INTEGER PRIMARY KEY,barcode,name,valid_from,valid_to",
    "tbl_warehouse":"id INTEGER PRIMARY KEY,timestamp,place,item,amount",
    }

db_name = "wms01.db"
con = sqlite3.connect(db_name)
cur = con.cursor()

#Initial Place and process
place = "P1"
process = "in"
# Initial amount of moved items is 1
amount = 1
###########################

def main():
    #initialize database, if it does not exist, it will be created
    for table in table_list:
        columns = table_list[table]
        table_create(table, columns)
    scanning()


def table_create(table, columns):
    # Creates table in sqlozte if it not exists
    global cur
    print("Create table" , table)
    sql = "CREATE TABLE if not exists "+ table +"("+columns+")"
    print(sql)
    cur.execute(sql)



def scanning():
    global con
    global place
    global process
    # Check if a place and Process is known, for inital setup
    # if not, force employee to scan
    while place is None:
        barcode = input("Scan Place")
        whatScanned(barcode)
    while process is None:
        barcode = input("Scan Process")
        whatScanned(barcode)
    ##############################################
    while True:
        barcode = input("Scan Item you want to "+ process+" "+str(amount) +" pieces in "+ place+": ")
        #Identify if place or process was scanned an change global variable
        if whatScanned(barcode):
            #returns True if barcode was not a process or a place
            #print("Item was scanned (No Place & No Process)")
            text = article_info(barcode)
            if text == None:
                print("Article ",barcode," not found!")
                if process == "out":
                    print("Can't outsource, unknown item...")
                    continue
                created = createArticle(barcode)
                if created == False:
                    # If the new articel was not whished to be created, scan again...
                    #print("not created")
                    continue
            #print("Stock Movement logging...")
            #print(amount,process)
            stock_movement(barcode, process, place, amount)


def stock_movement(item, process, place, amount):
    #print("entered stock_movement()")
    if int(amount) <=0:
        raise ValueError("Amount hast to be greater than Zero!")
    global cur
    global con
    amount = int(amount)
    now = datetime.today()
    timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
    #Get current amount of items in dedicated places
    cur.execute("SELECT id,item,place,amount,timestamp FROM tbl_warehouse WHERE item=? and place=?", (item,place))
    rows = cur.fetchall()
    #for row in rows:
    #    print(row)
    try:
        dataset = rows[0]
        #If items are found in the place, the dataset will be uzpdated by the new amount
        dataset_id = dataset[0]
        current_amount = dataset[3]
        #print(current_amount)
        if process == "in":
            new_amount = current_amount + amount
        elif process == "out":
            new_amount = current_amount - amount
            if new_amount < 0:
                raise ValueError("Amount less than Zero! No valid Tansaction...")
        #print(new_amount)
        #cur.execute("update tbl_warehouse (timestamp, item, place, amount) where id=",dataset_id, " values (?, ?, ?, ?)", (timestamp, item, place, amount))
        cur.execute("UPDATE tbl_warehouse SET amount=?, timestamp=? WHERE ID=?", (new_amount,timestamp,dataset_id))
    except IndexError:
        #If no article is found in existing place, new dataset is inserted insot databse
        #print("Article not found in")
        #if process == "out":
        #    raise ValueError("Can't outsource, newly added item...")
        cur.execute("insert into tbl_warehouse (timestamp, item, place, amount) values (?, ?, ?, ?)",(timestamp, item, place, amount))
    con.commit()
    cur.execute("SELECT * FROM tbl_warehouse WHERE item=? and place=?", (item,place))
    rows = cur.fetchall()
    for row in rows:
        print(row)
    return("success")

def createArticle(barcode):
    global cur
    global con
    create = input("Do you want to save the article to the database? y/n: ")
    if create == "y":
        name = input("Name of Article: ")
        today = date.today()
        datestr = today.strftime("%Y-%m-%d")
        valid_from = datestr
        #print(valid_from)
        cur.execute("insert into tbl_items (barcode, name, valid_from) values (?, ?, ?)",(barcode, name, valid_from))
        con.commit()#
    else:
        return False

def whatScanned(barcode):
    global place
    global process
    global amount
    places = ["P1","P2"]
    processes = ["in","out"]
    if barcode in places:
        print("Barcode of Place "+barcode+" was scanned")
        place = barcode
        return False
    if barcode in processes:
        print("Barcode of Process "+barcode+" was scanned")
        process = barcode
        return False
    if len(barcode) <= 3 and barcode.isnumeric():
        print("Amount detected: "+barcode)
        if int(barcode) < 1:
            raise ValueError("Amount has to be greater than Zero!")
        amount = barcode
        return False
    else:
        return True


def article_info(barcode):
    global cur
    sql = "SELECT name FROM tbl_items WHERE barcode = '"+barcode+"'"
    print(sql)
    res = cur.execute(sql)
    result = res.fetchone()
    print(result)
    return result



if __name__ == "__main__":
    main()