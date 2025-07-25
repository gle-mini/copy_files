import os
import sys
import pytest
from pathlib import Path
import shutil

# Import the functions to test; adjust module name if your script file is named differently
from src.copy_files import dump_tree, main
import pytest


def write_file(path: Path, content: bytes):
    path.write_bytes(content)


@pytest.fixture(autouse=True)
def isolate_fs(tmp_path, monkeypatch):
    """Run each test in an isolated temporary working directory."""
    monkeypatch.chdir(tmp_path)
    yield


def test_default_output(tmp_path):
    # Create source folder and a sample file
    src = tmp_path / "src"
    src.mkdir()
    file1 = src / "file1.txt"
    write_file(file1, b"hello123")

    # Run dump_tree with default output
    dump_tree(str(src))

    out_file = tmp_path / "output.txt"
    assert out_file.exists(), "Default output file was not created"
    content = out_file.read_text()

    assert "### ./src/file1.txt ###" in content
    assert "hello123" in content


def test_custom_output(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    foo = src / "foo.py"
    write_file(foo, b"print('hi')")

    custom = tmp_path / "myout.txt"
    dump_tree(str(src), str(custom))

    assert custom.exists(), "Custom output file was not created"
    content = custom.read_text()

    assert "### ./src/foo.py ###" in content
    assert "print('hi')" in content


def test_exclude_exact(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    readme = src / "README.md"
    write_file(readme, b"should be excluded")

    dump_tree(str(src))
    content = (tmp_path / "output.txt").read_text()

    assert "README.md" not in content


def test_exclude_glob(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    obj = src / "test.o"
    write_file(obj, b"objbinary")

    dump_tree(str(src))
    content = (tmp_path / "output.txt").read_text()

    assert "test.o" not in content


def test_exclude_dir(tmp_path):
    src = tmp_path / "src"
    build = src / "build"
    build.mkdir(parents=True)
    xfile = build / "x.txt"
    write_file(xfile, b"nested")

    dump_tree(str(src))
    content = (tmp_path / "output.txt").read_text()

    assert "x.txt" not in content


def test_rel_path_prefix(tmp_path):
    # Files under srcs/database should be skipped
    base = tmp_path / "srcs" / "database"
    base.mkdir(parents=True)
    data = base / "data.bin"
    write_file(data, b"binarydata")

    outpath = tmp_path / "out.txt"
    dump_tree(str(tmp_path), str(outpath))
    content = outpath.read_text()

    assert "data.bin" not in content


def test_main_usage_error(monkeypatch, capsys):
    # No args should print usage
    monkeypatch.setattr(sys, 'argv', ['script.py'])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Usage:" in captured.out


def test_main_nonexistent(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['script.py', 'no_such_dir'])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "does not exist" in captured.out
