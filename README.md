# ReverserAI (v1.0.1)
Author: **Tim Blazytko**

_Provides automated reverse engineering assistance through the use of local large language models (LLMs) on consumer hardware._

## Description:

_ReverserAI_ is a research project designed to automate and enhance reverse engineering tasks through the use of locally-hosted large language models (LLMs). Operating entirely offline, this initial release features the automatic suggestion of high-level, semantically meaningful function names derived from decompiler output. _ReverserAI_ is provided as a Binary Ninja plugin; however, its architecture is designed to be extended to other reverse engineering platforms such as IDA and Ghidra.

While local LLMs do not match the performance and capabilities of their cloud-based counterparts like ChatGPT4 and require substantial computing resources, they represent a significant step forward in balancing performance with confidentiality requirements.

_ReverserAI_ serves as an initial exploration into the potential of local LLMs as aids in reverse engineering on consumer-grade hardware. It showcases what is currently achievable and plans to be a playground for future developments in the realm of AI-assisted reverse engineering.

Some example use cases can be found in [examples](./examples).

> [!NOTE]
> Disclaimer: My expertise in machine learning and LLMs is limited. There may exist more efficient models or methods to achieve similar tasks with greater performance. This project represents a culmination of research into viable configurations, offering a stable foundation with acceptable performance. Feedback and contributions to improve _ReverserAI_ are highly encouraged.


## Core Features

- **Offline Operation**: Runs LLMs entirely on local CPU/GPU, ensuring data privacy and security.

- **Automatic Function Naming**: Automatically suggests semantically meaningful function names from decompiler output.

- **Multi-Tool Integration**: Seamlessly integrates with multiple reverse engineering platforms:
  - **Binary Ninja**: Full plugin integration with UI commands
  - **Ghidra**: Script-based integration with decompiler API
  - **Extensible Architecture**: Designed for easy extension to IDA and other tools

- **Consumer Hardware Compatibility**: Optimized to run on consumer-grade hardware, such as Apple silicon architectures.


## Installation

### General Installation

_ReverserAI_ can be installed from source for use with multiple reverse engineering tools:

```bash
git clone https://github.com/mrphrazer/reverser_ai.git
cd reverser_ai

# install requirements
pip3 install -r requirements.txt

# install ReverserAI
pip3 install .
```

### Binary Ninja Plugin Installation

For Binary Ninja integration, _ReverserAI_ can be easily integrated via Binary Ninja's plugin manager. Alternatively, manually install in Binary Ninja's `plugins` folder using the commands above.

### Ghidra Integration

For Ghidra integration:

1. Install ReverserAI using the general installation steps above
2. Copy the scripts from `ghidra_scripts/` to your Ghidra scripts directory
3. Launch Ghidra and run the scripts from the Script Manager

Upon initial launch, the tool will automatically download the `mistral-7b-instruct-v0.2.Q4_K_M.gguf` large language model file (~5GB). The download time varies based on internet connection speed. To manually initiate the download, execute the [`model_download.py`](scripts/model_download.py) script.


## Hardware Requirements

For optimal LLM performance on consumer-grade hardware, a setup with multiple CPU threads or a powerful GPU is advised. _ReverserAI_ runs efficiently on systems with at least 16 GB of RAM and 12 CPU threads, with queries taking about 20 to 30 seconds. GPU optimizations, especially on Apple silicon devices, can reduce this to 2 to 5 seconds per query.


## Usage

_ReverserAI_ is accessible through Binary Ninja's user interface and via command line.

### User Interface

#### Binary Ninja

To invoke the plugin within Binary Ninja, navigate to `Plugins -> ReverserAI` and, for example, run "Rename All Functions":

<p align="left">
<img alt="Plugin Menu" src="imgs/plugin_menu.png" width="500"/>
</p>

Depending on the total number of functions in the binary, this may take a while. The AI-assisted function name suggestions will appear in the Log window:

<p align="center">
<img alt="Binary Ninja Log" src="imgs/plugin_results.png"/>
</p>

#### Ghidra

To use ReverserAI with Ghidra:

1. **Install ReverserAI** following the installation instructions above
2. **Copy Ghidra Scripts**: Copy the scripts from `ghidra_scripts/` to your Ghidra scripts directory
3. **Launch Ghidra** and open your target binary
4. **Run Scripts**: Access the scripts through Ghidra's Script Manager:
   - `ReverserAI_RenameAllFunctions.py` - Rename all functions in the program
   - `ReverserAI_RenameFunction.py` - Rename the currently selected function

The scripts will automatically:
- Initialize the decompiler interface
- Generate decompiled code for functions
- Query the local LLM for name suggestions
- Apply the suggestions to rename functions in Ghidra

#### Command Line

For testing and experimentation, use the standalone scripts:

```bash
# Test with Binary Ninja-style output
python3 scripts/gpt_function_namer.py example_config.toml

# Test with Ghidra-style output
python3 scripts/ghidra_function_namer.py example_config.toml
```


