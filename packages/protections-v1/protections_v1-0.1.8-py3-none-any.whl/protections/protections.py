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

    df_id = df_employee_protection.merge(df_crediting, on = ['Employee Id', 'Sales Order'], how = 'left', suffixes = ['','_5.57'])
    df_id['Exclude?'] = True
    
    # Combine into the desired format
    df_id['Comment For Excluding'] = df_id['Comment For Excluding'].apply(func_comment_for_exclude )
    df_id.fillna('', inplace = True)
    df = df_id[df_id['Code'] != '']
    
    df.to_excel(protection_file_name, index = False)
    
    df_filtered = df[df['Comment For Excluding'] == f"{get_previous_month_year()} Protection - {get_todays_date()}"]

    total = df_id[['Employee Id', 'Sales Order']].drop_duplicates().shape[0]
    matched = df_filtered.drop_duplicates(subset=['Employee Id', 'Sales Order']).shape[0]
    matched_already = df_id[df_id['Code'] != ''][['Employee Id', 'Sales Order']].drop_duplicates().shape[0]

    print('Done...')
    
    print()
    print()
    print('Summary : ')
    
    print('Total       : ', total)
    print('Matched     : ', matched)
    print('Not Matched : ', total - matched)
    print('   1. Already Protected : ', matched_already - matched)
    print('   2. Other Issue       : ', total - matched_already)


