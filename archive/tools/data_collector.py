import os
import json
from langchain_gigachat.tools.giga_tool import giga_tool


@giga_tool
def data_collector(input_text: str) -> str:
    """
    Читает все текстовые файлы из указанной папки.

    Вход: путь к папке (строка).
    Выход: JSON-строка, где ключи — имена файлов, а значения — их содержимое.
    """
    folder_path = input_text.strip()
    result = {}

    if not os.path.isdir(folder_path):
        return json.dumps({"error": f"Папка '{folder_path}' не найдена."}, ensure_ascii=False)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                result[filename] = content
            except Exception as e:
                result[filename] = f"Ошибка чтения файла: {str(e)}"

    return json.dumps({"files": result}, ensure_ascii=False)


# Пример вызова (для тестирования, если запускать как скрипт)
if __name__ == "__main__":
    result = data_collector(r"C:\Users\artem\YandexDisk\AI_Agent_4BT\AI-agent-for-business-requirements\examples of letters for test")
    print(result)
