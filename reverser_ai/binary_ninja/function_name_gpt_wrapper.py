from binaryninja import log_info, log_warn
from binaryninja.settings import Settings

from ..gpt.base_wrapper import BaseFunctionNameGPTWrapper


class FunctionNameGPTWrapper(BaseFunctionNameGPTWrapper):
    """
    FunctionNameGPTWrapper is a specialized class designed for use with Binary Ninja.
    It leverages the FunctionNameGPT class to generate function name suggestions based on the
    High-Level Intermediate Language (HLIL) decompiler output of functions. This class serves as a bridge between
    Binary Ninja's decompiler output and the FunctionNameGPT's capabilities, allowing automated, AI-driven renaming
    of functions within the Binary Ninja environment based on the analysis of their decompiled code.
    This process facilitates more meaningful and descriptive function names,
    enhancing the readability and comprehensibility of reverse-engineered code.
    """

    def __init__(self):
        """
        Initializes the FunctionNameGPTWrapper instance with a given configuration.
        """
        # Read GPT config from Binary Ninja Settings and initialize base class
        super().__init__()

    @staticmethod
    def read_config():
        """
        Reads the configuration from Binary Ninja Settings and creates a config dictionary.

        The configuration includes settings for optimizing speed and resource usage by the FunctionNameGPT
        based on the user's hardware capabilities and preferences.

        Returns:
        - dict: A dictionary containing configuration settings read from Binary Ninja.
        """
        config = {}
        # Access each setting and specify the correct setting identifier
        config["use_mmap"] = Settings().get_bool("reverser_ai.use_mmap")
        config["n_threads"] = Settings().get_integer("reverser_ai.n_threads")
        config["n_gpu_layers"] = Settings().get_integer(
            "reverser_ai.n_gpu_layers")
        config["seed"] = Settings().get_integer("reverser_ai.seed")
        config["verbose"] = Settings().get_bool("reverser_ai.verbose")

        return config

    @staticmethod
    def get_hlil_output(f):
        """
        Extracts and returns the HLIL (High-Level Intermediate Language) decompiler output for a given function
        as a string.

        Parameters:
        - f (Function): A BinaryNinja Function object.

        Returns:
        - str: The HLIL decompiler output for the function, formatted as a string.
        """
        # Generate a formatted string from the HLIL lines of the function
        return f"{str(f)}\n" + ''.join(["\t" + line + "\n" for line in map(str, f.hlil.root.lines)])

    def get_decompiler_output(self, function_obj):
        """
        Extracts and returns the decompiler output for a given function as a string.
        This method implements the abstract method from BaseFunctionNameGPTWrapper.

        Parameters:
        - function_obj: A BinaryNinja Function object.

        Returns:
        - str: The decompiler output for the function, formatted as a string.
        """
        return self.get_hlil_output(function_obj)

    def get_function_name_suggestion(self, f):
        """
        Queries NameGPT to obtain a suggested name for a given function based on its HLIL decompiler output.

        Parameters:
        - f (Function): A BinaryNinja Function object.

        Returns:
        - str: The suggested function name.
        """
        # Use the base class implementation
        return super().get_function_name_suggestion(f)

    def log_info(self, message):
        """
        Logs an informational message using Binary Ninja's logging system.
        
        Parameters:
        - message (str): The message to log.
        """
        log_info(message, logger="ReverseAI")

    def log_warn(self, message):
        """
        Logs a warning message using Binary Ninja's logging system.
        
        Parameters:
        - message (str): The warning message to log.
        """
        log_warn(message, logger="ReverseAI")

    def get_function_name(self, function_obj):
        """
        Gets the current name of the function.
        
        Parameters:
        - function_obj: A BinaryNinja Function object.
        
        Returns:
        - str: The current function name.
        """
        return function_obj.name

    def set_function_name(self, function_obj, name):
        """
        Sets the name of the function.
        
        Parameters:
        - function_obj: A BinaryNinja Function object.
        - name (str): The new function name.
        """
        function_obj.name = name

    def apply_suggestion(self, f):
        """
        Obtains a suggested name for a given function and applies this suggestion to the function
        within Binary Ninja's database.

        Parameters:
        - f (Function): A BinaryNinja Function object to rename.
        """
        # Use the safe apply suggestion method from the base class
        self.safe_apply_suggestion(f)
