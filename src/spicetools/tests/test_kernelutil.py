import os

from spicetools.kernelutil import make_meta


def test_make_meta():
    # Test with a single kernel path
    make_meta("kernel1.bsp", output="test_meta.txt")
    with open("test_meta.txt", "r") as f:
        contents = f.read()
    assert "kernel1.bsp" in contents
    assert "KERNELS" in contents
    assert "PATH_VALUES" in contents
    assert "PATH_SYMBOLS" in contents

    # Test with multiple kernel paths
    make_meta("kernel1.bsp", "kernel2.bsp", output="test_meta_multiple.txt")
    with open("test_meta_multiple.txt", "r") as f:
        contents = f.read()
    assert "kernel1.bsp" in contents
    assert "kernel2.bsp" in contents

    # Clean up
    os.remove("test_meta.txt")
    os.remove("test_meta_multiple.txt")  # Clean up the test files
    # Ensure the files are removed
    assert not os.path.exists("test_meta.txt")
    assert not os.path.exists("test_meta_multiple.txt")  # Ensure the files are removed
