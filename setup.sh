#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

python3 -m pip install --user func_timeout

mkdir -p case
mkdir -p ingred
mkdir -p ingredSeed
mkdir -p llvm-testsuite

g++ -std=c++17 mutator.cpp -o mutator -I ./include
g++ -std=c++17 mutator_CU.cpp -o mutator_CU -I ./include
g++ -std=c++17 mutator_REU.cpp -o mutator_REU -I ./include

# If llvm-testsuite is empty but old SeedPool exists, populate it.
if [ -d SeedPool ] && [ -z "$(find llvm-testsuite -type f -name '*.wasm' -print -quit)" ]; then
  cp SeedPool/*.wasm llvm-testsuite/ 2>/dev/null || true
fi

# If ingredSeed is empty, populate it from llvm-testsuite.
if [ -z "$(find ingredSeed -type f -name '*.wasm' -print -quit)" ]; then
  cp llvm-testsuite/*.wasm ingredSeed/ 2>/dev/null || true
fi

echo
echo "Setup complete."
echo "Counts:"
echo "  llvm-testsuite wasm files: $(find llvm-testsuite -type f -name '*.wasm' | wc -l)"
echo "  ingredSeed wasm files:     $(find ingredSeed -type f -name '*.wasm' | wc -l)"
echo
echo "Extraction:"
echo "  PATH=\"$PWD/wabt:\$PATH\" python3 extract.py ./ingredSeed ./ingred"
echo
echo "Generation:"
echo "  PATH=\"$PWD/wabt:\$PATH\" python3 test.py normal ./llvm-testsuite ./ingred ./case"
