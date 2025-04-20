import os
import extract_msg

def data_collector(folder_path: str) -> str:
    try:
        # Получаем список всех файлов (без папок), отсортированный по имени
        files = sorted(
            [f for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f))]
        )

        if not files:
            return "Нет доступных файлов для обработки."

        # Собираем содержимое
        combined_content = ""
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            
            if file_name.lower().endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    combined_content += f"{file_name}\n{content}\n\n"
            elif file_name.lower().endswith(".msg"):
                try:
                    msg = extract_msg.Message(file_path)
                    msg_subject = msg.subject or ""
                    msg_body = msg.body or ""
                    content = f"Subject: {msg_subject}\nBody:\n{msg_body}"
                    combined_content += f"{file_name}\n{content}\n\n"
                except Exception as msg_error:
                    combined_content += f"{file_name}\nОшибка при чтении MSG файла: {msg_error}\n\n"

        # print(combined_content.strip())
        return combined_content.strip()
    
    except Exception as e:
        return f"Ошибка при обработке файлов: {str(e)}"
    
if __name__ == "__main__":
    result = data_collector(r'C:/Users/artem/YandexDisk/AI_Agent_4BT/AI-agent-for-business-requirements/examples')
    print(result)
