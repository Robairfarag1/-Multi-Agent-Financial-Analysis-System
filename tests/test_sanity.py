import os

def test_readme_exists():
    assert os.path.exists("README.md")

def test_repo_layout():
    for p in ["src", "src/data", "notebooks", "data_cache"]:
        assert os.path.isdir(p)
