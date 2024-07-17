from chiklisp_stdlib import STABLE_INCLUDE_DIRECTORY, NIGHTLY_INCLUDE_DIRECTORY


def test_paths():
    assert STABLE_INCLUDE_DIRECTORY.parts[-2:] == (
        "chiklisp_stdlib",
        "stable",
    )

    assert NIGHTLY_INCLUDE_DIRECTORY.parts[-2:] == (
        "chiklisp_stdlib",
        "nightly",
    )
