# ReverserAI: Rename Selected Function
# @author Tim Blazytko
# @category ReverserAI
# @keybinding
# @menupath Tools.ReverserAI.Rename Current Function
# @toolbar

"""
ReverserAI Ghidra Script: Rename Selected Function

This script integrates ReverserAI with Ghidra to automatically suggest and apply
a semantically meaningful function name for the currently selected function based 
on decompiler output using local LLMs.

Usage:
1. Place this script in your Ghidra scripts directory
2. Install ReverserAI: pip install -e /path/to/reverser_ai
3. Select a function in Ghidra (cursor must be within the function)
4. Run the script from Ghidra's script manager or via the Tools menu
5. Optionally, create a configuration file to customize LLM settings

The script will:
- Get the currently selected function
- Generate decompiler output for the function
- Query the local LLM for a suggested function name  
- Apply the suggestion to rename the function in Ghidra
"""

import sys
import os

# Add the ReverserAI package to the Python path
try:
    from reverser_ai.ghidra import rename_function
    print("ReverserAI module loaded successfully")
except ImportError as e:
    print(f"Error importing ReverserAI: {e}")
    print("Please ensure ReverserAI is installed: pip install -e /path/to/reverser_ai")
    print("And that the installation path is in your Python path")
    sys.exit(1)

# Ghidra imports
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor


def main():
    """
    Main function to rename the currently selected function using ReverserAI.
    """
    # Get the current program
    program = getCurrentProgram()
    if program is None:
        print("No program is currently open")
        return

    # Get the currently selected function
    current_location = getCurrentLocation()
    if current_location is None:
        print("No location selected. Please place cursor within a function.")
        return

    function_manager = program.getFunctionManager()
    current_function = function_manager.getFunctionContaining(current_location.getAddress())
    
    if current_function is None:
        print("No function found at current location. Please place cursor within a function.")
        return

    print(f"Renaming function: {current_function.getName()} at {current_function.getEntryPoint()}")

    try:
        # Create a transaction for the renaming operation
        transaction_id = program.startTransaction("ReverserAI Rename Function")
        
        try:
            # Use ReverserAI to rename the function
            rename_function(current_function)
            print(f"Function renaming completed successfully")
            
        except Exception as e:
            print(f"Error during function renaming: {e}")
            program.endTransaction(transaction_id, False)  # Rollback on error
            return
            
        finally:
            # Always end the transaction
            if program.getCurrentTransaction() is not None:
                program.endTransaction(transaction_id, True)  # Commit changes
        
    except Exception as e:
        print(f"Error starting transaction: {e}")
    
    print("ReverserAI function renaming process completed")


if __name__ == "__main__":
    main()