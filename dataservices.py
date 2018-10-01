from collections import OrderedDict
import os

from file_attachment_import.file_attachment_import_2 import fai


def clear():
    os.system('cls') if os.name == 'nt' else os.system('clear')


def menu_loop():
    clear()
    service = main_menu()[1]
    clear()
    service()


main_menu_options = OrderedDict({
    'File Attachment Import': fai,
    'File Attachment Export': 'begin',
    'Email History Import': 'begin',
    'Email History Export': 'begin',
    'App Transfer to CSV': 'begin',
    'Duplicate Company Handling': 'begin',
})


def main_menu():
    for i, k in enumerate(main_menu_options.keys()):
        print(i+1, k)
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
