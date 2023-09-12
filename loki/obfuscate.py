#!/usr/bin/python3

"""
Build n random instances
"""

from argparse import ArgumentParser, Namespace
from datetime import datetime
from functools import partial
from pathlib import Path
from time import time
from typing import Dict, List, Optional
from multiprocessing import Pool
import random
import subprocess
import logging
import os
import shutil
import sys

NUM_CPUS: Optional[int] = os.cpu_count()
assert NUM_CPUS is not None, "os.cpu_count() returned None"

################################################################

# Paths
TESTCASE_REPO = Path("./testcases").resolve() # from where to draw replacement code
TRANSLATOR_DIR: Path = Path("./translator").resolve()
LLVM_INSTALL: Path = Path("./translator/llvm").resolve()
OBFUSCATOR_DIR: Path = Path("./obfuscator").resolve()
GIT_DIR: Path = Path("..").resolve()

# Default values
FAILED_INSTANCE_IS_CRITICAL = False
NUM_INSTANCES: int = NUM_CPUS
BUILD_TIMEOUT = 10800 # 3 hours

RUST_CONFIG = """pub const CONFIG: Config = Config {
    rewrite_mba: true,
    superoptimization: true,
    schedule_non_deterministic: true,
    handler_duplication: false,
    num_alus: 511,
    min_semantics_per_alu: 3,
    max_semantics_per_alu: 5,
    min_superhandler_depth: 3,
    max_superhandler_depth: 12,
    num_reserved_alu_handler: 2,
    equivalence_classes_path: "./mba/",
    verification_iterations: 100,
    debug_output: false,
    eval_dir: "THIS/IS/A/PLACEHOLDER",
    num_instances: 80,
};"""

################################

logger = logging.getLogger("obfuscate-script")
MAX_PARALLEL_PROCESSES = NUM_CPUS

ORIG_BIN_NAME = "orig_exe"
OBF_BIN_NAME = "obf_exe"
OBF_LIB_NAME = "libobf.so"

################################################################

def setup_logging(target_dir: Path, log_level: int = logging.DEBUG) -> None:
    """Setup logger"""
    # Create handlers
    c_handler = logging.StreamHandler()  # pylint: disable=invalid-name
    f_handler = logging.FileHandler("obfuscate.log", "w+")  # pylint: disable=invalid-name
    fl_handler = logging.FileHandler(target_dir / "setup_eval.log", "w+")
    c_handler.setLevel(log_level)
    f_handler.setLevel(log_level)
    fl_handler.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    c_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    f_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    fl_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    logger.addHandler(fl_handler)

### Generate random inputs ###

def identify_pointer_args() -> List[bool]:
    """Identify which arguments of target_function are pointers"""
    with open("./src/input_program.cpp", "r", encoding="utf-8") as input_program:
        content = [l for l in input_program.readlines() if 'extern "C"' in l and "target_function(" in l]
    assert len(content) == 1, f"Found {len(content)} definitions of target_function in ./src/input_program.cpp"
    arg_str = content[0].split("target_function(")[1]
    return [bool("*" in arg) for arg in arg_str.split(",")]


def create_random_string_testcase() -> str:
    """Create string of random length"""
    choice: int = random.getrandbits(64) % 2
    if choice == 0:
        return "A" * random.randint(16, 128 + 1)
    if choice == 1:
        return "B" * random.choice([16, 32, 64])
    raise ValueError(f"Unexpected case: choice is {choice} but should be 0 to 1 (included)")


def create_random_testcase() -> str:
    """Create one random testcase"""
    choice: int = random.getrandbits(64) % 5
    if choice == 0:
        return str(random.getrandbits(8))
    if choice == 1:
        return str(random.getrandbits(16))
    if choice == 2:
        return str(random.getrandbits(32))
    if choice == 3:
        return str(random.getrandbits(64))
    if choice == 4:
        special_testcases = [
            0x0, 0x1, 0x2, 0x80, 0xff, 0x8000, 0xffff, 0x8000_0000,
            0xffff_ffff, 0x8000_0000_0000_0000, 0xffff_ffff_ffff_ffff
        ]
        return str(random.choice(special_testcases))
    raise ValueError(f"Unexpected case: choice is {choice} but should be 0 to 4 (included)")

