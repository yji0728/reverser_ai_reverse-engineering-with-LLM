from .function_name_gpt_wrapper import GhidraFunctionNameGPTWrapper


class GhidraFunctionNameGPTManager:
    """
    Manages a single instance of GhidraFunctionNameGPTWrapper to ensure it is initialized only once across multiple
    uses in the Ghidra scripting environment.

    This class implements the singleton design pattern to manage the unique and static initialization
    of GhidraFunctionNameGPTWrapper, which facilitates the application of GPT-based function naming suggestions
    within the Ghidra analysis environment.

    Attributes:
        _ghidra_function_name_gpt (GhidraFunctionNameGPTWrapper or None): A singleton instance of GhidraFunctionNameGPTWrapper.
        _config_path (str): Path to the configuration file to use.
    """

    def __init__(self, config_path=None):
        """
        Initializes the manager with a specified configuration path.
        
        Parameters:
        - config_path (str): Path to configuration file. If None, uses default config.
        """
        self._ghidra_function_name_gpt = None
        self._config_path = config_path

    def get_instance(self):
        """
        Retrieves the singleton instance of GhidraFunctionNameGPTWrapper.

        If the instance has not been initialized, it initializes it.

        Returns:
            GhidraFunctionNameGPTWrapper: The initialized singleton instance of the wrapper.
        """
        if self._ghidra_function_name_gpt is None:
            self._ghidra_function_name_gpt = GhidraFunctionNameGPTWrapper(self._config_path)
        return self._ghidra_function_name_gpt

    def set_config_path(self, config_path):
        """
        Sets a new configuration path and resets the instance to force reinitialization.
        
        Parameters:
        - config_path (str): Path to configuration file.
        """
        self._config_path = config_path
        self._ghidra_function_name_gpt = None  # Reset instance to force reinitialization