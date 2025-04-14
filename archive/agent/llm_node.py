import json
from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import SystemMessage, AIMessage
import dotenv

GIGA_KEY = dotenv.get_key('.env', 'GIGA_KEY')

# Создаем объект LLM для модели Gigachat 2 Max.
# Здесь можно задать max_tokens и другие параметры по необходимости.
llm = GigaChat(
        credentials=GIGA_KEY,  # замените на свой ключ
        verify_ssl_certs=False,
        scope="GIGACHAT_API_PERS",
        model="GigaChat-2-Max",
        auto_upload_images=True
    )

def gather_data(state):
    """
    Функция-узел LLM, которая:
      1. Принимает текущее состояние (MessagesState) с историей сообщений.
      2. Если в истории еще нет системного сообщения, добавляет его с инструкциями.
      3. Вызывает LLM (с учетом истории), чтобы сгенерировать новый ответ.
         Ответ может содержать специальные вызовы инструментов (tool_calls).
      4. Возвращает обновленное состояние с добавленным AI-ответом.
    """
    messages = state.get("messages", [])

    # Добавляем системное сообщение с инструкциями, если его еще нет.
    if not messages or not any(isinstance(m, SystemMessage) for m in messages):
        system_instructions = '''
Ты — AI-ассистент для составления бизнес-требований.
Твоя задача: на основе входящего запроса и имеющихся данных (например, переписок, документов, файлов)
сформировать итоговый документ бизнес-требований в формате JSON:
{"business_requirements": "текст требований"}

Если тебе нужны данные из документов, используй инструмент:
Action: folder_reader
Action Input: "<путь к папке>"

Если требуется уточнение у человека, используй:
Action: human
Action Input: "<текст запроса>"

Используй только указанный формат для вызова инструментов.
'''
        sys_msg = SystemMessage(content=system_instructions)
        # Добавляем системное сообщение в начало списка сообщений.
        messages.insert(0, sys_msg)

    # Вызываем LLM, передавая всю историю сообщений.
    response = llm.invoke(messages)

    # Отладочная информация: выводим, если модель сгенерировала вызовы инструментов.
    print("LLM generated tool_calls:", json.dumps(response.tool_calls, indent=2, ensure_ascii=False))
    print("LLM generated response:", json.dumps(response.content, indent=2, ensure_ascii=False))

    # Обновляем состояние: добавляем полученный ответ к истории сообщений.
    new_messages = messages + [response]
    return {"messages": new_messages}
