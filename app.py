import requests
import os
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
token = config.get('idocs', 'token')

baseurl = 'https://external.idocs.kz/api/'
apiv1 = f'{baseurl}v1/ExternalDocuments/'
apiv2 = f'{baseurl}2/external-documents/'
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

type_docs = ["inbox", "outbox"]

for type in type_docs:
    os.makedirs(type, exist_ok=True)
    page = 0
    has_documents = True

    # Set to store unique file_id values
    file_id_set = set()

    if os.path.exists('file_history.txt'):
        with open('file_history.txt', "r") as history_file:
            file_id_set.update(line.strip() for line in history_file)

    while has_documents:
        response = requests.get(f"{apiv2}{type}?page={page}", headers=headers)
        if response.status_code == 200:
            documents_list = response.json()
            total_documents_count = len(documents_list)
            print(type, total_documents_count, page)
            # If the list of documents is empty, set has_documents to False to exit the loop
            if total_documents_count == 0:
                has_documents = False

            for document in documents_list:
                file_id = document["DocumentId"]
                if file_id in file_id_set:
                    print(f"File with ID '{file_id}' is already downloaded.")
                    continue  # Skip the download

                file_name = document["DocumentContentName"]
                created_on = document["DocumentCreatedOn"].split("T")[0]

                # Create the nested directory based on the 'type' and 'created_on' date
                nested_directory = os.path.join(type, created_on)
                os.makedirs(nested_directory, exist_ok=True)

                get_file = requests.get(f"{apiv1}{file_id}/PrintForm", headers=headers).content
                with open(os.path.join(nested_directory, f"{file_name}_{file_id}.pdf"), "wb") as file:
                    file.write(get_file)

                # Add file_id to the set and save to file_history.txt
                file_id_set.add(file_id)
                with open('file_history.txt', "a") as history_file:
                    history_file.write(f"{file_id}\n")

            page += 1
        else:
            print(f"Ошибка при обращении к API. Код статуса: {response.status_code}")
            break