### Configuration

Configuring _ReverserAI_ to match your hardware setup optimizes its performance. Key configuration parameters include CPU and GPU utilization preferences: For powerful GPUs, configure _ReverserAI_ to primarily use GPU, reducing CPU threads to minimize overhead. Without a strong GPU, increase CPU thread usage to maximize processing power. For systems with balanced resources, allocate tasks between CPU and GPU for efficient operation. Further details on these parameters follow:

* `use_mmap`: Enables loading the entire model into memory (~5GB) when set to `true`. Recommended for performance improvement.

* `n_threads`:  Specifies the number of CPU threads to utilize. Maximize CPU thread count to the number of available CPU threads for full utilization, or set to 0 to disable.

* `n_gpu_layers`: Determines GPU layer usage. Enter values up to 99 for powerful GPUs, or 0 to disable GPU processing.

* `seed`: A fixed seed ensures deterministic behavior for debugging (consistent output for identical inputs). Modify the seed for varied responses.

* `verbose`:  Enabling `verbose` mode provides detailed logs about the model and configuration settings.

The default configuration prioritizes GPU performance and minimizes verbose output.


#### Binary Ninja

To adjust settings in Binary Ninja, open `Settings` and search for `reverser_ai`. Changes require Binary Ninja to be restarted.

<p align="center">
<img alt="Plugin Settings" src="imgs/plugin_settings.png"/>
</p>

Each change requires a restart of Binary Ninja.


#### Configuration Files

_ReverserAI_ now supports enhanced configuration files that allow tool-specific settings and more granular control. You can:

1. **Create a configuration template**:
   ```bash
   python3 scripts/config_manager.py create my_config.toml
   ```

2. **Validate your configuration**:
   ```bash
   python3 scripts/config_manager.py validate my_config.toml
   ```

3. **View tool-specific settings**:
   ```bash
   python3 scripts/config_manager.py tool-config my_config.toml ghidra
   ```

For detailed parameter adjustment, utilize the enhanced configuration system with files like [`example_config_full.toml`](example_config_full.toml) that support tool-specific settings:

```
$ time python3 scripts/gpt_function_namer.py example_config.toml
Suggested name: xor_two_numbers

real	0m1.550s
user	0m0.268s
sys	0m0.223s
```


## Code Organization

_ReverserAI_'s codebase maintains a clear separation between generic LLM functionalities and tool-specific integration, ensuring modularity and ease of extension. Below is an overview of the primary components:

- **`gpt` Folder**: Contains code for interacting with large language models (LLMs). This includes:
  - A generic agent (`agent.py`) for model-agnostic operations.
  - A specialized module (`function_name_gpt.py`) for generating function name suggestions.
  - A base wrapper class (`base_wrapper.py`) that provides common functionality for all tool integrations.

- **`binary_ninja` Folder**: Hosts wrapper instances that:
  - Utilize Binary Ninja features to produce decompiler outputs.
  - Interface with the `gpt` folder's agents, enabling LLM-powered function naming within Binary Ninja.
  - Inherit from the base wrapper class for consistent behavior.

- **`ghidra` Folder**: Contains Ghidra-specific integration components:
  - Ghidra function name wrapper (`function_name_gpt_wrapper.py`) that interfaces with Ghidra's decompiler API.
  - Manager class for singleton pattern implementation.
  - Utility functions for Ghidra-specific operations.

- **`ghidra_scripts` Folder**: Ready-to-use Ghidra scripts that:
  - Provide user-friendly interfaces for ReverserAI functionality within Ghidra.
  - Handle Ghidra-specific initialization and transaction management.
  - Can be directly imported into Ghidra's script manager.

- **`scripts` Folder**: Command-line utilities and demos:
  - Configuration management tools.
  - Standalone function naming demos for different tools.
  - Model download and setup utilities.
  

## Limitations and Future Work

_ReverserAI_ serves as a proof of concept that demonstrates the potential of leveraging local LLMs for reverse engineering tasks on consumer-grade hardware. Currently, its primary functionality is to offer function name suggestions, but there exists significant scope for enhancement and expansion. Future directions could include:

* Investigating additional interaction methods and parameters with LLMs to enhance quality and processing speed.

* Adding network communication for hosting the _ReverserAI_ agent on a powerful server, circumventing local hardware constraints.

* Fine-tuning existing models or developing specialized models tailored to reverse engineering needs.

* Expanding functionality to include code explanations, analysis, and bug detection, subject to scalability and feasibility.

* Extending support to additional reverse engineering platforms such as IDA Pro (Ghidra support has been added in this version).

* Implementing variable renaming, structure recovery, and other advanced reverse engineering assistance features.

This project welcomes further contributions, suggestions, and enhancements, including pull requests.


## Contact

For more information, contact [@mr_phrazer](https://twitter.com/mr_phrazer).