### End generate random inputs ###

### Initial stuff that is run one time ###

def get_base_dir() -> Path:
    """
        Extract root directory of obfuscation projects /* UGLY */
    """
    base_dir = Path(__file__).resolve().parent
    os.chdir(base_dir)
    assert_is_dir(base_dir / "translator")
    assert_is_dir(base_dir / "obfuscator")
    assert_is_dir(base_dir / "testcases")
    return base_dir


def build_rust(build_timeout: int) -> bool:
    """Ensure the obfuscator vm_alu Rust component is built"""
    output = ""
    assert_is_dir(Path("obfuscator"))
    cwd = os.getcwd()
    os.chdir("obfuscator")
    cmd: List[str] = ["cargo", "build", "--release", "--bin", "vm_alu"]
    logger.debug(f"Building Rust release binary: {' '.join(cmd)}")
    try:
        process = subprocess.run(
            cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=build_timeout
        )
        output = prettify_str(process.stderr.decode())
    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout for: {' '.join(cmd)}")
        os.chdir(cwd)
        return False
    except subprocess.CalledProcessError as err:
        logger.warning(f"Process errored out with {err} for {' '.join(cmd)}")
        os.chdir(cwd)
        return False
    os.chdir(cwd)
    if "Finished release" not in output:
        logger.error(f"Rust build failed:\n{output}")
        return False
    return True


def initial_build(build_timeout: int) -> str:
    """Ensure the translator C++ component is built"""
    assert Path("./build.sh").exists() and Path("./build.sh").is_file(), "./build.sh not found :("
    cmd: List[str] = ["./build.sh"]
    logger.debug("Executing ./build.sh")
    try:
        process = subprocess.run(
            cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=build_timeout
        )
        return prettify_str(process.stderr.decode())
    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout for: {' '.join(cmd)}")
    except subprocess.CalledProcessError as err:
        logger.warning(f"Process errored out with {err} for {' '.join(cmd)}")
    sys.exit(1)


def setup_builds(base_dir: Path, timeout: int) -> None:
    """Run initial builds such as ./build.sh or cargo run --release"""
    os.chdir("translator")
    initial_out = initial_build(timeout)
    if initial_out.strip() != "":
        logger.critical(f"./build.sh failed:\n{initial_out}")
        sys.exit(1)
    os.chdir(base_dir)
    logger.debug("Initial build done")

### end initial build methods ###

### Utils ###

def save_original_input(original_input_str: str) -> Path:
    """Save original input_program.cpp"""
    original_input = Path(original_input_str)
    assert original_input.exists() and original_input.is_file(), "./src/input_program.cpp not found :("
    backup = original_input.with_suffix(".cpp.backup")
    original_input.rename(backup)
    assert Path("./src/input_program.cpp.backup").exists() \
            and Path("./src/input_program.cpp.backup").is_file(), "Saving original input failed :("
    return backup


def restore_original_input(backup_original_input: Path) -> None:
    """Restore original input_program.cpp"""
    if backup_original_input.exists() and backup_original_input.is_file():
        backup_original_input.rename(backup_original_input.with_suffix(""))
    assert Path("./src/input_program.cpp").exists() \
            and Path("./src/input_program.cpp").is_file(), "Restoring original input failed :("


def prettify_str(string: str) -> str:
    """Fix newlines and remove terminal colors"""
    string = string.replace("\\x1b[1m\\x1b[31m", "") # failure color
    string = string.replace("\\x1b[1m\\x1b[33m", "") # warning color
    string = string.replace("\\x1b[1m\\x1b[32m", "") # success color
    string = string.replace("\\x1b(B\\x1b[m", "") # white color
    string = string.strip()
    return string


