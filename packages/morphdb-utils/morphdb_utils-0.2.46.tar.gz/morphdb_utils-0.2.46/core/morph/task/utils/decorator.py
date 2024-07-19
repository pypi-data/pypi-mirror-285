import ast
from typing import Any, Dict, List, Union


class DecoratorParser:
    @staticmethod
    def parse_decorator(decorator: ast.AST) -> Union[str, Dict[str, Any]]:
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            decorator_info: Dict[str, Any] = {
                "name": (
                    decorator.func.id if isinstance(decorator.func, ast.Name) else ""
                ),
                "args": [],
                "keywords": {},
            }
            for arg in decorator.args:
                if isinstance(arg, ast.Constant):
                    decorator_info["args"].append(arg.value)
                elif isinstance(arg, ast.Str):
                    decorator_info["args"].append(arg.s)
                elif isinstance(arg, ast.JoinedStr):
                    decorator_info["args"].append(DecoratorParser.parse_joined_str(arg))
            for kw in decorator.keywords:
                if isinstance(kw.value, ast.Constant):
                    decorator_info["keywords"][kw.arg] = kw.value.value
                elif isinstance(kw.value, ast.JoinedStr):
                    decorator_info["keywords"][
                        kw.arg
                    ] = DecoratorParser.parse_joined_str(kw.value)
                elif isinstance(kw.value, ast.Str):
                    decorator_info["keywords"][kw.arg] = kw.value.s
            return decorator_info
        return ""

    @staticmethod
    def parse_joined_str(joined_str: ast.JoinedStr) -> str:
        parts = []
        for value in joined_str.values:
            if isinstance(value, ast.Str):
                parts.append(value.s)
            elif isinstance(value, ast.FormattedValue):
                parts.append(DecoratorParser.parse_formatted_value(value))
        return "".join(parts)

    @staticmethod
    def parse_formatted_value(formatted_value: ast.FormattedValue) -> str:
        if isinstance(formatted_value.value, ast.Name):
            return f"{formatted_value.value.id}"
        elif isinstance(formatted_value.value, ast.Attribute):
            return DecoratorParser.parse_attribute(formatted_value.value)
        elif isinstance(formatted_value.value, ast.Call):
            func = formatted_value.value.func
            if isinstance(func, ast.Name):
                func_name = func.id
            elif isinstance(func, ast.Attribute):
                func_name = DecoratorParser.parse_attribute(func)
            else:
                func_name = ""

            args = ", ".join(
                str(arg.value) if isinstance(arg, ast.Constant) else ""
                for arg in formatted_value.value.args
            )
            return f"{func_name}({args})"
        return ""

    @staticmethod
    def parse_attribute(attribute: ast.Attribute) -> str:
        value = attribute.value
        if isinstance(value, ast.Name):
            return f"{value.id}.{attribute.attr}"
        elif isinstance(value, ast.Attribute):
            return f"{DecoratorParser.parse_attribute(value)}.{attribute.attr}"
        return attribute.attr

    @staticmethod
    def get_decorators(
        code: str, function_name: str = "main"
    ) -> List[Union[str, Dict[str, Any]]]:
        tree = ast.parse(code)
        decorators: List[Union[str, Dict[str, Any]]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                for decorator in node.decorator_list:
                    parsed_decorator = DecoratorParser.parse_decorator(decorator)
                    if parsed_decorator:
                        decorators.append(parsed_decorator)
                break
        return decorators
