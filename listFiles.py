import httplib2
from apiclient import discovery
from google.oauth2 import service_account

from itertools import chain
import os
from os import path
import shutil


scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
secret_file = 'credentials.json'
spreadsheet_id = '1vJ1S909ivuaiHyAJEUAUji3LdJ9tao6V0Ku4DQFXry8'
range_name = 'Sheet1!A2:A'
credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
service = discovery.build('sheets', 'v4', credentials=credentials)

folder_path = '/mnt/d/Series'

video_extensions = ['.mp4', '.mkv', '.m4v', '.avi']
videos_insert_array = []


def getDataFromSheet():
    result_input = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, 
        range=range_name
    ).execute()
    if result_input.get('values'):
        getFolderFiles(list(chain.from_iterable(result_input.get('values'))))
    else:
        getFolderFiles(result_input.get('values'))


def insertToSheet():
    data = {
        'values' : videos_insert_array 
    }
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, 
        body=data, 
        range=range_name, 
        valueInputOption='RAW'
    ).execute()


def splitFileData(file):
    return list(os.path.splitext(file))


def filterVideos(sheet_files, local_files):
    return [x for x in local_files if x not in sheet_files]


def getFolderFiles(sheet_files):  

    if sheet_files:
        video_files = filterVideos(sheet_files, os.listdir(folder_path))
    else:
        video_files = os.listdir(folder_path)

    if video_files:
        for main_directory_files in video_files:
            main_directory_file_path = folder_path + '/' + main_directory_files
            if os.path.isfile(main_directory_file_path):
                videos_insert_array.append([main_directory_files, 'Movie'])
            else:
                files_from_folders = [sub_directory_files for subdir, sub_directories, sub_directory_files in os.walk(main_directory_file_path)]
                without_hidden_files_count = len([without_hidden_files for without_hidden_files in list(chain.from_iterable(files_from_folders)) if splitFileData(without_hidden_files)[1] in video_extensions and not without_hidden_files.startswith('.')])

                if(without_hidden_files_count == 1):
                    videos_insert_array.append([main_directory_files, 'Movie'])
                elif(without_hidden_files_count > 1):
                    videos_insert_array.append([main_directory_files, 'Series'])
        insertToSheet()


getDataFromSheet()