def enumerate_testcases(allowlist: List[str], denylist: List[str]) -> List[Path]:
    """
    Enumerate all testcases included in allowlist.
    If no allowlisted entry exists, enumerate all entries not on denylist
    """
    testcases = []
    if allowlist:
        testcases = [
            Path(testcase) for testcase in TESTCASE_REPO.glob("**/*.c*") if testcase.name.split(".c")[0] in allowlist
        ]
    else:
        testcases = [
            Path(testcase) for testcase in TESTCASE_REPO.glob("**/*.c*") if testcase.name.split(".c")[0] not in denylist
        ]
    logger.info(f"Found {len(testcases)} testcases")
    return testcases


def assert_is_exec(executable: Path) -> None:
    """Assert file exists and is executable"""
    assert executable.exists() and executable.is_file() \
            and os.access(executable, os.X_OK), f"{executable} does not exist or is not executable"


def assert_is_file(file: Path) -> None:
    """Assert file exists"""
    assert file.exists() and file.is_file(), f"{file} does not exist"


def assert_is_dir(directory: Path) -> None:
    """Assert directory exists"""
    assert directory.exists() and directory.is_dir(), f"{directory} directory does not exist"


def check_bin_dir(eval_dir: Path, shared: bool) -> None:
    """Check whether expected directories exist"""
    bin_path = eval_dir / "bin"
    assert_is_dir(bin_path)
    if not shared:
        assert_is_exec(bin_path / "lift_input")
    else:
        assert_is_file(bin_path / "lift_input")
    assert_is_exec(bin_path / "generate-vm-9.0")
    assert_is_file(bin_path / "template.bc")


def check_workdir_dir(testcase_dir: Path, num_instances: int, shared: bool, ignore: Optional[List[Path]] = None) \
            -> None:
    """Check whether the testcase"""
    assert_is_dir(testcase_dir)
    assert_is_dir(testcase_dir / "src")
    assert_is_file(testcase_dir / "src" / "input_program.cpp")
    assert_is_file(testcase_dir / "src" / "input_program.bc")
    assert_is_file(testcase_dir / "src" / "lifted_input.txt")
    assert_is_file(testcase_dir / "src" / "input_program_opt.bc")
    assert_is_file(testcase_dir / "src" / "input_program_opt.ll")
    assert_is_dir(testcase_dir / "instances")
    for number in range(num_instances):
        instance_dir = testcase_dir / "instances" / f"vm_alu{number:03}"
        assert_is_dir(instance_dir)
        if ignore is None or instance_dir not in ignore:
            if shared:
                assert_is_file(instance_dir / OBF_LIB_NAME)
            else:
                assert_is_exec(instance_dir / OBF_BIN_NAME)
    assert_is_file(testcase_dir / "bin" / ORIG_BIN_NAME)


def run_exe(executable: Path, cmd_arguments: List[str], timeout: int, check: bool = False, silent: bool = False,
            env: Optional[Dict[str, str]] = None) -> Optional[str]:
    """Run an executable file or some script"""
    assert_is_exec(executable)
    cmd: List[str] = [str(executable)]
    if cmd_arguments:
        cmd += cmd_arguments
    if not silent:
        logger.debug(f"Executing {' '.join(cmd)}")
    try:
        if env is not None:
            process = subprocess.run(
                cmd, check=check, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, env=env
            )
        else:
            process = subprocess.run(
                cmd, check=check, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout
            )
        output = prettify_str(process.stdout.decode())
        return output
    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout for: {' '.join(cmd)}")
    except subprocess.CalledProcessError as err:
        logger.warning(f"Process errored out with {err} for {' '.join(cmd)}")
        if err.stdout:
            logger.warning(f"Output: {err.stdout.decode()}")
        sys.exit(1)
    return None


def copy_file(src: Path, dst: Path) -> Path:
    """Copy a file"""
    return Path(shutil.copy2(src, dst))

### end utils ###


def lift_input(eval_dir: Path, input_program: Path, timeout: int) -> bool:
    """Run lift_input binary to lift input"""
    output = run_exe(eval_dir / "bin" / "lift_input", [str(input_program.resolve())], timeout)
    if output is None:
        return False
    error_lines = [l.strip() for l in output.split("\n") if \
        not "Could not translate an instruction:  ret i64 %" in l and \
        not "Could not translate an instruction:  ret i32 %" in l and \
        not "Could not translate an instruction:  ret i8 %" in l and \
        not "Done." in l and \
        not "call void @llvm.lifetime" in l \
        ]
    if error_lines:
        logger.error(f"LIFTER: Lifting failed with:\n {error_lines}")
        return False
    return True


