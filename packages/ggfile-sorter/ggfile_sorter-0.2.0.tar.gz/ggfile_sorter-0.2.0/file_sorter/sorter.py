import os
import shutil

def sort_files(directory):
    # Расширенный словарь для сопоставления расширений файлов с категориями
    extensions = {
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.tex', '.md', '.epub', '.csv', '.xls', '.xlsx', '.ppt', '.pptx'],
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp', '.ico', '.raw', '.psd'],
        'videos': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.mpeg', '.3gp'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'],
        'code': ['.py', '.js', '.html', '.css', '.cpp', '.c', '.java', '.php', '.swift', '.go', '.rs', '.rb', '.ts'],
        'executables': ['.exe', '.msi', '.app', '.dmg', '.sh', '.bat'],
        'fonts': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
        'ebooks': ['.epub', '.mobi', '.azw', '.azw3'],
        'data': ['.json', '.xml', '.yaml', '.sql', '.db', '.sqlite'],
        'designs': ['.ai', '.psd', '.xd', '.sketch', '.fig'],
        '3d_models': ['.obj', '.stl', '.fbx', '.blend', '.dae'],
        'virtual_machines': ['.vdi', '.vmdk', '.ova', '.vhd']
    }

    # Проверяем существование директории
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Директория {directory} не существует.")

    # Проходим по всем файлам в директории
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_ext = os.path.splitext(filename)[1].lower()

            # Определяем категорию файла
            for category, exts in extensions.items():
                if file_ext in exts:
                    # Создаем папку для категории, если она еще не существует
                    category_path = os.path.join(directory, category)
                    if not os.path.exists(category_path):
                        os.makedirs(category_path)

                    # Перемещаем файл в соответствующую папку
                    destination = os.path.join(category_path, filename)
                    try:
                        shutil.move(file_path, destination)
                        print(f"Перемещен файл {filename} в папку {category}")
                    except Exception as e:
                        print(f"Ошибка при перемещении файла {filename}: {str(e)}")
                    break
            else:
                # Если расширение не найдено, помещаем файл в папку "other"
                other_path = os.path.join(directory, "other")
                if not os.path.exists(other_path):
                    os.makedirs(other_path)
                destination = os.path.join(other_path, filename)
                try:
                    shutil.move(file_path, destination)
                    print(f"Перемещен файл {filename} в папку other")
                except Exception as e:
                    print(f"Ошибка при перемещении файла {filename}: {str(e)}")

    print("Сортировка файлов завершена.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        directory_to_sort = sys.argv[1]
        try:
            sort_files(directory_to_sort)
        except FileNotFoundError as e:
            print(f"Ошибка: {str(e)}")
        except Exception as e:
            print(f"Произошла неожиданная ошибка: {str(e)}")
    else:
        print("Пожалуйста, укажите директорию для сортировки.")
        print("Использование: python sorter.py /путь/к/директории")