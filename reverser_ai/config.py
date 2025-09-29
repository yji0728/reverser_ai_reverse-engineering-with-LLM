import toml
import os
from typing import Dict, Any, Optional


def get_default_config() -> Dict[str, Any]:
    """
    Returns the default configuration for ReverserAI.
    
    Returns:
        dict: Default configuration settings.
    """
    return {
        # Model configuration
        "use_mmap": True,
        "n_threads": 0,
        "n_gpu_layers": 99,
        "seed": 0,
        "verbose": False,
        
        # Tool-specific settings
        "tools": {
            "binary_ninja": {
                "enabled": True,
                "decompiler_type": "hlil"  # High-Level IL
            },
            "ghidra": {
                "enabled": True,
                "decompiler_timeout": 30,
                "use_function_signature_fallback": True
            },
            "ida": {
                "enabled": False,  # Not implemented yet
                "decompiler_type": "hexrays"
            }
        },
        
        # Function naming settings
        "function_naming": {
            "max_name_length": 50,
            "sanitize_names": True,
            "skip_library_functions": True,
            "skip_derived_names": True
        }
    }


def load_user_config(config_path: str) -> Dict[str, Any]:
    """
    Loads and parses a TOML configuration file, merging with defaults.

    This function reads a TOML file specified by the `config_path` parameter,
    parses it into a Python dictionary, and merges it with default settings.

    Args:
        config_path (str): The path to the TOML configuration file.

    Returns:
        dict: The configuration settings parsed from the TOML file, merged with defaults.
    
    Raises:
        FileNotFoundError: If the configuration file doesn't exist.
        toml.TomlDecodeError: If the TOML file is malformed.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Start with default configuration
    config = get_default_config()
    
    try:
        # Load user configuration from TOML file
        with open(config_path, 'r') as config_file:
            user_config = toml.load(config_file)
        
        # Merge user configuration with defaults
        config = merge_configs(config, user_config)
        
    except toml.TomlDecodeError as e:
        raise toml.TomlDecodeError(f"Error parsing TOML configuration file {config_path}: {e}")
    
    return config


def merge_configs(default_config: Dict[str, Any], user_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merges user configuration with default configuration.
    
    Args:
        default_config (dict): Default configuration dictionary.
        user_config (dict): User configuration dictionary.
        
    Returns:
        dict: Merged configuration dictionary.
    """
    merged = default_config.copy()
    
    for key, value in user_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            merged[key] = merge_configs(merged[key], value)
        else:
            # Override or add new values
            merged[key] = value
    
    return merged


def get_tool_config(config: Dict[str, Any], tool_name: str) -> Dict[str, Any]:
    """
    Extracts tool-specific configuration from the main config.
    
    Args:
        config (dict): Main configuration dictionary.
        tool_name (str): Name of the tool (e.g., 'binary_ninja', 'ghidra').
        
    Returns:
        dict: Tool-specific configuration merged with global settings.
    """
    # Start with global settings (excluding tool-specific sections)
    tool_config = {k: v for k, v in config.items() if k not in ['tools', 'function_naming']}
    
    # Add tool-specific settings if they exist
    if 'tools' in config and tool_name in config['tools']:
        tool_config.update(config['tools'][tool_name])
    
    # Add function naming settings
    if 'function_naming' in config:
        tool_config['function_naming'] = config['function_naming']
    
    return tool_config


def save_config_template(output_path: str, include_examples: bool = True) -> None:
    """
    Saves a template configuration file with all available options.
    
    Args:
        output_path (str): Path where to save the template configuration.
        include_examples (bool): Whether to include example values and comments.
    """
    if include_examples:
        template_content = """# ReverserAI Configuration File
# Adjust according to your hardware capabilities and preferences

# Model Configuration
# ===================

# Optimize speed by loading the entire model into memory (requires ~5GB RAM)
use_mmap = true

# Utilize CPU threads; set to 0 to prioritize GPU usage over CPU
# For full CPU load, set to maximum number of available threads
n_threads = 0

# Utilize GPU layers for faster processing with a strong GPU
n_gpu_layers = 99

# Ensure deterministic model outputs by specifying a seed
seed = 0

# Toggle verbose logging of model configurations
verbose = false

# Tool-Specific Configuration
# ===========================

[tools.binary_ninja]
enabled = true
decompiler_type = "hlil"  # High-Level Intermediate Language

[tools.ghidra]
enabled = true
decompiler_timeout = 30
use_function_signature_fallback = true

[tools.ida]
enabled = false  # Not implemented yet
decompiler_type = "hexrays"

# Function Naming Settings
# ========================

[function_naming]
max_name_length = 50
sanitize_names = true
skip_library_functions = true
skip_derived_names = true
"""
    else:
        # Generate minimal config from defaults
        config = get_default_config()
        template_content = toml.dumps(config)
    
    with open(output_path, 'w') as f:
        f.write(template_content)


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validates configuration settings and raises exceptions for invalid values.
    
    Args:
        config (dict): Configuration dictionary to validate.
        
    Raises:
        ValueError: If configuration values are invalid.
    """
    # Validate basic types and ranges
    if not isinstance(config.get('use_mmap'), bool):
        raise ValueError("use_mmap must be a boolean value")
    
    if not isinstance(config.get('n_threads'), int) or config['n_threads'] < 0:
        raise ValueError("n_threads must be a non-negative integer")
    
    if not isinstance(config.get('n_gpu_layers'), int) or config['n_gpu_layers'] < 0:
        raise ValueError("n_gpu_layers must be a non-negative integer")
    
    if not isinstance(config.get('seed'), int):
        raise ValueError("seed must be an integer")
    
    if not isinstance(config.get('verbose'), bool):
        raise ValueError("verbose must be a boolean value")
    
    # Validate function naming settings if present
    if 'function_naming' in config:
        fn_config = config['function_naming']
        if 'max_name_length' in fn_config:
            if not isinstance(fn_config['max_name_length'], int) or fn_config['max_name_length'] <= 0:
                raise ValueError("function_naming.max_name_length must be a positive integer")