def clangpp_compile(src: Path, dst: Path, args: List[str], timeout: int, silent: bool = False) -> bool:
    """Compile input program to destination
        ./llvm/bin/clang++ [args] [src] -o [dst]
    """
    clangpp_bin = LLVM_INSTALL / "bin" / "clang++"
    clangpp_args = args + [str(src), "-o", str(dst)]
    output = run_exe(clangpp_bin, clangpp_args, timeout, silent=silent)
    if output is None or (output and "error" in output):
        logger.error(f"CLANG++: Compiling original executable failed:\n{output}")
        return False
    return True


def src_to_bitcode(src: Path, timeout: int) -> bool:
    """Emit a source code file as llvm bitcode file"""
    # logger.debug(f"DDEBUG: src_to_bitcode: {src}")
    clang_bin = LLVM_INSTALL / "bin" / "clang"
    clang_args = ["-c", "-emit-llvm", "--std=c++14", "-O3", "-Xclang", "-disable-llvm-passes",
                  str(src), "-o", str(src.with_suffix(".bc"))]
    output = run_exe(clang_bin, clang_args, timeout)
    if output is None or (output and "error" in output):
        logger.error(
            f"Failed to convert {src} to {src.with_suffix('.bc')} using {clang_bin} {' '.join(clang_args)} " \
            f"- unexpected output:\n{output}"
        )
        return False
    return True


def llvm_dis(target: Path, timeout: int) -> bool:
    """Run llvm-dis on target"""
    llvm_dis_bin = LLVM_INSTALL / "bin" / "llvm-dis"
    llvm_dis_args = [str(target)]
    output = run_exe(llvm_dis_bin, llvm_dis_args, timeout)
    if output is None or output != "":
        logger.error(f"LLVM-DIS: Failed to make {target} human readable")
        return False
    return True


def prepare_testcase_workdir(testcase_path: Path, workdir: Path, timeout: int) -> None:
    """Create testcase workdir and compile original binary + bitcode"""
    # logger.debug(f"DDEBUG: {testcase_path}")
    workdir.mkdir()
    src_subdir = workdir / "src"
    src_subdir.mkdir()
    dst_input_program = src_subdir / "input_program.cpp"
    copy_file(testcase_path, dst_input_program)
    if not src_to_bitcode(dst_input_program, timeout):
        logger.error("Failed to compile source program to bitcode")
        sys.exit(1)
    if not lift_input(workdir.parent.parent, dst_input_program.parent, timeout):
        logger.error("Failed to lift source program's bitcode to TIL")
        sys.exit(1)
    # move file to workdir
    input_program_opt = src_subdir / "input_program_opt.bc"
    llvm_dis(input_program_opt, timeout)
    (workdir / "bin").mkdir()
    if not clangpp_compile(input_program_opt, workdir / "bin" / ORIG_BIN_NAME, ["-O3"], timeout):
        logger.error(f"Failed to compile original executable for {workdir}")
        sys.exit(1)


def prepare_eval_bin_subdir(eval_bin_dir: Path) -> None:
    """Copy binaries (lift_input, generate-vm-9.0) to evaluation/bin directory"""
    eval_bin_dir.mkdir()
    orig_bin_dir = TRANSLATOR_DIR / "bin"
    copy_file(orig_bin_dir / "lift_input", eval_bin_dir / "lift_input")
    copy_file(orig_bin_dir / "generate-vm-9.0", eval_bin_dir / "generate-vm-9.0")
    copy_file(orig_bin_dir / "template.bc", eval_bin_dir / "template.bc")
    logger.debug(f"Copied lift_input, generate-vm-9.0, and template.bc to {eval_bin_dir}")


