import os
import zipfile
import tempfile
import shutil
import platform
from git import Repo
from git.exc import InvalidGitRepositoryError
import click
import sys

def get_default_downloads_dir():
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.path.expanduser("~"), "Downloads")
    elif system == "Darwin":  # macOS
        return os.path.expanduser("~/Downloads")
    else:  # Linux and other Unix-like systems
        return os.path.expanduser("~/Downloads")  # Most Linux distros use this by default

def get_files_to_download(repo_path, ignore_gitignore):
    repo = Repo(repo_path)
    all_files = []
    
    for root, dirs, files in os.walk(repo_path):
        if '.git' in dirs:
            dirs.remove('.git')
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, repo_path)
            all_files.append(relative_path)
    
    if ignore_gitignore:
        return all_files
    else:
        ignored = set(repo.ignored(all_files))
        return [f for f in all_files if f not in ignored]

def download_files(repo_path, output_zip, ignore_gitignore):
    files_to_download = get_files_to_download(repo_path, ignore_gitignore)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files_to_download:
            source_path = os.path.join(repo_path, file)
            dest_path = os.path.join(temp_dir, os.path.basename(file))
            shutil.copy2(source_path, dest_path)
        
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.basename(file_path))

def get_default_output_name(path):
    dir_name = os.path.basename(os.path.abspath(path))
    downloads_dir = get_default_downloads_dir()
    return os.path.join(downloads_dir, f"{dir_name}_files.zip")

@click.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--ignore-gitignore', is_flag=True, help='Ignore .gitignore file')
@click.option('--output', help='Output zip file path (default: <OS-specific Downloads folder>/<directory_name>_files.zip)')
def main(path, ignore_gitignore, output):
    """Download files from a Git repository into a zipped directory."""
    repo_path = os.path.abspath(path)
    
    if output is None:
        output = get_default_output_name(repo_path)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    try:
        download_files(repo_path, output, ignore_gitignore)
        click.echo(f"Files downloaded and zipped successfully to {output}")
    except InvalidGitRepositoryError:
        click.echo(f"Error: {repo_path} is not a valid Git repository.", err=True)
        sys.exit(1)  # Exit with status code 1 for invalid repository
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}", err=True)
        sys.exit(1)  # Exit with status code 1 for other errors

if __name__ == "__main__":
    main()