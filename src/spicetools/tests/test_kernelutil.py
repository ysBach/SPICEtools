from spicetools.kernelutil import make_meta


def test_make_meta(tmp_path):
    # Test with a single kernel path
    make_meta("kernel1.bsp", output=tmp_path / "test_meta.txt")
    with open(tmp_path / "test_meta.txt", "r") as f:
        contents = f.read()

    assert "kernel1.bsp" in contents
    assert "KERNELS" in contents
    assert "PATH_VALUES" in contents
    assert "PATH_SYMBOLS" in contents

    # Test with multiple kernel paths
    make_meta("kernel1.bsp", "kernel2.bsp", output=tmp_path / "test_meta_multiple.txt")
    with open(tmp_path / "test_meta_multiple.txt", "r") as f:
        contents = f.read()

    assert "kernel1.bsp" in contents
    assert "kernel2.bsp" in contents

    # Clean up is handled by pytest's tmp_path fixture
    # No need to manually remove files
