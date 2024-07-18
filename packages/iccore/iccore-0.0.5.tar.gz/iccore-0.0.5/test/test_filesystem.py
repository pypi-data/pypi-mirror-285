import os
import shutil
from pathlib import Path
from iccore import filesystem

def test_archives():

    work_dir = Path(os.getcwd()) / "test_archives"
    os.makedirs(work_dir)
    
    test_dir = work_dir / "test_archive_dir"
    os.makedirs(test_dir)

    with open(test_dir / "test_file.dat", 'w') as f:
        f.write("test file content")

    archive_name = "test_archive"
    filesystem.make_archive(work_dir / archive_name,
                            "zip",
                            test_dir)

    filesystem.unpack_archive(work_dir / f"{archive_name}.zip", work_dir / "extracted")
    
    shutil.rmtree(work_dir)
    
