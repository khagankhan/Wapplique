import os
import shlex
import sys
from time import perf_counter

import func_timeout
from func_timeout import func_set_timeout

# Edit only this when you change target.
# Use {} where the wasm file path should go.
webassembly_implementation_cmd = '/users/khan22/wasmtime/target/release/wasmtime run -C cache=no "{}"'

TIME_UNIT = 1000000  # us
TIMEOUT_SECONDS = 10

@func_set_timeout(TIMEOUT_SECONDS)
def run(command):
    return os.system(command + " >/dev/null 2>/dev/null")

def time_count(command):
    try:
        start = perf_counter()
        ret_code = run(command)
        end = perf_counter()
        execution_time = (end - start) * TIME_UNIT
        if ret_code != 0:
            return ret_code, -1
        return ret_code, execution_time
    except func_timeout.exceptions.FunctionTimedOut:
        return 124, -1

def append_result(wasm_file, status, exec_time):
    with open("runtime_outputs.txt", "a") as f:
        f.write("=" * 60 + "\n")
        f.write(f"{wasm_file}\n")
        f.write(f"Return Code: {status}\n")
        f.write(f"Time: {exec_time}\n\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 run.py <wasm-file>")
        sys.exit(1)

    wasm_file = os.path.abspath(sys.argv[1])

    if not os.path.isfile(wasm_file):
        print(f"Input file does not exist: {wasm_file}")
        sys.exit(1)

    if not wasm_file.endswith(".wasm"):
        print(f"Input is not a .wasm file: {wasm_file}")
        sys.exit(1)

    command = webassembly_implementation_cmd.format(wasm_file)
    status, exec_time = time_count(command)
    append_result(wasm_file, status, exec_time)
