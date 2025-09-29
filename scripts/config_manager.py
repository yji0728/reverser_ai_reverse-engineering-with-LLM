#!/usr/bin/env python3
"""
ReverserAI Configuration Manager

This script helps users create, validate, and manage ReverserAI configuration files.

Usage:
    python3 config_manager.py create [output_path]     # Create a new config template
    python3 config_manager.py validate config_file     # Validate a config file
    python3 config_manager.py show config_file         # Show config values
    python3 config_manager.py tool-config config_file tool_name  # Show tool-specific config
"""

from reverser_ai.config import (
    get_default_config, 
    load_user_config, 
    save_config_template, 
    validate_config, 
    get_tool_config
)
import sys
import os
import json


def create_config(output_path: str) -> None:
    """Create a new configuration template."""
    try:
        save_config_template(output_path, include_examples=True)
        print(f"Configuration template created at: {output_path}")
        print("Edit this file to customize your ReverserAI settings.")
    except Exception as e:
        print(f"Error creating configuration template: {e}")
        sys.exit(1)


def validate_config_file(config_path: str) -> None:
    """Validate a configuration file."""
    try:
        config = load_user_config(config_path)
        validate_config(config)
        print(f"Configuration file '{config_path}' is valid.")
        
        # Show which tools are enabled
        if 'tools' in config:
            enabled_tools = [name for name, settings in config['tools'].items() 
                           if settings.get('enabled', False)]
            if enabled_tools:
                print(f"Enabled tools: {', '.join(enabled_tools)}")
            else:
                print("No tools are explicitly enabled.")
        
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error validating configuration: {e}")
        sys.exit(1)


def show_config(config_path: str) -> None:
    """Display configuration values."""
    try:
        config = load_user_config(config_path)
        print(f"Configuration from '{config_path}':")
        print("=" * 50)
        print(json.dumps(config, indent=2))
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)


def show_tool_config(config_path: str, tool_name: str) -> None:
    """Display tool-specific configuration."""
    try:
        config = load_user_config(config_path)
        tool_config = get_tool_config(config, tool_name)
        print(f"Configuration for tool '{tool_name}' from '{config_path}':")
        print("=" * 50)
        print(json.dumps(tool_config, indent=2))
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)


def show_defaults() -> None:
    """Display default configuration values."""
    config = get_default_config()
    print("Default ReverserAI Configuration:")
    print("=" * 40)
    print(json.dumps(config, indent=2))


def print_usage() -> None:
    """Print usage information."""
    print("ReverserAI Configuration Manager")
    print("=" * 40)
    print()
    print("Usage:")
    print("  python3 config_manager.py create [output_path]")
    print("    Create a new configuration template")
    print()
    print("  python3 config_manager.py validate config_file")
    print("    Validate a configuration file")
    print()
    print("  python3 config_manager.py show config_file")
    print("    Display configuration values")
    print()
    print("  python3 config_manager.py tool-config config_file tool_name")
    print("    Display tool-specific configuration")
    print("    Supported tools: binary_ninja, ghidra, ida")
    print()
    print("  python3 config_manager.py defaults")
    print("    Display default configuration values")
    print()
    print("Examples:")
    print("  python3 config_manager.py create my_config.toml")
    print("  python3 config_manager.py validate my_config.toml")
    print("  python3 config_manager.py tool-config my_config.toml ghidra")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "create":
        output_path = sys.argv[2] if len(sys.argv) > 2 else "reverser_ai_config.toml"
        create_config(output_path)
    
    elif command == "validate":
        if len(sys.argv) < 3:
            print("Error: Missing configuration file path")
            print_usage()
            sys.exit(1)
        validate_config_file(sys.argv[2])
    
    elif command == "show":
        if len(sys.argv) < 3:
            print("Error: Missing configuration file path")
            print_usage()
            sys.exit(1)
        show_config(sys.argv[2])
    
    elif command == "tool-config":
        if len(sys.argv) < 4:
            print("Error: Missing configuration file path or tool name")
            print_usage()
            sys.exit(1)
        show_tool_config(sys.argv[2], sys.argv[3])
    
    elif command == "defaults":
        show_defaults()
    
    else:
        print(f"Error: Unknown command '{command}'")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()