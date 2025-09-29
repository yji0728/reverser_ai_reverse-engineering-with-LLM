from ..gpt.base_wrapper import BaseFunctionNameGPTWrapper
from ..config import load_user_config
import os


class GhidraFunctionNameGPTWrapper(BaseFunctionNameGPTWrapper):
    """
    GhidraFunctionNameGPTWrapper is a specialized class designed for use with Ghidra.
    It leverages the FunctionNameGPT class to generate function name suggestions based on the
    decompiler output of functions. This class serves as a bridge between Ghidra's decompiler output 
    and the FunctionNameGPT's capabilities, allowing automated, AI-driven renaming of functions 
    within the Ghidra environment based on the analysis of their decompiled code.
    This process facilitates more meaningful and descriptive function names,
    enhancing the readability and comprehensibility of reverse-engineered code.
    """

    def __init__(self, config_path=None):
        """
        Initializes the GhidraFunctionNameGPTWrapper instance with a given configuration.
        
        Parameters:
        - config_path (str): Path to configuration file. If None, uses default config.
        """
        self._config_path = config_path
        # Initialize base class
        super().__init__()

    def read_config(self):
        """
        Reads the configuration from a config file and creates a config dictionary.

        The configuration includes settings for optimizing speed and resource usage by the FunctionNameGPT
        based on the user's hardware capabilities and preferences.

        Returns:
        - dict: A dictionary containing configuration settings.
        """
        if self._config_path and os.path.exists(self._config_path):
            return load_user_config(self._config_path)
        else:
            # Default configuration for Ghidra integration
            return {
                "use_mmap": True,
                "n_threads": 0,
                "n_gpu_layers": 99,
                "seed": 0,
                "verbose": False
            }

    def get_decompiler_output(self, function, decompiler=None):
        """
        Extracts and returns the decompiler output for a given function as a string.
        This method implements the abstract method from BaseFunctionNameGPTWrapper.

        Parameters:
        - function: A Ghidra Function object.
        - decompiler: A Ghidra DecompInterface object (optional for this interface).

        Returns:
        - str: The decompiler output for the function, formatted as a string.
        """
        return self._get_ghidra_decompiler_output(function, decompiler)

    @staticmethod
    def _get_ghidra_decompiler_output(function, decompiler):
        """
        Extracts and returns the decompiler output for a given function as a string.

        Parameters:
        - function: A Ghidra Function object.
        - decompiler: A Ghidra DecompInterface object.

        Returns:
        - str: The decompiler output for the function, formatted as a string.
        """
        try:
            # Decompile the function
            decompile_results = decompiler.decompileFunction(function, 30, None)
            
            if decompile_results and decompile_results.decompileCompleted():
                # Get the C code representation
                c_code = decompile_results.getDecompiledFunction().getC()
                return str(c_code)
            else:
                # Fallback to function signature if decompilation fails
                return f"{function.getSignature()}"
        except Exception as e:
            print(f"Error decompiling function {function.getName()}: {e}")
            return f"{function.getSignature()}"

    def get_function_name_suggestion(self, function, decompiler):
        """
        Queries NameGPT to obtain a suggested name for a given function based on its decompiler output.

        Parameters:
        - function: A Ghidra Function object.
        - decompiler: A Ghidra DecompInterface object.

        Returns:
        - str: The suggested function name.
        """
        # Get decompiler output for the function and query FunctionNameGPT for a name suggestion
        decompiler_output = self._get_ghidra_decompiler_output(function, decompiler)
        return self.name_gpt.get_function_name_suggestion(decompiler_output)

    def log_info(self, message):
        """
        Logs an informational message using Ghidra's logging system.
        
        Parameters:
        - message (str): The message to log.
        """
        print(f"[INFO] {message}")

    def log_warn(self, message):
        """
        Logs a warning message using Ghidra's logging system.
        
        Parameters:
        - message (str): The warning message to log.
        """
        print(f"[WARN] {message}")

    def get_function_name(self, function_obj):
        """
        Gets the current name of the function.
        
        Parameters:
        - function_obj: A Ghidra Function object.
        
        Returns:
        - str: The current function name.
        """
        return function_obj.getName()

    def set_function_name(self, function_obj, name):
        """
        Sets the name of the function.
        
        Parameters:
        - function_obj: A Ghidra Function object.
        - name (str): The new function name.
        """
        try:
            # Import SourceType if available
            from ghidra.program.model.symbol import SourceType
            function_obj.setName(name, SourceType.USER_DEFINED)
        except ImportError:
            # Fallback if SourceType is not available
            function_obj.setName(name, None)

    def apply_suggestion(self, function, decompiler=None):
        """
        Obtains a suggested name for a given function and applies this suggestion to the function
        within Ghidra's database.

        Parameters:
        - function: A Ghidra Function object to rename.
        - decompiler: A Ghidra DecompInterface object. If None, creates a new one.
        """
        # Create decompiler interface if not provided
        if decompiler is None:
            try:
                from ghidra.app.decompiler import DecompInterface
                from ghidra.util.task import ConsoleTaskMonitor
                
                decompiler = DecompInterface()
                decompiler.openProgram(function.getProgram())
            except ImportError:
                self.log_warn("Error: Ghidra modules not available. This wrapper should be used within Ghidra environment.")
                return
            except Exception as e:
                self.log_warn(f"Error initializing decompiler: {e}")
                return

        # Store decompiler for use in get_decompiler_output
        self._current_decompiler = decompiler
        
        # Use the base class safe apply suggestion method
        self.safe_apply_suggestion(function)
        
        # Clean up
        self._current_decompiler = None

    def get_decompiler_output(self, function_obj):
        """
        Override to use the stored decompiler interface.
        
        Parameters:
        - function_obj: A Ghidra Function object.
        
        Returns:
        - str: The decompiler output for the function, formatted as a string.
        """
        decompiler = getattr(self, '_current_decompiler', None)
        if decompiler is None:
            # Fallback - try to create a new decompiler
            try:
                from ghidra.app.decompiler import DecompInterface
                decompiler = DecompInterface()
                decompiler.openProgram(function_obj.getProgram())
            except:
                return f"{function_obj.getSignature()}"
        
        return self._get_ghidra_decompiler_output(function_obj, decompiler)