def adapt_rust_config(modified_entries: List[str], silent: bool = False) -> bool:
    """Adapt the eval dir path set in the vm_alu config, then recompile the project"""
    config_path = OBFUSCATOR_DIR / "vm_alu" / "src" / "config.rs"
    logger.debug(f"Using Rust config at {config_path}")
    with open(config_path, "r", encoding="utf-8") as config_file:
        config = [l for l in config_file.read().split("\n")]
    ctr_modifications = 0
    for (i, line) in enumerate(config):
        for new_entry in modified_entries:
            if new_entry.split(": ")[0] == line.split(": ")[0]:
                if new_entry != line:
                    config[i] = new_entry
                    if not silent:
                        logger.debug(f"Rust config entry modified to: '{config[i]}'")
                ctr_modifications += 1
    # write back config to disk
    with open(config_path, "w", encoding="utf-8") as config_file:
        config_file.write("\n".join(config))
    if ctr_modifications != len(modified_entries):
        logger.error(
            f"Modified only {ctr_modifications} / {len(modified_entries)} - planned modifications: {modified_entries}"
        )
        return False
    return True


def execute_vm_alu(eval_workdir: Path, timeout: int, max_processes: int) -> None:
    """Create instances dir, fix rust config and run vm_alu binary"""
    if not adapt_rust_config([f"    eval_dir: \"{str(eval_workdir.resolve())}\","]) or not build_rust(timeout):
        logger.error("Failed to compile vm_alu for adapted config")
        sys.exit(1)
    vm_alu_bin = eval_workdir / "bin" / "vm_alu"
    copy_file(OBFUSCATOR_DIR / "target" / "release" / "vm_alu", vm_alu_bin)
    env = None
    num_cpu = os.cpu_count()
    if num_cpu is not None and max_processes < num_cpu:
        logger.debug(f"Using RAYON_NUM_THREADS={max_processes} to limit maximum number of cores used")
        env = {"RAYON_NUM_THREADS":str(max_processes)}
    output = run_exe(vm_alu_bin.resolve(), [], timeout, check=True, env=env)
    if output is None or output != "":
        logger.error(f"Executing {vm_alu_bin} returned '{output}' (should be '')")
        sys.exit(1)


def delete_alu_folder(instance_dir: Path) -> None:
    """Delete 'alu_files' folder. Should be called once generate_vm used ALU files to build template"""
    shutil.rmtree(instance_dir / "alus")


def generate_vm(eval_workdir: Path, debug: bool, timeout: int, instance_dir: Path) -> bool:
    """Run generate-vm-9.0 to merge Rust output with template.bc"""
    eval_dir = eval_workdir.parent.parent
    output = run_exe((eval_dir / "bin" / "generate-vm-9.0").resolve(),
                     [str(eval_dir / "bin" / "template.bc"), str(instance_dir)],
                     timeout=timeout,
                     silent=True)
    if output is None or output != "":
        logger.error(f"generate-vm-9.0 failed with ouptut: '{output}' (should be '')")
        return False
    if not debug:
        delete_alu_folder(instance_dir)
    return True


def compile_obfuscated(debug: bool, timeout: int, shared: bool, instance: Path) -> Optional[Path]:
    """Compile obfuscated binary from bitcode"""
    if shared:
        if not clangpp_compile((instance / "obf.bc").resolve(),
                               instance / OBF_LIB_NAME,
                               ["-O3", "-fPIC", "-shared"],
                               timeout=timeout,
                               silent=True):
            logger.error(f"Failed to compile obfuscated shared object for {instance}")
            return instance
    else:
        if not clangpp_compile((instance / "obf.bc").resolve(),
                               instance / OBF_BIN_NAME,
                               ["-O3"],
                               timeout=timeout,
                               silent=True):
            logger.error(f"Failed to compile obfuscated program for {instance}")
            return instance
    if not debug:
        os.remove(instance / "obf.bc")
    return None


