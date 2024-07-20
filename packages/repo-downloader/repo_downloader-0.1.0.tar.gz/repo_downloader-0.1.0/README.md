# Repo Downloader

Repo Downloader is a command-line tool that allows you to download files from a Git repository into a zipped directory. Very convenient for providing code files to LLMs.

## Installation

You can install Repo Downloader using pip:

```
pip install repo-downloader
```

## Usage

After installation, you can use the `repo-downloader` command:

```
repo-downloader [OPTIONS] [PATH]
```

Options:

- `--ignore-gitignore`: Ignore .gitignore file, do NOT use this option if you want to respect .gitignore rules
- `--output FILE`: Output zip file path (default: ~/Downloads/<directory_name>\_files.zip)

If no PATH is provided, it will use the current directory.

## Examples

1. Download files from the current directory:

   ```
   repo-downloader
   ```

2. Download files from a specific repository:

   ```
   repo-downloader /path/to/repository
   ```

3. Ignore .gitignore rules:

   ```
   repo-downloader --ignore-gitignore
   ```

4. Specify a custom output file:
   ```
   repo-downloader --output custom_name.zip
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
