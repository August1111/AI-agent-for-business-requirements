import json
import os
from dotenv import load_dotenv
from langchain_gigachat.tools.giga_tool import giga_tool
from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage

# Загружаем ключ из .env
load_dotenv()
GIGA_KEY = os.environ.get('GIGA_KEY')


@giga_tool
def relevance_classifier(inputs: dict) -> str:
    """
    Определяет, какие файлы относятся к продукту, указанному в inputs["product"].
    Формат входа:
    {
        "input_text": {
            "files": {
                "имя_файла1": "содержимое1",
                "имя_файла2": "содержимое2",
                ...
            }
        },
        "product": "Монеты"
    }
    """
    try:
        input_text = inputs.get("input_text", {})
        files = input_text.get("files", {})
        product = inputs.get("product", "")

        if not files or not product:
            return json.dumps({
                "status": "error",
                "explanation": "Отсутствуют файлы или название продукта."
            }, ensure_ascii=False)

        llm = GigaChat(
            credentials=GIGA_KEY,
            verify_ssl_certs=False,
            scope="GIGACHAT_API_PERS",
            model="GigaChat-2-Max",
            auto_upload_images=True
        )

        relevant = []
        irrelevant = []

        system_prompt = (
            f"Ты — ассистент по анализу бизнес-требований. "
            f"Твоя задача — определить, относится ли текст к продукту под названием \"{product}\"."
        )
        system_message = SystemMessage(content=system_prompt)

        for filename, content in files.items():
            user_prompt = (
                f"Вот содержимое файла:\n\n"
                f"{content}\n\n"
                "Сообщи, относится ли текст к указанному продукту. "
                "Ответь 'Yes' или 'No' и дай краткое пояснение."
            )
            user_message = HumanMessage(content=user_prompt)
            response = llm.invoke([system_message, user_message])
            answer = str(response.content)

            if "Yes" in answer:
                relevant.append({"file": filename, "explanation": answer})
            else:
                irrelevant.append(filename)

        return json.dumps({
            "status": "OK",
            "relevant_data": relevant,
            "irrelevant_data": irrelevant
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "explanation": str(e)
        }, ensure_ascii=False)

# Пример вызова (для тестирования, если запускать как скрипт)
if __name__ == "__main__":

    test_data = {
        "input_text": {
            "files": {
                "letter1.txt": "📧 1. Тема: Структура базы данных для каталога монет\nОт: Тимур Хабибуллин, Ведущий Backend-разработчик\nКому: Команда аналитиков и продуктовой разработки\nДата: 06.04.2025\n\nДобрый день, коллеги.\n\nНа основании предварительных требований к функционалу каталога монет, я подготовил предложение по структуре базы данных, которую мы планируем использовать. Это предварительная модель, и я прошу вас внимательно её рассмотреть и оставить комментарии до конца недели.\n\nБазовая таблица coins будет включать следующие поля: id, name, year, metal, weight, country, condition, price, description, image_urls.\n\nДополнительно предлагается выделить справочные таблицы: countries, metals, conditions.\n\nСпасибо!\n\nС уважением,\nТимур",
                "letter10.txt": "📧 10. Тема: Безопасность учётных записей пользователей\nОт: Алексей Морозов\n\nПожалуйста, подтвердите реалистичность сроков реализации требований по безопасности."
            }
        },
        "product": "Монеты"
    }

    result = relevance_classifier.invoke({"inputs": test_data})


    print(result)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
      