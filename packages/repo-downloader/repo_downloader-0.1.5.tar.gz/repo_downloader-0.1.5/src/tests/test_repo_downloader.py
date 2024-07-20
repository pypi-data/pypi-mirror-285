import os
import tempfile
import zipfile
import shutil
from click.testing import CliRunner
from git import Repo
from src.repo_downloader.main import main, get_default_downloads_dir, get_default_output_name

def create_test_repo():
    temp_dir = tempfile.mkdtemp()
    repo = Repo.init(temp_dir)
    
    # Create some files
    with open(os.path.join(temp_dir, 'file1.txt'), 'w') as f:
        f.write('Content of file1')
    with open(os.path.join(temp_dir, 'file2.txt'), 'w') as f:
        f.write('Content of file2')
    
    # Create .gitignore
    with open(os.path.join(temp_dir, '.gitignore'), 'w') as f:
        f.write('ignored_file.txt\n')
    
    # Create ignored file
    with open(os.path.join(temp_dir, 'ignored_file.txt'), 'w') as f:
        f.write('This file should be ignored')
    
    # Add and commit files
    repo.index.add(['file1.txt', 'file2.txt', '.gitignore'])
    repo.index.commit('Initial commit')
    
    return temp_dir

def test_get_default_downloads_dir():
    downloads_dir = get_default_downloads_dir()
    assert os.path.exists(downloads_dir)
    assert 'Downloads' in downloads_dir or downloads_dir == tempfile.gettempdir()

def test_get_default_output_name():
    with tempfile.TemporaryDirectory() as temp_dir:
        output_name = get_default_output_name(temp_dir)
        assert output_name.endswith('_files.zip')
        assert get_default_downloads_dir() in output_name

def test_main_custom_output():
    runner = CliRunner()
    repo_path = create_test_repo()
    try:
        with runner.isolated_filesystem():
            custom_output = os.path.join(os.getcwd(), 'custom_output.zip')
            result = runner.invoke(main, [repo_path, '--output', custom_output])
            assert result.exit_code == 0
            assert os.path.exists(custom_output)
            assert 'Files downloaded and zipped successfully' in result.output
            assert custom_output in result.output

            # Check zip file contents
            with zipfile.ZipFile(custom_output, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                assert 'file1.txt' in file_list
                assert 'file2.txt' in file_list
                assert '.gitignore' in file_list
                assert 'ignored_file.txt' not in file_list
    finally:
        # Clean up
        shutil.rmtree(repo_path)
        if os.path.exists(custom_output):
            os.remove(custom_output)

def test_main_invalid_repo():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        result = runner.invoke(main, [temp_dir])
        assert result.exit_code == 1
        assert 'Error: ' in result.output
        assert 'is not a valid Git repository' in result.output

def clean_downloads_dir():
    downloads_dir = get_default_downloads_dir()
    for file in os.listdir(downloads_dir):
        if file.endswith('_files.zip'):
            os.remove(os.path.join(downloads_dir, file))

def test_main_default_behavior():
    runner = CliRunner()
    repo_path = create_test_repo()
    try:
        clean_downloads_dir()
        with runner.isolated_filesystem():
            result = runner.invoke(main, [repo_path])
            assert result.exit_code == 0
            assert 'Files downloaded and zipped successfully' in result.output
            
            # Check if zip file was created in downloads directory
            downloads_dir = get_default_downloads_dir()
            zip_files = [f for f in os.listdir(downloads_dir) if f.endswith('_files.zip')]
            assert len(zip_files) == 1
            
            # Check zip file contents
            zip_path = os.path.join(downloads_dir, zip_files[0])
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                assert 'file1.txt' in file_list
                assert 'file2.txt' in file_list
                assert '.gitignore' in file_list
                assert 'ignored_file.txt' not in file_list
    finally:
        # Clean up
        shutil.rmtree(repo_path)
        clean_downloads_dir()

def test_main_ignore_gitignore():
    runner = CliRunner()
    repo_path = create_test_repo()
    try:
        clean_downloads_dir()
        with runner.isolated_filesystem():
            result = runner.invoke(main, [repo_path, '--ignore-gitignore'])
            assert result.exit_code == 0
            
            # Check zip file contents
            downloads_dir = get_default_downloads_dir()
            zip_files = [f for f in os.listdir(downloads_dir) if f.endswith('_files.zip')]
            zip_path = os.path.join(downloads_dir, zip_files[0])
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                assert 'ignored_file.txt' in file_list
    finally:
        # Clean up
        shutil.rmtree(repo_path)
        clean_downloads_dir()