def generate_obfuscated_vm(eval_workdir: Path, debug: bool, timeout: int, shared: bool, max_processes: int) \
            -> List[Path]:
    """For each instance, create obfuscated binary"""
    instances = list((eval_workdir / "instances").glob("vm_alu*"))
    logger.debug(
        f"Generating bitcodes from template.bc and bytecode for {len(instances)} instances " \
        f"on up to {max_processes} processes.."
    )
    with Pool(max_processes) as pool:
        generate_vm_func = partial(generate_vm, eval_workdir, debug, timeout)
        successful_generations = pool.map(generate_vm_func, instances)
    if not all(successful_generations):
        logger.critical("VM generation failed in at least one worker")
        sys.exit(1)
    target = "binaries" if not shared else "shared objects"
    logger.debug(
        f"Compiling obfuscated {target} for each instance for {len(instances)} instances " \
        f"on up to {max_processes} processes.."
    )
    with Pool(max_processes) as pool:
        compile_obfuscated_func = partial(compile_obfuscated, debug, timeout, shared)
        instance_paths = pool.map(compile_obfuscated_func, instances)
    failed_instances = [i for i in instance_paths if i is not None]
    if failed_instances:
        logger.error(f"Compiling obfuscated {target} failed in {len(failed_instances)} workers")
        # check if we should continue or abort when there is a broken instance
        if FAILED_INSTANCE_IS_CRITICAL:
            sys.exit(1)
    return failed_instances


def prepare_eval_dir(eval_dir_path: Path, shared: bool) -> Path:
    """Create and prepare evaluation directory"""
    prepare_eval_bin_subdir(eval_dir_path / "bin")
    check_bin_dir(eval_dir_path, shared)
    workdir_path = eval_dir_path / "workdirs"
    workdir_path.mkdir()
    return workdir_path


def get_git_info(path: Path) -> str:
    """Retrieve output of `git log -n1` for path"""
    process_a = subprocess.run(
        f"git --git-dir={path / '.git'} branch | grep '^*'", check=False, shell=True, stdout=subprocess.PIPE
    )
    branch = process_a.stdout.decode().strip().lstrip("*").strip()
    process_b = subprocess.run(
        ["git", f"--git-dir={path / '.git'}", "log", "-n1", "--oneline"], check=False, stdout=subprocess.PIPE
    )
    commit = process_b.stdout.decode().strip()
    return "Branch: " + branch + "\n" + "Commit: " + commit


def get_git_submodule_status(path: Path) -> str:
    """Retrieve output of `git submodule status` for path"""
    cmd = f"cd {path.as_posix()} > /dev/null && git submodule status && cd - > /dev/null"
    process = subprocess.run(cmd, shell=True, check=False, stdout=subprocess.PIPE)
    return process.stdout.decode().strip().replace("\n ", "\n")


def rust_config_to_str(path: Path) -> str:
    """Parse rust config and return relevant fields as str"""
    with open(path, "r", encoding="utf-8") as rust_config_file:
        config = rust_config_file.read()
    return config.split("pub const CONFIG: Config = Config {\n", 1)[1].split("};", 1)[0]


