import json
from langchain_core.messages import HumanMessage
from langgraph.graph import END, MessagesState
from workflow import build_workflow


def main():
    # Начальное сообщение от пользователя (запрос аналитика)
    prompt = "Составь бизнес требования по продукту 'LoyaltyProgram', используя данные из переписки, документов и файлов."
    input_messages = [HumanMessage(prompt)]

    # Создаем начальное состояние для графа (workflow)
    # В нашем случае состояние представляет собой словарь с ключом "messages"
    initial_state: MessagesState = {"messages": input_messages}

    # Строим граф (workflow) из узлов: LLM-узел и Tool-узел,
    # где узлы и переходы определены в модуле workflow.py.
    graph = build_workflow()

    # Запускаем workflow, передавая начальное состояние
    output_state = graph.invoke(initial_state)

    # Финальный вывод: последний message из состояния
    final_message = output_state["messages"][-1].content
    print("Final Output:")
    print(final_message)


if __name__ == "__main__":
    main()
