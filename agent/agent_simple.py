from langchain_gigachat.chat_models import GigaChat
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
import dotenv
from langchain_core.tools import Tool
import os
from uuid import uuid4
from langchain_core.prompts import ChatPromptTemplate
import re
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field  

GIGA_KEY = dotenv.get_key('.env', 'GIGA_KEY')

# Создаем экземпляр LLM для модели Gigachat 2 Max.
# Здесь можно задать max_tokens и другие параметры по необходимости.
llm = GigaChat(
        credentials=GIGA_KEY,  # нужно заменить на ключ
        verify_ssl_certs=False,
        scope="GIGACHAT_API_PERS",
        model="gigachat-max", # выбрал первую модель, а не вторую т.к. при использовании второй происходит переполнение стека 
        top_p=0.2,
        timeout = 1000
    )

#Задаём инструменты, которыми может пользоваться агент (в виде функций).
#Описания к ним ниже
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
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                combined_content += f"{file_name}\n{content}\n\n"

        # print(combined_content.strip())
        return combined_content.strip()
    
    except Exception as e:
        return f"Ошибка при обработке файлов: {str(e)}"
    
def get_requirements(text: str, folder_path: str) -> str:

    try:
        # Создаем папку, если её нет
        os.makedirs(folder_path, exist_ok=True)

        # Формируем путь к файлу
        file_path = os.path.join(folder_path, "final_document.txt")

        # Сохраняем текст в файл
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text.strip())

        print(f"Документ успешно сохранён в: {file_path}")
        return file_path
    
    except Exception as e:
        print(f"❗Ошибка при сохранении файла: {str(e)}")
        return ""
        

#Это для того, чтобы чётко прописать какие аргументы инструмент должен принимать на вход ( без этого агент выполняет get_requirements с ошибкой)
class GetRequirementsInput(BaseModel):
    text: str = Field(description="Текст для сохранения")
    folder_path: str = Field(description="Путь к папке")

#Создаю массив tools с инструментами (Tool) для агента. 
#Можно объявляться инструменты и через декоратор @tool (или @giga_tool) перед функцией, но у меня это, к сожалению, не работает. Поэтому вручную.
tools = [
    Tool(
        name = 'data_collector',
        func = data_collector,
        description = """
            Объединяет данные из файлов в одну строку.
            Аргументы:
            folder_path: Путь к папке, в которой производится поиск файлов.
            Возвращает:
            Строку с наименованиями и содержимым всех файлов в папке.
    """
    ),
    StructuredTool (
        name = 'get_requirements',
        func = get_requirements,
        description = """
            Сохраняет переданный текст в указанный файл внутри заданной папки.
    
            Аргументы:
                text (str): Текст для сохранения.
                folder_path (str): Путь к папке.
                filename (str): Название файла (по умолчанию "final_document.txt").
            
            Возвращает:
                str: Полный путь к сохраненному файлу.
    """,
        args_schema=GetRequirementsInput
    )
]

#Тут пока явно объявляю переменные, для промта агенту т.к. пока не научился читать их с пользовательского запроса
folder = 'C:/Users/artem/YandexDisk/AI_Agent_4BT/AI-agent-for-business-requirements/examples'
product = 'Монеты'

#Промт - синтрукция для агента. get_requirements - он так и не выполняет.
system_prompt = f"""
Ты бизнес-аналитик. Всегда действуй строго по инструкции. Ты обязан выполнить все 3 шага инструкции! :

1. Сначала вызывай инструмент 'data_collector', передав ему путь к {folder}
2. Из тех файлов, которые вернул инструмент 'data_collector', выбери те, которые относятся к продукту {product} и выпиши из них бизнес-требования, если это возможно.
Результатом выполнения этого шага будет являться список бизнес-требований к продукту с указанием для каждого требования из какого именно файла оно было взято.
3. Проанализируй список требований, которые ты составил на предыдущем шаге и скомпилируй их в один чёткий и хорошо структурирванный текст. На каждое требование обязательно должна быть ссылка из какого файла оно взято.
Вызови инструмент 'get_requirements'. Передай ему текст, сформированный на предыдущем шаге и путь к папке: {folder}. 

Никогда не завершай разговор не выполнив все 3 шага. Заверши разговор только после получения результата от работы инструмента 'get_requirements'.

Запрещено писать Python-код, делать предположения, просить уточнений, описывать алгоритмы.
Ты должен сразу выполнять действия с помощью инструментов.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "{input}")
])

# Если при создании агента передавать отдельно promt и отдельно экземпляр llm, обогащённый инструментами, агент не работает. Поэтому сделал так.
processing_chain = prompt| llm.bind_tools(tools)

# Объявляю отдельный экземпляр класса MemorySaver, а не напрямую передаю MemorySaver в коде создания агента, чтобы можно было гибко смотреть состояния агента.
memory = MemorySaver()

age_zzz = create_react_agent(processing_chain
                                    , tools
                                    , checkpointer = memory
                                    )

# Перед запуском требуется генерировать thread_id (уникальный идентификатор сессии)
thread_id = str(uuid4())
config = {"configurable": {"thread_id": thread_id}}

# Запускаю агент 
user_prompt = r"Напиши бизнес требования к продукту Монеты. Папка: C:\Users\artem\YandexDisk\AI_Agent_4BT\AI-agent-for-business-requirements\examples"  
print("Вызов агента...")
age_zzz.invoke({"input": user_prompt}, config=config)

print("Чтение состояния памяти...")
result = memory.get(config)

print("Содержимое памяти:")
if isinstance(result, dict):
    for k, v in result.items():
        print(f"{k}:", v)
else:
    print(result)

messages = result.get("channel_values", {}).get("messages", [])

# Ниже просто, чтобы вывести в консоль последнее сообщение от модели
# Фильтруем только AIMessage
ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]

# Берём последнее
if ai_messages:
    last_ai_message = ai_messages[-1]
    print("Последнее сообщение от модели:")
    print(last_ai_message.content)
else:
    print("AIMessage не найдено.")
