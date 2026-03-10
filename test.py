import os
import sys
import subprocess
import time

Case_For_Seed = 200
CAMPAIGN_START = time.time()

def cmd(commandline):
    status, output = subprocess.getstatusoutput(commandline)
    return status, output

mutate_cmd = "./mutator mutation {} {} {} >> mutation.log"
simple_mutate_cmd = "./mutator simplemutation ./ingredient {} {}"
mutate_CU_cmd = "./mutator_CU mutation {} {} {}"
mutate_REU_cmd = "./mutator_REU mutation {} {} {}"
mutate_RND_cmd = "./mutator_RND mutation {} {} {} >> mutation_RND.log"

GLOBAL_CASE_ID = 0

def make_timestamped_name(tar_dir, file_name):
    global GLOBAL_CASE_ID
    GLOBAL_CASE_ID += 1

    elapsed_seconds = int(time.time() - CAMPAIGN_START)
    stem = file_name[:-5] if file_name.endswith(".wasm") else file_name

    return os.path.join(
        tar_dir,
        f"{GLOBAL_CASE_ID:09d}_{stem}_t{elapsed_seconds}s.wasm"
    )
    
def run_target(new_file):
    sys.stdout.flush()

    completed = subprocess.run(
        [sys.executable, "run.py", new_file],
        check=False,
    )
    sys.stdout.flush()

def fuzz(args):
    file_path, file_name, ingred_dir, tar_dir, mutateCmd = args
    status = cmd("wasm2wat {} -o {}.wat".format(file_path, file_path[:-5]))
    if status[0] != 0:
        print("Bad input: {}".format(file_path))
        return

    global Case_For_Seed
    cmd("wat2wasm {}.wat -o {}".format(file_path[:-5], file_path))

    for i in range(Case_For_Seed):
        new_file = make_timestamped_name(tar_dir, file_name)

        if os.path.exists(new_file):
            print("File {} existing, contine...".format(new_file))
            continue

        print("Generating {}".format(new_file))
        cmd(mutateCmd.format(ingred_dir, file_path, new_file))

        if not os.path.exists(new_file):
            continue

        run_target(new_file)
        sys.stdout.flush()

def fuzz_simple(args):
    file_path, file_name, tar_dir = args
    status = cmd("wasm2wat {} -o {}.wat".format(file_path, file_path[:-5]))
    if status[0] != 0:
        print("Bad input: {}".format(file_path))
        return

    global Case_For_Seed
    cmd("wat2wasm {}.wat -o {}".format(file_path[:-5], file_path))

    for i in range(Case_For_Seed):
        new_file = make_timestamped_name(tar_dir, i, file_name)

        if os.path.exists(new_file):
            print("File {} existing, contine...".format(new_file))
            continue

        print("Generating {}".format(new_file))
        cmd(simple_mutate_cmd.format(file_path, new_file))

        status = cmd("wasm2wat {}".format(new_file))
        if status[0] != 0:
            cmd("rm -f {}".format(new_file))
            continue

        if os.path.exists(new_file):
            run_target(new_file)

        sys.stdout.flush()

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python3 test.py [normal/simple/CU/REU/RND] [seed dir] [ingred dir] [tar dir]")
        exit(0)

    seed_dir = os.path.abspath(sys.argv[2])
    ingred_dir = os.path.abspath(sys.argv[3])
    tar_dir = os.path.abspath(sys.argv[4])

    os.makedirs(tar_dir, exist_ok=True)

    for root, dirs, files in os.walk(seed_dir):
        for file in files:
            if file.endswith(".wasm") and not file.endswith("aot.wasm") and not file.endswith(".debug.wasm"):
                file_path = os.path.abspath(root + "/" + file)
                print("Mutating {}".format(file_path))

                if sys.argv[1] == "simple":
                    fuzz_simple((file_path, file, tar_dir))
                elif sys.argv[1] == "normal":
                    fuzz((file_path, file, ingred_dir, tar_dir, mutate_cmd))
                elif sys.argv[1] == "CU":
                    fuzz((file_path, file, ingred_dir, tar_dir, mutate_CU_cmd))
                elif sys.argv[1] == "REU":
                    fuzz((file_path, file, ingred_dir, tar_dir, mutate_REU_cmd))
