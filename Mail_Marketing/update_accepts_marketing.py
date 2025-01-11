import pandas as pd
import time
import sys
from tqdm import tqdm 
import requests
sys.path.append('/home/snparada/Spacionatural/Libraries/klaviyo_lib/')
from profiles import KlaviyoProfiles

# Inicializa el objeto de KlaviyoProfiles
klaviyo_profile_obj = KlaviyoProfiles()

# Lee todos los perfiles
profiles_df = pd.read_csv('/home/snparada/Spacionatural/Data/Historical/historic_customers_klaviyo.csv')

# Itera sobre cada perfil y actualiza la preferencia de marketing
for index, row in profiles_df.iterrows():
    profile_id = row['id']  # Asume que el ID del perfil está en la columna 'id'
    
    # Actualiza el perfil para aceptar marketing
    response = klaviyo_profile_obj.update_profile_by_id_accepts_marketing(
        profile_id, 
        accepts_marketing=True  # Asegura que el perfil acepte marketing
    )
    
    # Puedes agregar un pequeño retraso entre las solicitudes para no saturar la API
    time.sleep(0.1)
    
    # O usa tqdm para visualizar el progreso
    tqdm.write(f"Perfil {profile_id} actualizado: {response}")

print("Todos los perfiles han sido actualizados para aceptar marketing.")
