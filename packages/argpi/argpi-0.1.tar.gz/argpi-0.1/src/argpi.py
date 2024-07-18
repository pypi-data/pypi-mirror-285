from sys import argv as __args__, exit as __exit__
from enum import Enum
from functools import wraps

# call_once decorator
def call_once(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Use a special attribute to track if the function has been called
        if hasattr(self, '_called_functions') and func.__name__ in self._called_functions:
            raise Exception(f"{func.__name__} can only be called once.")
        if not hasattr(self, '_called_functions'):
            self._called_functions = {}
        self._called_functions[func.__name__] = True
        return func(self, *args, **kwargs)
    return wrapper


# class for storing argument description
class ArgumentDescription:
    def __init__(self):
        self.__name: str = ""
        self.__description: str = ""
        self.__shorthand: str = ""
    
    @call_once
    def name(self, text: str):
        self.__name = text
        return self
    
    @call_once
    def description(self, text: str):
        self.__description = text
        return self
    
    @call_once
    def shorthand(self, text: str):
        self.__shorthand = text
        return self
    
    @property
    def __name__(self) -> str:
        return self.__name

    @property
    def __description__(self) -> str:
        return self.__description
    
    @property
    def __shorthand__(self) -> str:
        return self.__shorthand

# Enum for choosing fetch type
class FetchType(Enum):
    SINGULAR = 1
    TILL_LAST = 2
    TILL_NEXT = 3

# class for argument parsing
class Arguments:
    def __init__(self):
        self.arguments: list[str]
        self.defined: list[dict] = []
        # self.errors: list[str] = []
        # self.ok: bool
        self.found: list[dict] = []
    
    @call_once
    def __capture__(self):
        self.arguments = __args__[1:]
        return self
    
    def __set_arguments__(self, custom_captured_arguments: list[str]):
        self.arguments = custom_captured_arguments
        return self
    
    def __add__(self, arg: str, argument_description: ArgumentDescription) -> None:
        if argument_description.__shorthand__ == "":
            raise ValueError("ArgumentDescription needs a mandatory shorthand. Try adding a shorthand!")
        

        data = {
            "__argument__":arg,
            "Description": argument_description, 
        }

        self.defined.append(data)
    
    def __analyse__(self) -> None:
        for x in self.arguments:
            for y in self.defined:
                if x == y["__argument__"] or x == y["Description"].__shorthand__:
                    self.found.append(y)
    
    def __there__(self, check: str) -> bool:
        returner = False
        for x in self.found:
            if x["__argument__"] == check or x["Description"].__shorthand__ == check:
                returner = True
                break

        return returner
    
    def __fetch__(self, arg: str, fetch_type: FetchType) -> str | list[str]:
        if not isinstance(fetch_type, FetchType):
            raise ValueError("Invalid FetchType provided for \"fetch\" function!")
        
        # 1 is singular
        # 2 is last
        # 3 is next

        if fetch_type.value == 1:
            try:
                # check if required arg is present in the arguments
                index = self.arguments.index(arg)
            except ValueError:
                # if not,
                # then check for its shorter counterpart
                for x in self.defined:
                    if x["__argument__"] == arg:
                        try:
                            index = self.arguments.index(x["Description"].__shorthand__)
                        except ValueError:
                            print(f"Argument \"{arg}\"Not Present!")
                            __exit__(1)
                    elif x["Description"].__shorthand__ == arg:
                        try:
                            index = self.arguments.index(x["__argument__"])
                        except ValueError:
                            print(f"Argument \"{arg}\"Not Present!")
                            __exit__(1)

            
            if index == len(self.arguments) - 1:
                raise ValueError(f"\"{arg}\" was expected to have one argument but none provided!")
            else:
                return self.arguments[index+1]
        elif fetch_type.value == 2:
            try:
                # check if required arg is present in the arguments
                index = self.arguments.index(arg)
            except ValueError:
                # if not,
                # then check for its shorter counterpart
                for x in self.defined:
                    if x["__argument__"] == arg:
                        try:
                            index = self.arguments.index(x["Description"].__shorthand__)
                        except ValueError:
                            print(f"Argument \"{arg}\"Not Present!")
                            __exit__(1)
                    elif x["Description"].__shorthand__ == arg:
                        try:
                            index = self.arguments.index(x["__argument__"])
                        except ValueError:
                            print(f"Argument \"{arg}\"Not Present!")
                            __exit__(1)
            
            if index == len(self.arguments) - 1:
                raise ValueError(f"\"{arg}\" was expected to have atleast one argument but none provided!")
            else:
                # error handling check
                for x in self.found:
                    if x["__argument__"] == arg or x["Description"].__shorthand__ == arg:
                        if self.found.index(x) != len(self.found) - 1:
                            ## if not the last argument,
                            ## run till next argument
                            return self.__fetch__(arg=arg, fetch_type=FetchType.TILL_NEXT)
                            
                return self.arguments[index+1:]
        elif fetch_type.value == 3:
            try:
                # check if required arg is present in the arguments
                index = self.arguments.index(arg)
            except ValueError:
                # if not,
                # then check for its shorter counterpart
                for x in self.defined:
                    if x["__argument__"] == arg:
                        try:
                            index = self.arguments.index(x["Description"].__shorthand__)
                        except ValueError:
                            print(f"Argument \"{arg}\"Not Present!")
                            __exit__(1)
                    elif x["Description"].__shorthand__ == arg:
                        try:
                            index = self.arguments.index(x["__argument__"])
                        except ValueError:
                            print(f"Argument \"{arg}\"Not Present!")
                            __exit__(1)
            
            if index == len(self.arguments) - 1:
                raise ValueError(f"\"{arg}\" was expected to have atleast one argument but none provided!")
            else:
                # error handling
                for x in self.found:
                    # for all found arguments, get the value of the argument
                    if x["__argument__"] == arg or x["Description"].__shorthand__ == arg:
                        # check if the index is the last index,
                        # if its the last index, then run __fetch__ again with proper FetchType
                        # i.e. Till Last
                        if self.found.index(x) == len(self.found) - 1:
                            return self.__fetch__(arg, FetchType.TILL_LAST)
                        else:
                            current_argument_index_in_found_list = self.found.index(x)
                            next_argument_index_in_found_list = current_argument_index_in_found_list + 1
                            break
                
                try:
                    result = self.arguments[index+1:self.arguments.index(self.found[next_argument_index_in_found_list]["__argument__"])]
                except ValueError:
                    result = self.arguments[index+1:self.arguments.index(self.found[next_argument_index_in_found_list]["Description"].__shorthand__)]
                
                return result
    
    def __argument_has_value__(self, arg: str) -> bool:
        try:
            # check if required arg is present in the arguments
            index = self.arguments.index(arg)
        except ValueError:
            # if not,
            # then check for its shorter counterpart
            for x in self.defined:
                if x["__argument__"] == arg:
                    try:
                        index = self.arguments.index(x["Description"].__shorthand__)
                    except ValueError:
                        return False
                elif x["Description"].__shorthand__ == arg:
                    try:
                        index = self.arguments.index(x["__argument__"])
                    except ValueError:
                        return False
        
        if index == len(self.arguments) - 1:
            return False
        else:
            next_value = self.arguments[index + 1]
            # check if next value is an argument
            for x in self.defined:
                if x["__argument__"] == next_value or x["Description"].__shorthand__ == next_value:
                    return False
        
        return True