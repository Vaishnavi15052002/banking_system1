# csv_import.py
import csv

def read_csv(filename):
    customer_list = []   # list
    customer_set = set() # set
    customer_dict = {}   # dict

    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tup = (row['first_name'], row['last_name'], row['email'], row['phone'])  # tuple
            customer_list.append(tup)
            customer_set.add(row['email'])
            customer_dict[row['email']] = tup

    print("List:", customer_list)
    print("Set:", customer_set)
    print("Dict:", customer_dict)
