# ReverserAI: Rename All Functions
# @author Tim Blazytko
# @category ReverserAI
# @keybinding
# @menupath Tools.ReverserAI.Rename All Functions
# @toolbar

"""
ReverserAI Ghidra Script: Rename All Functions

This script integrates ReverserAI with Ghidra to automatically suggest and apply
semantically meaningful function names based on decompiler output using local LLMs.

Usage:
1. Place this script in your Ghidra scripts directory
2. Install ReverserAI: pip install -e /path/to/reverser_ai
3. Run the script from Ghidra's script manager or via the Tools menu
4. Optionally, create a configuration file to customize LLM settings

The script will:
- Iterate through all functions in the current program
- Generate decompiler output for each function
- Query the local LLM for suggested function names  
- Apply the suggestions to rename functions in Ghidra
"""

import sys
import os

# Add the ReverserAI package to the Python path
# Adjust this path to where you installed ReverserAI
try:
    from reverser_ai.ghidra import rename_all_functions
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
    Main function to rename all functions in the current program using ReverserAI.
    """
    # Get the current program
    program = getCurrentProgram()
    if program is None:
        print("No program is currently open")
        return

    print("Starting ReverserAI function renaming for program: {}".format(program.getName()))
    print("This may take a while depending on the number of functions...")

    try:
        # Initialize decompiler interface
        decompiler = DecompInterface()
        decompiler.openProgram(program)

        # Create a transaction for the renaming operations
        transaction_id = program.startTransaction("ReverserAI Rename All Functions")
        
        try:
            # Use ReverserAI to rename all functions
            rename_all_functions(program)
            print("Function renaming completed successfully")
            
        except Exception as e:
            print(f"Error during function renaming: {e}")
            program.endTransaction(transaction_id, False)  # Rollback on error
            return
            
        finally:
            # Always end the transaction
            if program.getCurrentTransaction() is not None:
                program.endTransaction(transaction_id, True)  # Commit changes
        
        # Cleanup
        decompiler.dispose()
        
    except Exception as e:
        print(f"Error initializing decompiler or starting transaction: {e}")
    
    print("ReverserAI function renaming process completed")


if __name__ == "__main__":
    main()