#!/usr/bin/env bash
# Isolated CPU-only double-precision build, same official release as MD runtime.
set -euo pipefail
ROOT=$(cd "$1" && pwd)
PKG="$ROOT/software/gromacs_double"
FFTW=/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda
mkdir -p "$PKG"
cd "$PKG"
curl --fail --location --retry 3 --connect-timeout 20 --max-time 600 \
  https://ftp.gromacs.org/gromacs/gromacs-2025.4.tar.gz -o gromacs-2025.4.tar.gz
printf '733448146f1f0555c9fd8d7a5d14ac7b  gromacs-2025.4.tar.gz\n' | md5sum -c - > source_check.txt
sha256sum gromacs-2025.4.tar.gz > source.sha256
tar -xzf gromacs-2025.4.tar.gz
cmake -S gromacs-2025.4 -B build -DGMX_DOUBLE=ON -DGMX_GPU=OFF \
  -DGMX_MPI=OFF -DGMX_THREAD_MPI=ON -DGMX_SIMD=AVX2_256 \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$PKG/install" \
  -DFFTWF_LIBRARY="$FFTW/lib/libfftw3.so" -DFFTWF_INCLUDE_DIR="$FFTW/include" \
  -DFFTW_LIBRARY="$FFTW/lib/libfftw3.so" -DFFTW_INCLUDE_DIR="$FFTW/include" \
  -DGMX_FFT_LIBRARY=fftw3 -DGMX_BUILD_UNITTESTS=ON -DGMXAPI=OFF \
  -DGMX_INSTALL_NBLIB_API=OFF > configure.log 2>&1
cmake --build build -j 16 > build.log 2>&1
cmake --install build > install.log 2>&1
"$PKG/install/bin/gmx_d" --version > runtime_version.txt 2>&1
printf 'Build complete; numerical checks still required before use.\n' > build_complete.txt
