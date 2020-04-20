from collections import OrderedDict
import os

from app_transfer_to_csv.app_data_transfer import adt
from email_history_export.email_history_export import ehe
from email_history_export.threaded_email_history_export import tehe
from email_history_import.email_history_import import ehi
from file_attachment_import.file_attachment_import import fai
from file_attachment_export.file_attachment_export import fae


def clear():
    os.system('cls') if os.name == 'nt' else os.system('clear')


def menu_loop():
    clear()
    service = main_menu()[1]
    clear()
    service()


main_menu_options = OrderedDict({
    'File Attachment Import': fai,
    'File Attachment Export': fae,
    'Email History Import': ehi,
    'Email History Export': ehe,
    'Threaded Email History Export': tehe,
    'App Transfer to CSV': adt,
    'Duplicate Company Handling': 'begin',
})


def main_menu():
    for i, k in enumerate(main_menu_options.keys()):
        print(i+1, k)
    print('Ctrl+C to quit\n')
    selection = input('Which data service do you need? ')
    while True:
        try:
            selection = int(selection)
            if selection < 1 or selection >= len(main_menu_options):
                raise IndexError
        except ValueError:
            selection = input('Value must be an integer. Try again: ')
        except IndexError:
            selection = input('Selection not available. Try again: ')
        else:
            return list(main_menu_options.items())[selection-1]


if __name__ == '__main__':
    menu_loop()
