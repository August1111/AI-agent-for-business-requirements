from langgraph.graph import StateGraph, END, MessagesState


def should_continue(state: MessagesState) -> str:
    """
    Функция для проверки, содержит ли последнее сообщение вызовы инструментов.
    Если tool_calls есть – возвращаем имя узла "tools_node", иначе – сигнал завершения (END).
    """
    messages = state.get("messages", [])
    if messages:
        last_message = messages[-1]
        # Проверяем, есть ли атрибут tool_calls и не пустой ли он
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools_node"
    return END


def build_workflow():
    """
    Собирает workflow (граф) из двух узлов:
      - "llm_node": узел, где LLM генерирует ответы и формирует tool_calls.
      - "tools_node": узел, который обрабатывает вызовы инструментов.
    Граф настроен так, что после работы инструмента всегда возвращается к LLM-узлу,
    а если LLM не генерирует tool_calls, workflow завершается.
    """
    # Импортируем функцию узла LLM из модуля agent/llm_node.py
    from agent.llm_node import gather_data
    # Импортируем функцию узла инструментов из модуля agent/tool_node.py
    from agent.tool_node import run_tools

    # Создаем граф состояния с типом состояния MessagesState
    workflow = StateGraph(MessagesState)

    # Добавляем узлы
    workflow.add_node("llm_node", gather_data)
    workflow.add_node("tools_node", run_tools)

    # Устанавливаем начальный узел (entry point) – LLM Node
    workflow.set_entry_point("llm_node")

    # Условный переход: если в последнем сообщении LLM есть tool_calls, переходим в tools_node,
    # иначе workflow завершается.
    workflow.add_conditional_edges("llm_node", should_continue, ["tools_node", END])

    # После работы tools_node всегда возвращаемся к узлу LLM для дальнейшей генерации.
    workflow.add_edge("tools_node", "llm_node")

    return workflow.compile()


if __name__ == "__main__":
    # Пример запуска workflow с пустым начальным состоянием.
    initial_state: MessagesState = {"messages": []}
    wf = build_workflow()
    result = wf.invoke(initial_state)
    print("Workflow завершен. Финальное состояние:")
    print(result)
