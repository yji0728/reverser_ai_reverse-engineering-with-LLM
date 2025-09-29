from .function_name_gpt_wrapper import GhidraFunctionNameGPTWrapper
from .ghidra_manager import GhidraFunctionNameGPTManager
from .utils import is_derived_func_name

# Initialize the manager as a global variable to be reused across plugin functions
manager = GhidraFunctionNameGPTManager()


def rename_function(function):
    """
    Queries GhidraFunctionNameGPTWrapper for a function name suggestion and applies it to a single function.

    This function is intended to be used as a callback or a hook within the Ghidra scripting environment
    to rename a specific function.

    Args:
        function: The Ghidra function object to rename.
    """
    # Retrieve the singleton instance of the GPT manager
    gpt = manager.get_instance()

    # Apply the GPT-based name suggestion to the function
    gpt.apply_suggestion(function)


def rename_all_functions(program):
    """
    Iterates over all functions in a Ghidra program, querying a GPT-based model for name suggestions,
    and applies those suggestions to each function.

    This function implements a worklist algorithm to ensure that functions are renamed in an order that respects
    their call dependencies. Specifically, it aims to rename "leaf" functions (those that do not call other functions)
    before renaming functions that call them. This approach facilitates the propagation of contextual information
    and learned insights across function names, potentially leading to more accurate and context-aware renaming.

    Due to the reliance on a GPT-based model for suggestions and the iterative nature of the algorithm, this operation
    can be slow, especially for binaries with a large number of functions.

    Args:
        program: The Ghidra program containing the functions to be renamed.
    """
    # Retrieve the singleton instance of the GPT manager for name suggestions
    gpt = manager.get_instance()
    
    # Get the function manager from the program
    function_manager = program.getFunctionManager()
    
    # Initialize sets and lists for tracking processed and pending functions
    done = set()
    todo = []

    # Initial population of the worklist with all functions in the program
    functions = function_manager.getFunctions(True)  # True for forward iterator
    for function in functions:
        if function not in done:
            todo.append(function)

    # Process functions in the worklist, respecting call dependencies
    while len(todo) != 0:
        current = todo.pop()

        # Skip already processed functions
        if current in done:
            continue

        # Check if all callees of the current function have been processed
        called_functions = current.getCalledFunctions(None)  # Get all called functions
        callees_processed = True
        for callee in called_functions:
            if callee not in done:
                callees_processed = False
                break

        if callees_processed:
            # Apply the GPT-based name suggestion to the function if its actual name is not derived
            if not is_derived_func_name(current.getName()):
                gpt.apply_suggestion(current)
            # Mark the current function as processed
            done.add(current)

        # Re-add the current function to the worklist to ensure it's reconsidered after its callees are processed
        todo.append(current)

        # Add unprocessed callees to the worklist for processing
        for callee in called_functions:
            if callee not in done:
                todo.append(callee)