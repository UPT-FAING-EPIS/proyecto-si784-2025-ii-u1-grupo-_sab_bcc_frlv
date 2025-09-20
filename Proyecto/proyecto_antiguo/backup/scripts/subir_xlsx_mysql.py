import pandas as pd
from pymongo import MongoClient

def subir_csv_a_mongodb(csv_file, collection_name, mongo_uri, db_name):
    df = pd.read_csv(csv_file, low_memory=False)
    records = df.to_dict(orient='records')

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Insertar los datos
    result = collection.insert_many(records)
    print(f"Subidos {len(result.inserted_ids)} documentos a la colección '{collection_name}' en MongoDB.")
    client.close()

# Ejemplo de uso
mongo_uri = 'mongodb://localhost:27017/'
db_name = 'keyloggerdataset'
import os
csv_file = os.path.join('..', 'DATOS', 'Keylogger_Detection.csv')
collection_name = 'Keylogger_Detection'

subir_csv_a_mongodb(csv_file, collection_name, mongo_uri, db_name)
