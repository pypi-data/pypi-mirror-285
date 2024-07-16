import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import time

def drop_duplicates_by_earlier_date(df1):
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'])

    # Sort by 'Sales Order Number' and 'Order_Date'
    df1 = df1.sort_values(by=['Sales Order', 'Order_Date'])

    # Drop duplicates, keeping the first (earliest date)
    df1 = df1.drop_duplicates(subset='Sales Order', keep='first')

    # Reset index for clean DataFrame
    df1 = df1.reset_index(drop=True)
    return df1

def get_absolute_difference(value):
    current, past = value
    return past - abs(current)

# Function to get the previous month and year
def get_previous_month_year():
    today = datetime.today()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)
    return last_month.strftime("%B %Y")

# Function to get the correct suffix for a day
def get_day_suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        return "th"
    else:
        return ["st", "nd", "rd"][day % 10 - 1]

# Function to get today's date in the desired format
def get_todays_date():
    today = datetime.today()
    day = today.day
    suffix = get_day_suffix(day)
    return today.strftime(f"%d{suffix} %B")

def func_comment_for_exclude(x):
    if x != '':
        return x
    else:
        return f"{get_previous_month_year()} Protection - {get_todays_date()}"

def func_crediting(x):
    if abs(x) < 0.1:
        return 0
    else:
        return x
    


def new_business_rule(value):
    action, past, diff= value
    if (action == 'Subjective Opinion') or (action == ''):
        if past < 1:
            return 'Needs Protection'
        elif diff >= -10:
            return 'Paid Before - No Action'
        else:
            return 'Subjective Opinion'
        
    else:
        return action
    
    
def get_protection_data(df_crediting,df_employee_protection, protection_file_name):
    
    df_crediting = df_crediting[df_crediting['Exclude?'] != 'true']

    df_id = df_employee_protection.merge(df_crediting, on = ['Order ID','Employee Id', 'Sales Order'], how = 'left', suffixes = ['','_5.57'])
    df_id['Exclude?'] = True
    
    # Combine into the desired format
    df_id['Comment For Excluding'] = 'INCP-R Exclusion'
    df_id.fillna('', inplace = True)
    df = df_id[df_id['Code'] != '']
    
    df.to_excel(protection_file_name, index = False)
    
    df_filtered = df[df['Comment For Excluding'] == 'INCP-R Exclusion']

    total = df_id[['Order ID','Employee Id', 'Sales Order']].drop_duplicates().shape[0]
    matched = df_filtered.drop_duplicates(subset=['Order ID','Employee Id', 'Sales Order']).shape[0]
    matched_already = df_id[df_id['Code'] != ''][['Order ID','Employee Id', 'Sales Order']].drop_duplicates().shape[0]


    print('Done...')
    
    print()
    print()
    print('Summary : ')
    
    print('Total       : ', total)
    print('Matched     : ', matched)
    print('Not Matched : ', total - matched)
    print('   1. Already Protected : ', matched_already - matched)
    print('   2. Other Issue       : ', total - matched_already)

    
    return df,df_id



def start_incp():
    d = {'Sales Order Number' : 'Sales Order',
        'Final Employee Name' : 'Employee Name',
        'Final Position ID'   : 'Position',
        'Position Code'       : 'Position',
        'SO'                  : 'Sales Order',
        'Employee code'       : 'Employee Id',
        'Order ID(Unique ID)' : 'Order ID',
        'Employee name'       : 'Employee Name',
        'Order Date'          : 'Order_Date',
        'Employee_Name'       :'Employee Name',
        'Employee_ID'         :'Employee Id',
        'Sales_Order'         : 'Sales Order',
        'Final Employee Code' : 'Employee Id',
        'Transaction Order ID': 'Order ID',}

    
    try:
        # Get the current working directory
        folder_path = os.getcwd()

        # List all CSV files in the folder
        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
        if len(csv_files) == 6:
            csv_files = csv_files[1:] + [csv_files[0]]


        # Check if there are enough CSV files
        if len(csv_files) < 3:
            raise FileNotFoundError("Not enough CSV files found in the current directory.")
        
        print('Importing the files...')
        
        # Read the specified CSV files into DataFrames
        df_crediting = pd.read_csv(csv_files[2], dtype='str')
        df_transactions = pd.read_csv(csv_files[1], dtype='str', encoding='ISO-8859-1')
        df_order_date = pd.read_csv(csv_files[0], dtype='str')
        df_past1 = pd.read_csv(csv_files[3], dtype='str')
        df_past2 = pd.read_csv(csv_files[4], dtype='str')
        df_past = pd.concat([df_past1,df_past2])
        if len(csv_files) == 6:
            df_amy = pd.read_csv(csv_files[5], dtype = 'str')

        
        print('Done...')

    except Exception as e:
        print('Problem in importing the files')

    df_transactions.drop("Unnamed: 0", axis = 1, inplace = True)
    df_crediting.drop("Unnamed: 0", axis = 1, inplace = True)
    df_order_date.drop("Unnamed: 0", axis = 1, inplace = True)


    df_transactions.rename(columns = d, inplace = True)
    df_order_date.rename(columns = d, inplace = True)
    df_crediting.rename(columns = d, inplace = True)
    df_past.rename(columns = d, inplace = True)

    print()
    print()
    print('Applying Filter Conditions...')
    
    df_transactions = df_transactions[df_transactions['Commission_Status_Reason'] == 'INCP-R']
    df_transactions = df_transactions[['Sales Order',  'Employee Name', 'Employee Id','Order ID']]

    df_order_date = drop_duplicates_by_earlier_date(df_order_date)

    df_order_date = df_order_date[['Sales Order','Order_Date']]


    df = df_transactions.merge(df_order_date, on = 'Sales Order', how = 'left')    # Need to check 

    df.dropna(subset = ['Employee Name', 'Employee Id', 'Order_Date'], inplace = True)
    df.fillna('', inplace = True)

    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    df = df[df['Order_Date'] <= '2023-12-31']
    df = df.drop_duplicates()
    
    print('Done...')

    print()
    print()
    print('Adding Past Crediting Value in the Data...')
    
    df = df.merge(df_past, on = ['Employee Name','Sales Order','Employee Id'], how = 'left')
    df.fillna('',inplace = True)
    def func_status(x):
        if (x =='') or (float(x) > 10):
            return 'Exclude'
        elif float(x) <= 0:
            return 'No Action'
        else:
            return 'Gap'
    df['Status'] = df['Ordervalue'].apply(func_status)

    print('Done...')

    print()
    print()
    print('Exporting INCP Exclusion Data...')
    
    df_employee_protection = df[df['Status'] == 'Exclude']

    df_crediting['Comment For Excluding'].fillna('', inplace = True)
    protection_file_name = "incp_r_exclusion.xlsx"
    df_crediting.rename(columns = d, inplace = True)



    df_protection, total_matched = get_protection_data(
                                                            df_crediting,
                                                            df_employee_protection,
                                                            protection_file_name
                                                        )
    
    total_matched[total_matched['Code'] == ''][['Sales Order',  'Employee Name', 'Employee Id','Order ID']].drop_duplicates().to_excel('missing_data.xlsx', index = False)
    df.to_excel('include_exclude_gap.xlsx', index = False)
    

def main():
    start = time.time()

    start_incp()
    end = time.time()
    print("Execution Time : ",int(end-start) , "s")