import ast
import inspect

from openai.types.chat import ChatCompletionToolParam


class FunctionWrapper:
    """
    A wrapper class for extracting information from a function.

    Attributes:
    - func: The function to be wrapped.
    - info: A dictionary containing the extracted information from the function.
    """

    type_maps = {
        "int": "integer",
        "str": "string",
        "bool": "boolean",
        "float": "number",
        "list": "array",
        "dict": "object",
    }

    def __init__(self, func):
        """
        Initializes the FunctionWrapper object.

        Parameters:
        - func: The function to be wrapped.
        """
        self.func = func
        self.info = self.extract_function_info()

    def extract_function_info(self):
        """
        Extracts information from the wrapped function.

        Returns:
        - A dictionary containing the extracted information from the function.
        """
        source = inspect.getsource(self.func)
        while source.startswith("  "):
            source = "\n".join([line[2:] for line in source.split("\n")])
        try:
            tree = ast.parse(source)
        except SyntaxError:
            raise SyntaxError(f"Cannot parse function {self.func.__name__}.")

        # Extract function name
        function_name = tree.body[0].name if isinstance(tree.body[0], ast.FunctionDef) else None

        # Extract function description from docstring
        function_description = self.extract_description_from_docstring(self.func.__doc__)

        # Extract function arguments and their types
        args = tree.body[0].args if isinstance(tree.body[0], ast.FunctionDef) else None
        parameters = {"type": "object", "properties": {}}
        required = []
        if args:
            for arg in args.args:
                argument_name = arg.arg
                argument_type = self.extract_parameter_type(argument_name, self.func.__doc__)
                argument_type = str(argument_type).replace(" ", "").replace("\n", "")
                parameter_description = self.extract_parameter_description(
                    argument_name, self.func.__doc__
                )
                argument_type_ = argument_type
                if "list" in argument_type_:
                    argument_type = "list"
                if "optional" not in argument_type_:
                    required.append(argument_name)
                elif "," in argument_type:
                    argument_type = argument_type_.split(",")[0]
                elif " " in argument_type_:
                    argument_type = argument_type_.split(" ")[0]
                parameters["properties"][argument_name] = {
                    "type": self.type_maps.get(argument_type, argument_type),
                    "description": parameter_description,
                }
                if argument_type == "list":
                    item_type = argument_type_.split("[")[-1].split("]")[0]
                    item_type = self.type_maps.get(item_type, item_type)
                    parameters["properties"][argument_name]["items"] = dict(type=item_type)

        # Extract function return type
        return_type = None
        if isinstance(tree.body[0], ast.FunctionDef) and tree.body[0].returns:
            return_type = ast.get_source_segment(source, tree.body[0].returns)
            return_type = self.type_maps.get(return_type, return_type)

        function_info = {
            "name": function_name,
            "description": function_description,
            "parameters": {
                "type": "object",
                "properties": parameters["properties"] if args else None,
                "required": required if args else None,
            },
        }
        # if return_type:
        #     function_info["return_type"] = return_type
        # else:
        #     raise ValueError(f"Function {self.func.__name__} must have a return type.")

        return function_info

    def extract_description_from_docstring(self, docstring):
        """
        Extracts the function description from the docstring.

        Parameters:
        - docstring: The docstring of the function.

        Returns:
        - The function description.
        """
        if docstring:
            lines = docstring.strip().split("\n")
            description_lines = []
            for line in lines:
                line = line.strip()
                if (
                    line.startswith(":param")
                    or line.startswith(":type")
                    or line.startswith(":return")
                ):
                    break
                if line:
                    description_lines.append(line)
            return "\n".join(description_lines)
        return None

    def extract_parameter_type(self, parameter_name, docstring):
        """
        Extracts the type of a function parameter from the docstring.

        Parameters:
        - parameter_name: The name of the parameter.
        - docstring: The docstring of the function.

        Returns:
        - The type of the parameter.
        """
        if docstring:
            type_prefix = f":type {parameter_name}:"
            lines = docstring.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith(type_prefix):
                    return line.replace(type_prefix, "").strip()
        return None

    def extract_parameter_description(self, parameter_name, docstring):
        """
        Extracts the description of a function parameter from the docstring.

        Parameters:
        - parameter_name: The name of the parameter.
        - docstring: The docstring of the function.

        Returns:
        - The description of the parameter.
        """
        if docstring:
            param_prefix = f":param {parameter_name}:"
            lines = docstring.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith(param_prefix):
                    return line.replace(param_prefix, "").strip()
        return None

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def as_tool(self) -> ChatCompletionToolParam:
        return ChatCompletionToolParam(dict(type="function", function=self.info))


def function_info(func):
    """
    Returns a FunctionWrapper object containing the extracted information from the function.

    Parameters:
    - func: The function to extract information from.

    Returns:
    - A FunctionWrapper object containing the extracted information from the function.
    """
    return FunctionWrapper(func)
