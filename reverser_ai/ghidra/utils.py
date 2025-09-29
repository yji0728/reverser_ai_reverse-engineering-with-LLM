import re


def is_derived_func_name(func_name):
    """
    Determines if a function name is likely system-generated or derived, as opposed to being manually assigned.

    This function checks if the provided function name matches common patterns used by decompilers and analysis tools
    for automatically generated function names. Such names typically include patterns like "FUN_", "sub_", "thunk_",
    numeric sequences, or library/system function prefixes.

    Parameters:
    - func_name (str): The name of the function to check.

    Returns:
    - bool: True if the function name appears to be derived/auto-generated, False otherwise.
    """
    if not func_name:
        return True

    # Common patterns for auto-generated function names in Ghidra and other tools
    derived_patterns = [
        r'^FUN_[0-9a-fA-F]+$',           # Ghidra default pattern: FUN_00401000
        r'^sub_[0-9a-fA-F]+$',           # IDA/other tools pattern: sub_401000
        r'^thunk_FUN_[0-9a-fA-F]+$',     # Ghidra thunk pattern
        r'^_*[0-9a-fA-F]{6,}$',          # Hexadecimal addresses: 401000, _401000
        r'^func_[0-9]+$',                # Generic numbered functions: func_1, func_2
        r'^function_[0-9]+$',            # Another generic pattern
        r'^loc_[0-9a-fA-F]+$',           # Location-based names
        r'^j_.*',                        # Jump/thunk prefixes
        r'^_*start$',                    # Entry point variations
        r'^_*main$',                     # Main function (sometimes auto-detected)
        r'^.*_[0-9a-fA-F]{6,}$',         # Functions with hex suffixes
    ]

    # Check against each pattern
    for pattern in derived_patterns:
        if re.match(pattern, func_name, re.IGNORECASE):
            return True

    # Additional checks for very short or suspicious names
    if len(func_name) <= 2:
        return True

    # Check for names that are all numbers or hex
    if re.match(r'^[0-9a-fA-F]+$', func_name):
        return True

    return False


def sanitize_function_name(suggested_name):
    """
    Sanitizes a suggested function name to ensure it conforms to valid identifier rules.

    Parameters:
    - suggested_name (str): The suggested function name from the GPT model.

    Returns:
    - str: A sanitized function name that is valid for use in Ghidra.
    """
    if not suggested_name:
        return "unnamed_function"

    # Remove extra whitespace
    name = suggested_name.strip()

    # Replace invalid characters with underscores
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)

    # Ensure the name starts with a letter or underscore
    if name and not re.match(r'^[a-zA-Z_]', name):
        name = '_' + name

    # Limit length to reasonable size
    if len(name) > 50:
        name = name[:50]

    # Remove consecutive underscores
    name = re.sub(r'_+', '_', name)

    # Remove trailing underscores
    name = name.rstrip('_')

    # Ensure we have a valid name
    if not name or name == '_':
        return "unnamed_function"

    return name


def get_function_context(function, program):
    """
    Extracts contextual information about a function that might be useful for naming.

    Parameters:
    - function: A Ghidra Function object.
    - program: The Ghidra program containing the function.

    Returns:
    - dict: A dictionary containing contextual information about the function.
    """
    context = {}
    
    try:
        # Basic function information
        context['name'] = function.getName()
        context['address'] = str(function.getEntryPoint())
        context['parameter_count'] = function.getParameterCount()
        context['return_type'] = str(function.getReturnType())
        
        # Call information
        called_functions = function.getCalledFunctions(None)
        context['calls_count'] = len(list(called_functions))
        
        calling_functions = function.getCallingFunctions(None)
        context['called_by_count'] = len(list(calling_functions))
        
        # Code units and instruction count (approximate)
        body = function.getBody()
        context['code_units_count'] = sum(1 for _ in program.getListing().getCodeUnits(body, True))
        
    except Exception as e:
        print(f"Error getting context for function {function.getName()}: {e}")
    
    return context