from pathlib import Path
import re
from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
board_config = env.BoardConfig()
FRAMEWORK_DIR = Path(env.PioPlatform().get_package_dir("framework-easypdk-hal"))
HAL_DIR = FRAMEWORK_DIR / "HAL"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Match #include "something"
INCLUDE_REGEX = re.compile(r'#\s*include\s*"([^"]+)"')

# Remove C-style block comments and C++-style line comments
COMMENT_REGEX = re.compile(r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE)

def strip_comments(text: str) -> str:
    """Return the text with C/C++ comments removed."""
    return re.sub(COMMENT_REGEX, '', text)

def scan_includes(path: Path) -> set[str]:
    """Return a set of all quoted includes found in a source/header file,
    ignoring commented-out includes."""
    try:
        text = path.read_text(errors="ignore")
    except Exception:
        return set()
    uncommented = strip_comments(text)
    found = set(INCLUDE_REGEX.findall(uncommented))
    return found


def collect_files(directory: Path, patterns=("*.c", "*.h")) -> list[Path]:
    """Return a list of files in a directory matching the given patterns."""
    files = []
    for p in patterns:
        files.extend(directory.glob(p))
    return files


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def get_core_files() -> list[str]:
    # Project directories
    config = env.GetProjectConfig()
    PROJECT_INCLUDE_DIR = Path(config.get("platformio", "include_dir"))
    PROJECT_SRC_DIR = Path(config.get("platformio", "src_dir"))

    # Gather project files
    src_files = collect_files(PROJECT_SRC_DIR)
    inc_files = collect_files(PROJECT_INCLUDE_DIR)

    print("\n- Source files (src folder):")
    print([f.name for f in src_files])

    print("- Include files (include folder):")
    print([f.name for f in inc_files])

    # Scan for all includes used in project source files
    used_includes = set()
    for f in src_files + inc_files:
        used_includes |= scan_includes(f)

    print("\n- Files included in source files:")
    print(sorted(used_includes))

    # Determine which HAL source files are required
    hal_sources = {f for f in HAL_DIR.glob("*.c")}
    matched_sources = []

    for c_file in hal_sources:
        h_name = c_file.with_suffix(".h").name
        if h_name in used_includes:
            matched_sources.append(c_file.name)

    # Enforce required file
    if "hal_util.c" not in matched_sources:
        matched_sources.append("hal_util.c")

    print("- HAL source files to compile:")
    print(matched_sources)
    print()

    return matched_sources


# ---------------------------------------------------------------------------
# PlatformIO integration
# ---------------------------------------------------------------------------

linkflags = [
    "-Wl-b IVECT = 0x0020",
    "-Wl-b PIREG = 0x02",
    "-Wl-b TMPSEG = 0x04",
    "--data-loc 0x08",
]
code_loc = board_config.get("build", {}).get("code_loc")
if code_loc:
    print("Code will be placed at:", code_loc)
    linkflags.append("--code-loc %s" % code_loc)

env.Append(
    CFLAGS=[
        #"--no-c-code-in-asm",
        #"--stack-auto",
        #"--opt-code-size"
        #"--opt-code-speed"
        #"--nogcse"
    ],
    CPPDEFINES=[],
    LINKFLAGS=linkflags,
    CPPPATH=[str(HAL_DIR)]
)

env.BuildSources(
    str(Path("$BUILD_DIR") / "HAL"),
    str(HAL_DIR),
    src_filter=["-<*>"] + [f" +<{f}>" for f in get_core_files()]
)