# HF to GGUF Converter

A Python package for converting Hugging Face models to GGUF files. This tool simplifies the process of transforming models for compatibility with the GGUF format, streamlining model conversion tasks.

## Features

- Convert models from Hugging Face to GGUF format
- Easy-to-use command-line interface
- Supports various output types
- Integrates with Ollama for model creation and execution

## Installation

You should have ```ollama``` installed in your system: https://ollama.com/

You can install the package from PyPI using pip:

```bash
pip install model2gguf
```

## Usage
After installing the package, you can use the model2gguf command to convert models.

## Basic Command
To convert a model, use the following command:
```bash
model2gguf convert --model_id "huggingface/model-id" --output_file "output_file.gguf"
```

### Command Options
- ```--model_id```: The Hugging Face model ID (e.g., "microsoft/Phi-3-mini-128k-instruct").
- ```--output_file```: The desired output file name for the GGUF file.
- ```--outtype```: The type of output (e.g., q8_0).
- ```--local_dir```: (Optional) The directory to download the model to, or the directory of the pre-downloaded model. If not specified, defaults to the current directory under the folder named : ```hf_model``` 

## Example
Convert the "distilgpt2" model and save the output as distilgpt2.gguf:

```bash
model2gguf --model_id "distilgpt2" --output_file "distilgpt2.gguf"
```
Specify a folder for downloading the model:

```bash
model2gguf --model_id "distilgpt2" --output_file "distilgpt2.gguf" --local_dir "models"
```

Use a pre-downloaded model from a specific folder:
```bash
model2gguf --model_id "path/to/pre-downloaded/model" --output_file "distilgpt2.gguf" 
```

## Ollama Integration
1. Create an Ollama Model:
```bash
model2gguf create_ollama --model_name "model-name" --modelfile_path "modelfile.txt"
```
This command creates an Ollama model using the GGUF file. The modelfile.txt should contain the path to your GGUF model file.

2. 
```bash
model2gguf run_ollama --model_name "model-name"
```
3. 
```bash
nvidia-smi -L
```
this command is to switch the usage of the model on top of a graphic card

4.
```bash
set CUDA_VISIBLE_DEVICES=GPU-{YOURE UUID}
```
This uuid comes up when you run the previous command just paste the alphanumerical value next to the gpu- uuid

## Contributing
Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository
2. Create a feature branch (git checkout -b feature-branch)
3. Commit your changes (git commit -am 'Add new feature')
4. Push to the branch (git push origin feature-branch)
5. Open a Pull Request
Please ensure your code adheres to the existing style and includes tests where applicable.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Authors
Rahul Patnaik (rpatnaik2005@gmail.com)
Krishna Dvaipayan (krishnadb.ei21@rvce.edu.in)

## Acknowledgments
- Special thanks to Georgi Gerganov the creator of llama.cpp.
- Special thanks to ollama for support us run the models locally.
- Inspired by various open-source projects and tools.

