import shutil
from pathlib import Path, PurePath
from threading import Thread


class SortingThread(Thread):

    count = 0

    def __init__(self, id_number):

        super().__init__()
        self.id_number = id_number
        SortingThread.count += 1
        self.process_number = SortingThread.count

    def run(self):

        print(f"Thread:{self.id_number}, process number:{self.process_number} was run.\n")
        print(f"Thread:{self.id_number}, process number:{self.process_number} has been completed.")


def archive_extr(file_link, extract_dir):
    # Unpacks the archive to the specified folder, then deletes the archive
    folder_name = file_link.name[:file_link.name.rfind(".")]
    extract_dir = Path(PurePath(extract_dir, 'archives', folder_name))
    shutil.unpack_archive(file_link, extract_dir)
    file_link.unlink()


def delete_empty_folders(main_folder):
    tree, folders_list = (get_files_tree_from(main_folder))
    empty_folders_list = []

    for folder in folders_list:

        if not any(Path(folder).iterdir()):
            empty_folders_list.append(folder)
            folder.rmdir()

    if empty_folders_list:
        delete_empty_folders(main_folder)


def get_files_tree_from(direction):  # builds a folder/file tree

    tree = {}    # dict.key - location, dict.value - list of files
    files = []
    folders = [direction]    # list of folders
    do_not_touch = ['archives', 'video', 'audio', 'documents', 'images', 'unknown']

    for obj in direction.iterdir():

        if obj.is_dir():

            if obj.name.casefold() in do_not_touch:
                """If the folder name matches the value in the list, 
                                        then we skip it and execute the else block"""
                
            else:
                sorting_thread_1 = SortingThread(1)
                tree_1, folders_1 = get_files_tree_from(obj)
                sorting_thread_1.start()
                sorting_thread_1.join()
                tree.update(tree_1)

                for i in folders_1:
                    folders.append(i)

        elif obj.is_file():
            files.append(obj.name)
            tree[direction] = files

    return tree, folders  # types: dict, list


def move_file_to_folder(file_link, file_type, main_folder):

    dest_folder = Path(PurePath(main_folder, file_type))
    dest_folder.mkdir(exist_ok=True)
    new_file_link = Path(PurePath(dest_folder, file_link.name))
    file_link.replace(new_file_link)


def tranliteration(file_name):
    
    UA_CYRILLIC_SYMBOLS = ("а", "б", "в", "г", "ґ", "д", "е", "є", "ж", "з", "и",
                           "і", "ї", "й", "к", "л", "м", "н", "о", "п", "р", "с",
                           "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ь", "ю", "я",
                           "ё", "ъ", "ы", "э")
    
    LATIN_SYMBOLS = ("a", "b", "v", "h", "g", "d", "e", "ye", "zh", "z", "y",
                     "i", "i", "yi", "k", "l", "m", "n", "o", "p", "r", "s",
                     "t", "u", "f", "kh", "ts", "ch", "sh", "shc", "", "yu", "ya",
                     "e", "", "i", "ye")

    t_dictionary = {}

    for cyrillic_s, latin_s in zip(UA_CYRILLIC_SYMBOLS, LATIN_SYMBOLS):
        t_dictionary[ord(cyrillic_s)] = latin_s
        t_dictionary[ord(cyrillic_s.upper())] = latin_s.upper()

    translated_name = file_name.translate(t_dictionary)

    return translated_name


def normalize(string):

    latin_name = tranliteration(string)     # Replace Cyrillic withLatin
    latin_num_and_abc = ''      # leave in name only letters\numbers and '_'

    for char in latin_name:
        if char.isalnum():
            latin_num_and_abc += char
        else:
            latin_num_and_abc += '_'

    return latin_num_and_abc


def renaming(f_link):

    if f_link.is_file():
        file_name = f_link.name[:(f_link.name).rfind(".")]
        file_ext = f_link.suffix
        norm_file_name = normalize(file_name)
        new_name = f_link.replace(Path(f_link.parent, norm_file_name + file_ext))

    else:
        new_name = f_link

    return new_name


def sorting_files_to_folders(tree, known_file_extension, main_folder):

    for key, values in tree.items():
        for file in values:
            sorting_thread_2 = SortingThread(2)
            file_location = renaming(Path(PurePath(key, file)))
            file_suffix = file_location.suffix.casefold()

            if file_suffix in known_file_extension['archives']:
                sorting_thread_2.start()
                archive_extr(file_location, main_folder)

            elif file_suffix in known_file_extension['audio']:
                ftype = 'audio'
                sorting_thread_2.start()
                move_file_to_folder(file_location, ftype, main_folder)

            elif file_suffix in known_file_extension['documents']:
                ftype = 'documents'
                sorting_thread_2.start()
                move_file_to_folder(file_location, ftype, main_folder)

            elif file_suffix in known_file_extension['images']:
                ftype = 'images'
                sorting_thread_2.start()
                move_file_to_folder(file_location, ftype, main_folder)

            elif file_suffix in known_file_extension['video']:
                ftype = 'video'
                sorting_thread_2.start()
                move_file_to_folder(file_location, ftype, main_folder)

            else:
                ftype = 'unknown'
                move_file_to_folder(file_location, ftype, main_folder)

        sorting_thread_2.join()
    delete_empty_folders(main_folder)       # delete all empty folders


def main():
    
    KNOW_FILE_EXTENSION = {
        'archives': ['.zip', '.gz', '.tar'],
        'audio': ['.mp3', '.ogg', '.wav', '.amr'],
        'documents': ['.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'],
        'images': ['.jpeg', '.png', '.jpg', '.svg'],
        'video': ['.avi', '.mp4', '.mov', '.mkv']
    }

    print('I need the folder path to sort.\nFor example: C:\\blabla\\bla...\n')

    user_input = input("Please, enter folder:  ")
    main_path = Path(user_input)

    if user_input.casefold() == 'cancel':
        print('Canceling sorting...')
        return False

    elif main_path.exists() and main_path.is_dir():
        print(f'The folder which I will sort is: {main_path}\n')
        print('Sorting, please wait...')
        tree, folders_list = (get_files_tree_from(main_path))
        sorting_files_to_folders(tree, KNOW_FILE_EXTENSION, main_path)
        print(f'Folder {main_path} has been sorted!')
        return True

    else:
        print('This folder doesn\'t exist. \nPlease try again or write "cancel" to cancel sorting.')


# in case you run this module outside the master file
if __name__ == '__main__':
    main()
