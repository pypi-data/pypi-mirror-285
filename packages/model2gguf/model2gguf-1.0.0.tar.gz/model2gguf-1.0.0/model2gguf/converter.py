import os
import subprocess
from huggingface_hub import snapshot_download, create_repo, upload_file, HfApi

def download_model(model_id, local_dir):
    """Download the model from Hugging Face."""
    snapshot_download(repo_id=model_id, local_dir=local_dir)

def clone_llama_cpp(repo_url, local_dir):
    """Clone the llama.cpp repository and install dependencies."""
    subprocess.run(["git", "clone", repo_url, local_dir], check=True)
    subprocess.run(["pip", "install", "-r", os.path.join(local_dir, "requirements.txt")], check=True)

def convert_to_gguf(model_dir, output_file, outtype="q8_0"):
    """Convert the Hugging Face model to a GGUF file."""
    script_path = os.path.join("llama.cpp", "convert_hf_to_gguf.py")
    subprocess.run(["python", script_path, model_dir, "--outfile", output_file, "--outtype", outtype], check=True)

def create_ollama_model(model_name, modelfile_path):
    """Create an Ollama model using the GGUF file."""
    # Check if modelfile_path exists and is accessible
    if not os.path.isfile(modelfile_path):
        raise FileNotFoundError(f"The file '{modelfile_path}' does not exist or is not accessible.")
    
    # Run the Ollama create command with proper handling of paths
    try:
        subprocess.run(["ollama", "create", model_name, "-f", modelfile_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while creating the Ollama model: {e}")
        raise

def run_ollama_model(model_name):
    """Run an Ollama model."""
    subprocess.run(["ollama", "run", model_name], check=True)

def huggingface_login(token):
    """Login to Hugging Face CLI."""
    subprocess.run(["huggingface-cli", "login", "--token", token, "--add-to-git-credential"], check=True)

def upload_file_to_huggingface(file_path, repo_id):
    """Upload a file to Hugging Face."""
    api = HfApi()
    user = api.whoami()["name"]
    repo_url = f"{user}/{repo_id}"

    # Check if the repository already exists
    try:
        api.repo_info(repo_url)
        print(f"Repository '{repo_url}' already exists.")
    except:
        create_repo(repo_id, private=True)
        print(f"Repository '{repo_url}' created.")

    upload_file(path_or_fileobj=file_path, path_in_repo=os.path.basename(file_path), repo_id=repo_url)

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Convert Hugging Face model to GGUF file and manage Ollama models")
    
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand for converting models
    convert_parser = subparsers.add_parser("convert", help="Convert Hugging Face model to GGUF file")
    convert_parser.add_argument("--model_id", type=str, required=True, help="Model ID from Hugging Face or path to pre-downloaded model")
    convert_parser.add_argument("--output_file", type=str, required=True, help="Output file for the GGUF format")
    convert_parser.add_argument("--outtype", type=str, default="q8_0", help="Output type for the GGUF format")
    convert_parser.add_argument("--local_dir", type=str, default="hf_model", help="Local directory to download or find the model")

    # Subcommand for creating Ollama models
    create_parser = subparsers.add_parser("create_ollama", help="Create Ollama model using GGUF file")
    create_parser.add_argument("--model_name", type=str, required=True, help="Name for the Ollama model")
    create_parser.add_argument("--modelfile_path", type=str, default="modelfile.txt", help="Path to the modelfile.txt")

    # Subcommand for running Ollama models
    run_parser = subparsers.add_parser("run_ollama", help="Run Ollama model")
    run_parser.add_argument("--model_name", type=str, required=True, help="Name of the Ollama model to run")

    # Subcommand for Hugging Face login
    login_parser = subparsers.add_parser("login", help="Login to Hugging Face")
    login_parser.add_argument("--token", type=str, required=True, help="Hugging Face token")

    # Subcommand for uploading model to Hugging Face
    upload_parser = subparsers.add_parser("upload", help="Upload model to Hugging Face")
    upload_parser.add_argument("--file_path", type=str, required=True, help="Path to the file to upload")
    upload_parser.add_argument("--repo_id", type=str, required=True, help="Hugging Face repository ID")

    args = parser.parse_args()

    if args.command == "convert":
        # Define directories
        local_model_dir = args.local_dir
        llama_repo_url = "https://github.com/ggerganov/llama.cpp"
        llama_local_dir = "llama.cpp"

        # Check if the model_id is a local path or a Hugging Face model ID
        if os.path.isdir(args.model_id):
            local_model_dir = args.model_id
        else:
            # Download model from Hugging Face
            download_model(args.model_id, local_model_dir)
        
        # Clone the llama.cpp repository and install dependencies
        clone_llama_cpp(llama_repo_url, llama_local_dir)
        
        # Convert the model to GGUF format
        convert_to_gguf(local_model_dir, args.output_file, args.outtype)

    elif args.command == "create_ollama":
        create_ollama_model(args.model_name, args.modelfile_path)

    elif args.command == "run_ollama":
        run_ollama_model(args.model_name)

    elif args.command == "login":
        huggingface_login(args.token)

    elif args.command == "upload":
        upload_file_to_huggingface(args.file_path, args.repo_id)

if __name__ == "__main__":
    main()
