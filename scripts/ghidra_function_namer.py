#!/usr/bin/env python3
"""
ReverserAI Ghidra Function Namer

This script demonstrates the use of ReverserAI with Ghidra-style decompiled code.
It shows how the GPT model can suggest meaningful function names based on 
decompiler output that resembles Ghidra's format.

Usage:
    python3 ghidra_function_namer.py [config_file.toml]

If no config file is provided, default settings will be used.
"""

from reverser_ai.gpt.function_name_gpt import FunctionNameGPT
from reverser_ai.config import load_user_config
import sys
import os


def generate_ghidra_style_function():
    """
    Generates and returns a string containing the source code of a C function in Ghidra's decompilation style.
    This function demonstrates a more complex example that includes pointer operations, loops, and 
    string operations that are commonly seen in Ghidra decompiler output.

    Returns:
        str: The source code of the C function as a string, formatted like Ghidra output.
    """
    c_code = """
undefined8 FUN_00401234(char *param_1,int param_2)

{
  size_t sVar1;
  char *pcVar2;
  int local_20;
  int local_1c;
  
  if (param_1 == (char *)0x0) {
    return 0;
  }
  sVar1 = strlen(param_1);
  if ((int)sVar1 < param_2) {
    return 0;
  }
  local_1c = 0;
  for (local_20 = 0; local_20 < param_2; local_20 = local_20 + 1) {
    if (param_1[local_20] != param_1[param_2 - local_20 + -1]) {
      return 0;
    }
  }
  return 1;
}
    """
    return c_code.strip()


def generate_memory_copy_function():
    """
    Generates a Ghidra-style decompilation of a memory copy function.
    
    Returns:
        str: The source code formatted like Ghidra decompiler output.
    """
    c_code = """
void * FUN_00401000(void *param_1,void *param_2,int param_3)

{
  int32_t i;
  void *r4 = param_2 - 1;
  void *r3 = param_1 - 1;
  do {
    char r5 = *(r4 + 1);
    r4 = r4 + 1;
    *(r3 + 1) = r5;
    r3 = r3 + 1;
    i = i - 1;
  } while (i != 0);
  return r3;
}
    """
    return c_code.strip()


def generate_string_comparison_function():
    """
    Generates a Ghidra-style decompilation of a string comparison function.
    
    Returns:
        str: The source code formatted like Ghidra decompiler output.
    """
    c_code = """
int FUN_00401500(char *param_1,char *param_2)

{
  char cVar1;
  char cVar2;
  
  do {
    cVar2 = *param_2;
    cVar1 = *param_1;
    param_1 = param_1 + 1;
    param_2 = param_2 + 1;
    if (cVar1 == '\\0') break;
  } while (cVar1 == cVar2);
  return (int)cVar1 - (int)cVar2;
}
    """
    return c_code.strip()


def main():
    """
    Main function that demonstrates ReverserAI's function naming capabilities
    with various Ghidra-style decompiled functions.
    """
    print("ReverserAI Ghidra Function Namer Demo")
    print("=" * 50)
    
    # Load configuration
    config_path = None
    if len(sys.argv) >= 2:
        config_path = sys.argv[1]
        if not os.path.exists(config_path):
            print(f"Error: Configuration file '{config_path}' not found.")
            sys.exit(1)
        print(f"Using configuration file: {config_path}")
        config = load_user_config(config_path)
    else:
        print("Using default configuration")
        config = {
            "use_mmap": True,
            "n_threads": 0,
            "n_gpu_layers": 99,
            "seed": 0,
            "verbose": False
        }

    # Initialize the FunctionNameGPT model
    print("Initializing GPT model...")
    gpt = FunctionNameGPT(config)
    print("Model initialized successfully")
    print()

    # Test functions
    test_functions = [
        ("Palindrome Check Function", generate_ghidra_style_function()),
        ("Memory Copy Function", generate_memory_copy_function()),
        ("String Comparison Function", generate_string_comparison_function())
    ]

    for description, c_function_code in test_functions:
        print(f"Testing: {description}")
        print("-" * 30)
        print("Decompiled code:")
        print(c_function_code)
        print()
        
        try:
            # Get function name suggestion
            suggested_name = gpt.get_function_name_suggestion(c_function_code)
            print(f"Suggested name: {suggested_name}")
        except Exception as e:
            print(f"Error getting suggestion: {e}")
        
        print()
        print("=" * 50)
        print()


if __name__ == "__main__":
    main()