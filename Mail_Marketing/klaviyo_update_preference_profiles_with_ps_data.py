import pandas as pd
import time
import sys
from tqdm import tqdm 
import requests
sys.path.append('/home/snparada/Spacionatural/Libraries/klaviyo_lib/')
from profiles import KlaviyoProfiles

klaviyo_profile_obj = KlaviyoProfiles()

ps_customer_clasification = pd.read_csv('/home/snparada/Spacionatural/Data/Historical/historic_customer_prestashop_classification.csv')
klaviyo_customers = pd.read_csv('/home/snparada/Spacionatural/Data/Dim/customers_klaviyo.csv')

# Asegurarse de que los emails estén en formato adecuado
ps_customer_clasification['email'] = ps_customer_clasification['email'].str.strip().str.lower()
klaviyo_customers['email'] = klaviyo_customers['email'].str.strip().str.lower()

# Merge de los DataFrames
df_to_update_to_klaviyo = pd.merge(
    ps_customer_clasification, 
    klaviyo_customers[['email', 'id']],
    on='email', 
    how='left'
)

# Iterar sobre el DataFrame con tqdm para ver el progreso
for index, customer in tqdm(df_to_update_to_klaviyo.iterrows(), total=df_to_update_to_klaviyo.shape[0]):
    id = customer['id']
    if pd.isna(id):
        print(f"Skipping update for {customer['email']} due to missing ID.")
        continue

    firstname = customer['firstname'].title()
    lastname = customer['lastname'].title()
    preferences = customer['Labels']
    num_orders = customer['Num_Orders']
    last_purchase = customer['Last_Purchase']
    ticket_classification = customer['ticket_classification']
    monetary_classification = customer['monetary_classification']


    try:
        klaviyo_profile_obj.update_profile_by_id(
            id,
            first_name=firstname,
            last_name=lastname,
            preferencias=preferences,
            num_ps_orders=num_orders,
            monetary_classification=monetary_classification,
            ticket_classification=ticket_classification,
            last_purchase=last_purchase,
        )
        time.sleep(0.1)  # Short delay to avoid hitting API limits
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred for {id}: {e}")  # Print the HTTP error
    except Exception as e:
        print(f"An error occurred for {id}: {e}")  # Print other errors
