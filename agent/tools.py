import os
from langchain_core.tools import tool

@tool 
def files_numerator(folder_path: str) -> int:
    """
            Подсчитывает количество файлов в указанной папке.
            Аргументы:
            folder_path: Путь к папке, в которой производится поиск файлов.
            Возвращает:
            Количество файлов (не считая папок) в указанной директории.
    """
    try:
        files = os.listdir(folder_path)
        count = sum(1 for file in files if os.path.isfile(os.path.join(folder_path, file)))
        print(count)
        return count
    except Exception as e:
        print(f"Ошибка при доступе к папке {folder_path}: {e}")
        print(0)
        return 0




@tool 
def requirements_agregator(folder_path: str, file_name: str) -> str:
    """
    Инструмент для обработки файла.
    
    Аргументы:
      folder_path: Путь к папке, где лежат файлы.
      file_name: Имя файла, который необходимо обработать.
      
    Действия:
      1. Читает содержимое файла.
      2. Помечает файл как обработанный (перемещает его в подпапку "processed").
      3. Формирует промпт вида:
         "Проанализируй содержимое этого файла. Если оно относится к продукту Монеты, извлеки из него требования к данному продукту.
          Вот содержимое файла:
          <содержимое файла>"
      4. Возвращает содержимое файла для анализа
    """
    
    # Полный путь к файлу
    file_path = os.path.join(folder_path, file_name)
    
    # Чтение содержимого файла
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return f"Ошибка чтения файла {file_name}: {str(e)}"
    
    # Отметка файла как обработанного: перемещаем его в папку "processed"
    processed_folder = os.path.join(folder_path, "processed")
    os.makedirs(processed_folder, exist_ok=True)  # создаём папку, если её нет
    try:
        new_path = os.path.join(processed_folder, file_name)
        os.rename(file_path, new_path)
    except Exception as e:
        # Если не удаётся переместить, можно продолжить, просто залогировав ошибку
        print(f"Не удалось переместить файл {file_name}: {str(e)}")

    print(content)
    return(content)
    

