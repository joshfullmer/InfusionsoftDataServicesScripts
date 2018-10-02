import os

from database.utils import get_app_and_token


def clear():
    os.system('cls') if os.name == 'nt' else os.system('clear')


def fai():
    appname, token = get_app_and_token('Appname and Auth Code')
    clear()
    cwd = os.getcwd()
    attach_dir = cwd + '/file_attachment_import/attachments/' + appname
    os.makedirs(attach_dir, exist_ok=True)
    input(f'Put the folder and CSV into the following directory:\n'
          f'{attach_dir}\n\nPress Enter when the files have been moved.')


if __name__ == '__main__':
    fai()
