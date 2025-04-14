import os
from langchain_gigachat.tools.giga_tool import giga_tool

@giga_tool
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
        return count
    except Exception as e:
        print(f"Ошибка при доступе к папке {folder_path}: {e}")
        return 0

# Пример использования:
if __name__ == "__main__":  
    folder_path = r"C:\Users\artem\YandexDisk\AI_Agent_4BT\AI-agent-for-business-requirements\examples of letters for test"
    file_count = count_files_in_folder.invoke(folder_path)
    print(f"Количество файлов в папке {folder_path}: {file_count}")

