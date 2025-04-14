import os

def analyze_file_tool(folder_path: str, file_name: str, llm) -> str:
    """
    Инструмент для обработки файла.
    
    Аргументы:
      folder_path: Путь к папке, где лежат файлы.
      file_name: Имя файла, который необходимо обработать.
      llm: Объект модели LLM (например, GigaChat), через который производится вызов.
      
    Действия:
      1. Читает содержимое файла.
      2. Помечает файл как обработанный (перемещает его в подпапку "processed").
      3. Формирует промпт вида:
         "Проанализируй содержимое этого файла. Если оно относится к продукту Монеты, извлеки из него требования к данному продукту.
          Вот содержимое файла:
          <содержимое файла>"
      4. Вызывает LLM для анализа и возвращает ответ.
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
    
    # Формирование промпта для LLM
    prompt = (
        f"Проанализируй содержимое этого файла. Если оно относится к продукту Монеты, "
        f"извлеки из него требования к данному продукту.\n\n"
        f"Содержимое файла ({file_name}):\n{content}"
    )
    
    # Вызов модели LLM с заданным промптом
    llm_response = llm.run(prompt)
    
    return llm_response