def main(path: Path, args: Namespace) -> None:
    """
        1. Check if directory structure is as expected and binaries are available
        2. Create workdirs for the testcases
        3. Call Rust code to populate the workdirs with N obfuscated binaries
    """
    base_dir = get_base_dir()
    logger.info(f"Path for evaluation: {path}")
    logger.info(f"Base directory: {base_dir}")
    logger.info(f"Maximum number of cores: {args.max_processes}")
    logger.info(f"Number of instances: {args.num_instances}")
    logger.info(f"Timeout: {args.timeout}")
    logger.info(f"#Verification iterations: {args.verification_iterations}")
    logger.info("Rust config: \n\t" + "\n\t".join([l for l in RUST_CONFIG.split("\n") if l.startswith("    ")])) # pylint: disable=logging-not-lazy
    adapt_rust_config([l for l in RUST_CONFIG.split("\n") if l.startswith("    ") or l.startswith("\t")], silent=True)
    adapt_rust_config([f"    equivalence_classes_path: \"{OBFUSCATOR_DIR / 'mba'}/\","])
    adapt_rust_config([f"    num_instances: {args.num_instances},"]) # overwrite NUM_INSTANCES according to cmd
    adapt_rust_config([f"    verification_iterations: {args.verification_iterations},"])
    if args.nomba:
        adapt_rust_config(["    rewrite_mba: false,"])
    if args.nosuperopt:
        adapt_rust_config(["    superoptimization: false,"])
    if args.deterministic:
        adapt_rust_config(["    schedule_non_deterministic: false,"])
    with open(path / "documentation.txt", "a", encoding="utf-8") as docu:
        docu.write(f"Time: {str(datetime.now())}\n")
        docu.write("Loki:\n\t" + "\n\t".join(get_git_info(GIT_DIR).split("\n")) + "\n")
        rust_config_str = rust_config_to_str(OBFUSCATOR_DIR / "vm_alu" / "src" / "config.rs")
        docu.write("Rust config:\n\t" + "\n\t".join(rust_config_str.split("\n")) + "\n")
    timestamp_start = time()
    setup_builds(base_dir, args.timeout)
    workdir_path = prepare_eval_dir(path, args.shared)

    testcases: List[Path] = enumerate_testcases(args.allow, args.deny)

    for (i, testcase) in enumerate(testcases[::-1]):
        logger.info(f"Inspecting {testcase.name} ({i+1}/{len(testcases)})")
        testcase_workdir = workdir_path / testcase.stem
        prepare_testcase_workdir(testcase, testcase_workdir, args.timeout)
        execute_vm_alu(testcase_workdir, args.timeout, args.max_processes)
        if not args.no_generate_vm:
            failed_instances = generate_obfuscated_vm(
                testcase_workdir, args.debug, args.timeout, args.shared, args.max_processes
            )
            check_workdir_dir(testcase_workdir, args.num_instances, args.shared, ignore=failed_instances)
        else:
            logger.debug("Skipping creation of obfuscated VMs due to user flag --no-generate-vm")
    logger.info(f"Done in {round(time() - timestamp_start, 2)}s")


if __name__ == "__main__":
    parser = ArgumentParser(description="Run all testcases available and evaluate correctness and overhead") # pylint: disable=invalid-name
    parser.add_argument("path", nargs=1, help="path to evaluation directory")
    parser.add_argument("--allow", action="store", nargs="+", default=[], help="only run these tests")
    parser.add_argument("--deny", action="store", nargs="+", default=[],
                        help="avoid running these tests (ignored if allowlist is specified)")
    parser.add_argument("--timeout", dest="timeout", action="store", type=int, default=BUILD_TIMEOUT,
                        help="timeout for build process via run.sh")
    parser.add_argument("--instances", dest="num_instances", action="store", type=int, default=NUM_INSTANCES,
                        help="Number of obfuscated instances you want to generate (of the same target)")
    parser.add_argument("--debug", dest="debug", action="store_true", default=False,
                        help="Do not delete build artifacts (increased disk usage)")
    parser.add_argument("--log-level", dest="log_level", action="store", type=int, default=1,
                        help="Loglevel (1 = Debug, 2 = Info, 3 = Warning, 4 = Error)")
    parser.add_argument("--verification-rounds", dest="verification_iterations", action="store", type=int, default=1000,
                        help="Number of verification iterations to run")
    parser.add_argument("--max-processes", dest="max_processes", action="store", type=int,
                        default=MAX_PARALLEL_PROCESSES,
                        help="Number of maximal usable processes (defaults to os.cpu_count())")
    parser.add_argument("--no-generate-vm", action="store_true", default=False,
                        help="Do not call generate-vm (needed for experiment 11)")
    parser.add_argument("--shared", action="store_true", default=False,
                        help="Build as a shared object (.so) instead of executable")
    parser.add_argument("--nomba", action="store_true", default=False, help="Do not use MBA (rewrite_mba: false)")
    parser.add_argument("--nosuperopt", action="store_true", default=False,
                        help="Do not use superoperators (superoptimization: false)")
    parser.add_argument("--deterministic", action="store_true", default=False,
                        help="Deterministic handler (schedule_non_deterministic: false)")
    cargs = parser.parse_args() # pylint: disable=invalid-name

    target_path = Path(cargs.path[0]).resolve() # pylint: disable=invalid-name
    if (Path(cargs.path[0])).exists():
        print(f"Path {cargs.path[0]} already exists. Aborting..")
        sys.exit(1)
    target_path.mkdir()
    setup_logging(target_path, cargs.log_level * 10)

    main(target_path, cargs)