def start_protections():
    d = {'Sales Order Number' : 'Sales Order',
        'Final Employee Name' : 'Employee Name',
        'Final Position ID'   : 'Position',
        'Position Code'       : 'Position',
        'SO'                  : 'Sales Order',
        'Employee code'       : 'Employee Id',
        'Order ID(Unique ID)' :'Order ID',
        'Employee name'       : 'Employee Name',
        'Order Date'          : 'Order_Date',
        'Employee_Name'       :'Employee Name',
        'Employee_ID'         :'Employee Id',
        'Sales_Order'         : 'Sales Order',
        'Final Employee Code' : 'Employee Id'}


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
        df_crediting = pd.read_csv(csv_files[0], dtype='str')
        df_transactions = pd.read_csv(csv_files[1], dtype='str')
        df_order_date = pd.read_csv(csv_files[2], dtype='str')
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

    df_transactions.rename(columns = d, inplace = True)
    df_order_date.rename(columns = d, inplace = True)
    df_crediting.rename(columns = d, inplace = True)
    df_past.rename(columns = d, inplace = True)


    print()
    print()
    print('Applying Filter Conditions...')

    df_order_date = drop_duplicates_by_earlier_date(df_order_date)

    df_order_date = df_order_date[['Sales Order','Order_Date']]

    df_transactions['Crediting Value'] = df_transactions['Crediting Value'].apply(lambda x: float(x))

    df = df_transactions.merge(df_order_date, on = 'Sales Order', how = 'left')    # Need to check 
    df['Crediting Value'] = df['Crediting Value'].apply(lambda x: float(x))

    # Step 3: Merging the data to get the Original Order Date
    df.dropna(subset = ['Employee Name', 'Employee Id', 'Order_Date'], inplace = True)
    df.fillna('', inplace = True)

    # Step 4: Applying Filter Condition on Layered Component and Order Date
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    df = df[df['Order_Date'] <= '2023-12-31']
    df = df[df['Layered Component Type'] == '']
    df.drop('Layered Component Type', axis = 1, inplace = True)

    print('Done...')

    print()
    print()
    print('Calculating Distinct Component Count...')

    new_df = df[['Sales Order', 'Crediting Value', 'Employee Name', 'Position', 'Employee Id','Order_Date','BU - Org']].groupby(['Employee Id','Order_Date','BU - Org', 'Employee Name','Sales Order','Position']).sum().reset_index()
    new_df = new_df[new_df['Crediting Value'] < -100]
    new_df = new_df.merge(df[['Component Name','Sales Order', 'Employee Name','Employee Id']].groupby(['Sales Order', 'Employee Name','Employee Id']).nunique().reset_index(
        ), on = ['Sales Order', 'Employee Name','Employee Id'], how = 'left')
    new_df['new_crediting_value'] = new_df['Crediting Value']/new_df['Component Name']

    print('Done...')


    del df_transactions
    del df_order_date
    del df_past1
    del df_past2
    del df

    print()
    print()
    print('Adding Past Crediting Value in the Data...')


    df_past.dropna(subset = ['Employee Name', 'Employee Id', 'Sales Order','processing_month'], inplace = True)
    df_past['Ordervalue'] = df_past['Ordervalue'].apply(lambda x: float(x))
    df_past['processing_month'] =  pd.to_datetime(df_past['processing_month'], format = '%Y-%m-%d')
    df_past = df_past.sort_values(by=['Employee Name','Employee Id', 'Sales Order', 'processing_month'])

    # Drop duplicates, keeping the first (earliest date)
    df_past = df_past.drop_duplicates(subset=['Employee Name','Employee Id','Sales Order'], keep='first')

    # Reset index for clean DataFrame
    df_past = df_past.reset_index(drop=True)

    final_df = new_df.merge(df_past, on = ['Employee Name','Employee Id','Sales Order'], how = 'left')
    # final_df = new_df.merge(df_past, on = ['Employee Name','Sales Order'], how = 'left')
    del df_past
    final_df.fillna(0, inplace = True)
    final_df['difference'] = final_df[['Crediting Value', 'Ordervalue']].apply(get_absolute_difference, axis = 1) 
    final_df['distinct_component_difference'] = final_df[['new_crediting_value', 'Ordervalue']].apply(get_absolute_difference, axis = 1)


    print('Done...')

    print()
    print()
    print('Adding Amy Martins Data...')

    final_df['Action'] = ''
    df_amy.loc[len(df_amy.index)] = ['Amy Martin', 'Amy Martin', '', 'Amy Martin'] + [''] * 9
    final_df = final_df.merge(df_amy[['Employee Name','Manager L2']], on = 'Employee Name', how = 'left')
    final_df.fillna('', inplace = True)
    final_df.loc[final_df['Manager L2'] == 'Amy Martin', 'Action'] = 'Needs Protection'

    print('Done...')

    print()
    print()
    print('Creating Actions...')


    final_df['Action'] = final_df[['Action','Ordervalue', 'difference']].apply(new_business_rule, axis = 1)      
    final_df['Action'] = final_df[['Action','Ordervalue', 'distinct_component_difference']].apply(new_business_rule, axis = 1)     
    print('Done...')

    print()
    print()
    print('Exporting Employee Data for Protections File...')

    final_df.loc[(final_df['BU - Org'] == 'Ultrasound') & (final_df['Action'] == 'Subjective Opinion'), 'Action'] = 'Paid Before - No Action'

    final_df.drop('processing_month', axis = 1, inplace = True)
    output_columns = {
        'Ordervalue'           : 'Past Crediting Value',
        'new_crediting_value'  : 'Crediting Value / Component Count',
        'Component Name'       : 'Component Count',
        'avg_difference'       : 'new_difference'
    }

    final_df.rename(columns = output_columns, inplace = True)

    with pd.ExcelWriter(str(get_todays_date()) + '_summary_employee_data_for_protection.xlsx', engine='xlsxwriter') as writer:
        final_df.to_excel(writer, sheet_name='All Data', index=False)
        final_df[final_df['Action'] == 'Subjective Opinion'].to_excel(writer, sheet_name='Subjective Opinion', index=False)
    
    print('Done...')

    print()
    print()
    print('Exporting Protection Data...')

    df_crediting['Comment For Excluding'].fillna('', inplace = True)
    df_employee_protection = final_df[final_df['Action'] == 'Needs Protection'].copy()
    protection_file_name = "protection_data.xlsx"
    df_crediting.rename(columns = d, inplace = True)



    get_protection_data(
                            df_crediting,
                            df_employee_protection,
                            protection_file_name
                        )
    del df_crediting
    del df_employee_protection
    del final_df
    del new_df


def main():
    start = time.time()

    start_protections()
    end = time.time()
    print("Execution Time : ",int(end-start) , "s")
