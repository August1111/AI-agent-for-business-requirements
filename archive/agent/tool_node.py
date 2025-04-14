import re
from langchain_core.messages import AIMessage


class ToolNode:
    """
    Узел для исполнения вызовов инструментов.
    При инициализации принимает список инструментов и создает словарь по их имени.
    """

    def __init__(self, tools):
        # Формируем словарь: ключ - имя инструмента, значение - объект инструмента
        self.tool_map = {tool.name: tool for tool in tools}

    def run_tools(self, state):
        """
        Проверяет последнее сообщение в состоянии на наличие вызова инструмента.
        Если найден вызов, парсит его, выполняет соответствующий инструмент и
        добавляет новое сообщение с результатом (Observation) в историю сообщений.
        """
        messages = state.get("messages", [])
        if not messages:
            return state

        # Получаем последнее сообщение (предполагается, что это AIMessage с tool_calls)
        last_message = messages[-1]
        tool_call = self.parse_tool_call(last_message.content)

        if tool_call:
            tool_name = tool_call["tool_name"]
            tool_input = tool_call["tool_input"]
            # Проверяем, есть ли такой инструмент
            if tool_name in self.tool_map:
                tool = self.tool_map[tool_name]
                result = tool.run(tool_input)
                observation = f"Observation: {result}"
            else:
                observation = f"Observation: ERROR - Unknown tool '{tool_name}'"

            # Создаем новое сообщение с результатом вызова инструмента
            obs_message = AIMessage(content=observation)
            messages.append(obs_message)
            state["messages"] = messages
        return state

    def parse_tool_call(self, content):
        """
        Ищет в тексте содержимое, соответствующее формату вызова инструмента:
        Action: <tool_name>
        Action Input: <tool_input>

        Если найдено, возвращает словарь с ключами "tool_name" и "tool_input",
        иначе возвращает None.
        """
        # Регулярное выражение для поиска вызова инструмента
        pattern = r"Action:\s*(\w+)\s*[\r\n]+Action Input:\s*(.*)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            tool_name = match.group(1).strip()
            tool_input = match.group(2).strip()
            return {"tool_name": tool_name, "tool_input": tool_input}
        return None


    def run_tools(state):
        """
        Функция-узел для использования в workflow.
        Ожидается, что в состоянии (state) в качестве ключа "tool_node" передан объект ToolNode.
        Если его нет, выбрасывается ошибка.
        """
        if "tool_node" not in state:
            raise ValueError("Объект ToolNode не передан в состояние (ключ 'tool_node').")
        tool_node_instance = state["tool_node"]
        return tool_node_instance.run_tools(state)
