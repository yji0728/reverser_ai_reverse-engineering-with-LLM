from abc import ABC, abstractmethod
from .function_name_gpt import FunctionNameGPT


class BaseFunctionNameGPTWrapper(ABC):
    """
    Abstract base class for tool-specific function name GPT wrappers.
    
    This class provides a common interface and shared functionality for different
    reverse engineering tools (Binary Ninja, Ghidra, IDA, etc.) to integrate
    with the FunctionNameGPT system.
    
    Subclasses must implement the abstract methods to provide tool-specific
    functionality for reading configuration, extracting decompiler output,
    and applying function name suggestions.
    """

    def __init__(self, config=None):
        """
        Initializes the wrapper instance with a given configuration.
        
        Parameters:
        - config (dict): Configuration dictionary. If None, read_config() will be called.
        """
        if config is None:
            config = self.read_config()
        self.name_gpt = FunctionNameGPT(config)

    @abstractmethod
    def read_config(self):
        """
        Reads the configuration and creates a config dictionary.
        
        This method should be implemented by subclasses to read configuration
        from tool-specific sources (settings files, UI preferences, etc.).

        Returns:
        - dict: A dictionary containing configuration settings.
        """
        pass

    @abstractmethod
    def get_decompiler_output(self, function_obj):
        """
        Extracts and returns the decompiler output for a given function as a string.

        Parameters:
        - function_obj: A tool-specific function object.

        Returns:
        - str: The decompiler output for the function, formatted as a string.
        """
        pass

    def get_function_name_suggestion(self, function_obj):
        """
        Queries the GPT model to obtain a suggested name for a given function 
        based on its decompiler output.

        Parameters:
        - function_obj: A tool-specific function object.

        Returns:
        - str: The suggested function name.
        """
        decompiler_output = self.get_decompiler_output(function_obj)
        return self.name_gpt.get_function_name_suggestion(decompiler_output)

    @abstractmethod
    def apply_suggestion(self, function_obj):
        """
        Obtains a suggested name for a given function and applies this suggestion
        to the function within the tool's database/environment.

        Parameters:
        - function_obj: A tool-specific function object to rename.
        """
        pass

    @abstractmethod
    def log_info(self, message):
        """
        Logs an informational message using the tool's logging system.
        
        Parameters:
        - message (str): The message to log.
        """
        pass

    @abstractmethod
    def log_warn(self, message):
        """
        Logs a warning message using the tool's logging system.
        
        Parameters:
        - message (str): The warning message to log.
        """
        pass

    def safe_apply_suggestion(self, function_obj):
        """
        Safely applies a suggestion with error handling and logging.
        
        This method provides a common error handling pattern that can be used
        by all tool-specific implementations.
        
        Parameters:
        - function_obj: A tool-specific function object to rename.
        """
        try:
            old_name = self.get_function_name(function_obj)
            suggested_name = self.get_function_name_suggestion(function_obj)
            self.log_info(f"Renaming {old_name} to {suggested_name}")
            self.set_function_name(function_obj, suggested_name)
        except ValueError as err:
            function_name = self.get_function_name(function_obj)
            self.log_warn(f"Function {function_name}: {err}")
        except Exception as e:
            function_name = self.get_function_name(function_obj)
            self.log_warn(f"Error processing function {function_name}: {e}")

    @abstractmethod
    def get_function_name(self, function_obj):
        """
        Gets the current name of the function.
        
        Parameters:
        - function_obj: A tool-specific function object.
        
        Returns:
        - str: The current function name.
        """
        pass

    @abstractmethod
    def set_function_name(self, function_obj, name):
        """
        Sets the name of the function.
        
        Parameters:
        - function_obj: A tool-specific function object.
        - name (str): The new function name.
        """
        pass