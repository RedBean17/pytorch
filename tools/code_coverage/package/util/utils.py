import os
import shutil
import sys
import time
from typing import Any, NoReturn, Optional

from .setting import (
    CompilerType,
    LOG_DIR,
    PROFILE_DIR,
    TestList,
    TestPlatform,
    TestType,
)


def convert_time(seconds: float) -> str:
    seconds = int(round(seconds))
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


def print_time(message: str, start_time: float, summary_time: bool = False) -> None:
    with open(os.path.join(LOG_DIR, "log.txt"), "a+") as log_file:
        end_time = time.time()
        print(message, convert_time(end_time - start_time), file=log_file)
        if summary_time:
            print("\n", file=log_file)


def print_log(*args: Any) -> None:
    with open(os.path.join(LOG_DIR, "log.txt"), "a+") as log_file:
        print(f"[LOG] {' '.join(args)}", file=log_file)


def print_error(*args: Any) -> None:
    with open(os.path.join(LOG_DIR, "log.txt"), "a+") as log_file:
        print(f"[ERROR] {' '.join(args)}", file=log_file)


def remove_file(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)


def remove_folder(path: str) -> None:
    shutil.rmtree(path)


def create_folder(*paths: Any) -> None:
    for path in paths:
        os.makedirs(path, exist_ok=True)


# clean up all the files generated by coverage tool
def clean_up() -> None:
    # remove profile folder
    remove_folder(PROFILE_DIR)
    sys.exit("Clean Up Successfully!")


def convert_to_relative_path(whole_path: str, base_path: str) -> str:
    # ("profile/raw", "profile") -> "raw"
    if base_path not in whole_path:
        raise RuntimeError(base_path + " is not in " + whole_path)
    return whole_path[len(base_path) + 1 :]


def replace_extension(filename: str, ext: str) -> str:
    return filename[: filename.rfind(".")] + ext


# a file is related if it's in one of the test_list folder
def related_to_test_list(file_name: str, test_list: TestList) -> bool:
    for test in test_list:
        if test.name in file_name:
            return True
    return False


def get_raw_profiles_folder() -> str:
    return os.environ.get("RAW_PROFILES_FOLDER", os.path.join(PROFILE_DIR, "raw"))


def detect_compiler_type(platform: TestPlatform) -> CompilerType:
    if platform == TestPlatform.OSS:
        from package.oss.utils import (  # type: ignore[assignment, import, misc]
            detect_compiler_type,
        )

        cov_type = detect_compiler_type()  # type: ignore[call-arg]
    else:
        from caffe2.fb.code_coverage.tool.package.fbcode.utils import (  # type: ignore[import]
            detect_compiler_type,
        )

        cov_type = detect_compiler_type()

    check_compiler_type(cov_type)
    return cov_type  # type: ignore[no-any-return]


def get_test_name_from_whole_path(path: str) -> str:
    # code_coverage_tool/profile/merged/haha.merged -> haha
    start = path.rfind("/")
    end = path.rfind(".")
    assert start >= 0 and end >= 0
    return path[start + 1 : end]


def check_compiler_type(cov_type: Optional[CompilerType]) -> None:
    if cov_type is not None and cov_type in [CompilerType.GCC, CompilerType.CLANG]:
        return
    raise Exception(
        f"Can't parse compiler type: {cov_type}.",
        " Please set environment variable COMPILER_TYPE as CLANG or GCC",
    )


def check_platform_type(platform_type: TestPlatform) -> None:
    if platform_type in [TestPlatform.OSS, TestPlatform.FBCODE]:
        return
    raise Exception(
        f"Can't parse platform type: {platform_type}.",
        " Please set environment variable COMPILER_TYPE as OSS or FBCODE",
    )


def check_test_type(test_type: str, target: str) -> None:
    if test_type in [TestType.CPP.value, TestType.PY.value]:
        return
    raise Exception(
        f"Can't parse test type: {test_type}.",
        f" Please check the type of buck target: {target}",
    )


def raise_no_test_found_exception(
    cpp_binary_folder: str, python_binary_folder: str
) -> NoReturn:
    raise RuntimeError(
        f"No cpp and python tests found in folder **{cpp_binary_folder} and **{python_binary_folder}**"
    )
