from pathlib import Path
from subprocess import run


def project_sloc():
    """Returns the source-lines-of-code from the project"""

    result = run(
        ["pygount", str(Path("src") / "jugmt"), str(Path("tests")), "--format=summary"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"failed running 'pygount': {result.stderr}"

    for line in result.stdout.splitlines():
        if "Sum" not in line:
            continue

        return int(
            [
                col.strip()
                for col in line.replace("│", "|").split("|")[2:]
                if col.strip()
            ][2]
        )

    return 0


def test_sloc():
    """Test that the jugmt source do not grow too large"""

    sloc = project_sloc()
    print(f"sloc({sloc}) ", end="")

    assert sloc > 10, "Invalid sloc-count"

    assert project_sloc() < 500, "Too Much code; please simplfy..."
