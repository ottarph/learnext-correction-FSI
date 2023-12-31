# Based on: 
# https://github.com/sinzlab/pytorch-docker/blob/master/Dockerfile
# and
# https://github.com/JohannesHaubner/ShapeOpt/tree/main/docker

# Dependency versions
ARG PYBIND11_VERSION=2.10.1
ARG PETSC_VERSION=3.18.2
ARG SLEPC_VERSION=3.18.1
ARG UFL_BRANCH="2021.1.0"
#ARG DOLFIN_BRANCH="master" -> replaced by custom
ARG FFC_BRANCH="master"
ARG DIJITSO_BRANCH="master"
ARG FIAT_BRANCH="master"

# disable cache 
ARG CACHEBUST=0123

# Flags to pass to ninja build system.
ARG MAKEFLAGS
# Compiler optimisation flags for SLEPc and PETSc, all languages.
# CMake build type for DOLFIN C++ build. See CMake documentation.
ARG DOLFIN_CMAKE_BUILD_TYPE="RelWithDebInfo"
# Extra CMake C++ compiler flags for DOLFIN C++ build.
ARG DOLFIN_CMAKE_CXX_FLAGS="-O2"

########################################
FROM nvidia/cuda:12.0.0-devel-ubuntu22.04 as fenics-base
#FROM ubuntu:22.04 as fenics-base

# Deal with pesky Python 3 encoding issue
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND noninteractive
ENV MPLLOCALFREETYPE 1

RUN apt-get update && apt-get -y upgrade && apt-get install -y software-properties-common

# Add Python ppa
RUN add-apt-repository ppa:deadsnakes/ppa


# Usage of pip setuptools
ENV DEB_PYTHON_INSTALL_LAYOUT=deb_system

# PETSC vars
ENV PETSC_DIR=/usr/local/petsc
ENV PETSC_ARCH=linux-gnu-real-32
# SLEPC vars
ENV SLEPC_DIR=/usr/local/slepc
# IPOPT vars
ENV IPOPT_PATH=/usr/local/Ipopt

# Arguments that can be overridden by a user building the docker image
# Compiler optimisation flags for SLEPc and PETSc, all languages.
ARG PETSC_SLEPC_OPTFLAGS="-O2"
# Turn on PETSc and SLEPc debugging. "yes" or "no".
ARG PETSC_SLEPC_DEBUGGING="no"
# MPI variant. "mpich" or "openmpi".
ARG MPI="mpich"
ARG PETSC_VERSION
ARG SLEPC_VERSION
ARG PYBIND11_VERSION

# Environment variables
ENV OPENBLAS_NUM_THREADS=1 \
    OPENBLAS_VERBOSE=0
ENV DEB_PYTHON_INSTALL_LAYOUT=deb_system
WORKDIR /tmp

# Install dependencies available via apt-get.
# - First set of packages are required to build and run FEniCS.
# - Second set of packages are recommended and/or required to build
#   documentation or tests.
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get -qq update && \
    apt-get -yq --with-new-pkgs -o Dpkg::Options::="--force-confold" upgrade && \
    apt-get -y install \
    build-essential \
    ca-certificates \
    clang \
    cmake \
    curl \
    g++ \
    git \
    gfortran \
    graphviz \
    libboost-dev \
    libboost-filesystem-dev \
    libboost-iostreams-dev \
    libboost-math-dev \
    libboost-program-options-dev \
    libboost-system-dev \
    libboost-thread-dev \
    libboost-timer-dev \
    libeigen3-dev \
    libhdf5-${MPI}-dev \
    liblapack-dev \
    lib${MPI}-dev \
    libpng-dev \
    libopenblas-dev \
    lsb-release \
    ninja-build \
    pkg-config \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-tk \
    python3-numpy \
    python3-matplotlib \
    python3-scipy \
    unzip \
    wget \
    zip && \
    curl -sL https://deb.nodesource.com/setup_19.x | bash - &&\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN /bin/bash -l -c "pip3 install --upgrade numpy"
RUN /bin/bash -l -c "pip3 install h5py --no-binary=h5py"

# Install Python packages (via pip)
RUN python3 -m pip install --upgrade pip setuptools==58.3.0
RUN python3 -m pip install pytest pkgconfig
RUN python3 -m pip install --no-cache-dir mpi4py

# Install pybind11
RUN python3 -m pip install --no-cache-dir pybind11==${PYBIND11_VERSION} && \
    wget -nc --quiet https://github.com/pybind/pybind11/archive/v${PYBIND11_VERSION}.tar.gz && \
    tar -xf v${PYBIND11_VERSION}.tar.gz && \
    cd pybind11-${PYBIND11_VERSION} && \    
    mkdir build && \
    cd build && \
    cmake -DPYBIND11_TEST=False ../ && \
    make && \
    make install


# Install PETSc with real and complex types
RUN apt-get -qq update && \
    apt-get -y install bison flex && \
    wget -nc --quiet http://ftp.mcs.anl.gov/pub/petsc/release-snapshots/petsc-lite-${PETSC_VERSION}.tar.gz -O petsc-${PETSC_VERSION}.tar.gz && \
    mkdir -p ${PETSC_DIR} && tar -xf petsc-${PETSC_VERSION}.tar.gz -C ${PETSC_DIR} --strip-components 1 && \
    cd ${PETSC_DIR} && \
    # Real, 32-bit int
    python3 ./configure \
    --COPTFLAGS=${PETSC_SLEPC_OPTFLAGS} \
    --CXXOPTFLAGS=${PETSC_SLEPC_OPTFLAGS} \
    --FOPTFLAGS=${PETSC_SLEPC_OPTFLAGS} \
    --with-64-bit-indices=no \
    --with-debugging=${PETSC_SLEPC_DEBUGGING} \
    --with-fortran-bindings=no \
    --with-shared-libraries \
    --download-blacs \
    --download-hypre \
    --download-metis \
    --download-mumps \
    --download-ptscotch \
    --download-scalapack \
    --download-spai \
    --download-suitesparse \
    --download-superlu \
    --download-superlu_dist \
    --with-scalar-type=real && \
    make ${MAKEFLAGS} all && \
    # Install petsc4py
    cd src/binding/petsc4py && \
    python3 -m pip install --no-cache-dir . && \
    # Cleanup
    apt-get -y purge bison flex && \
    apt-get -y autoremove && \
    apt-get clean && \
    rm -rf \
    ${PETSC_DIR}/**/tests/ \
    ${PETSC_DIR}/**/obj/ \
    ${PETSC_DIR}/**/externalpackages/  \
    ${PETSC_DIR}/CTAGS \
    ${PETSC_DIR}/RDict.log \
    ${PETSC_DIR}/TAGS \
    ${PETSC_DIR}/docs/ \
    ${PETSC_DIR}/share/ \
    ${PETSC_DIR}/src/ \
    ${PETSC_DIR}/systems/ && \ 
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install SLEPc
RUN wget -nc --quiet https://slepc.upv.es/download/distrib/slepc-${SLEPC_VERSION}.tar.gz -O slepc-${SLEPC_VERSION}.tar.gz && \
    mkdir -p ${SLEPC_DIR} && tar -xf slepc-${SLEPC_VERSION}.tar.gz -C ${SLEPC_DIR} --strip-components 1 && \
    cd ${SLEPC_DIR} && \
    python3 ./configure && \
    make SLEPC_DIR=${SLEPC_DIR} && \
    # Install slepc4py
    cd src/binding/slepc4py && \
    python3 -m pip install --no-cache-dir . && \
    rm -rf ${SLEPC_DIR}/CTAGS ${SLEPC_DIR}/TAGS ${SLEPC_DIR}/docs ${SLEPC_DIR}/src/ ${SLEPC_DIR}/**/obj/ ${SLEPC_DIR}/**/test/ && \
    rm -rf /tmp/*


FROM fenics-base as fenics-end-user
LABEL description="End user image"

ARG FIAT_BRANCH
ARG FFC_BRANCH
ARG UFL_BRANCH
ARG DOLFIN_BRANCH
ARG DIJITSO_BRANCH
ARG DOLFIN_CMAKE_BUILD_TYPE
ARG DOLFIN_CMAKE_CXX_FLAGS
ARG MAKEFLAGS

WORKDIR /src
ENV PETSC_DIR=/usr/local/petsc
ENV PETSC_ARCH=linux-gnu-real-32
ENV ENV DEB_PYTHON_INSTALL_LAYOUT=deb_system

RUN git clone --branch ${FIAT_BRANCH} --single-branch  https://github.com/FEniCS/fiat.git && \
    git clone --branch ${FFC_BRANCH} --single-branch https://bitbucket.com/fenics-project/ffc.git && \
    git clone --branch ${UFL_BRANCH} --single-branch https://github.com/FEniCS/ufl.git && \
    git clone --single-branch https://JohannesHaubner@bitbucket.org/JohannesHaubner/dolfin_23.git && \
    git clone --branch ${DIJITSO_BRANCH} --single-branch https://bitbucket.com/fenics-project/dijitso.git

RUN cd fiat && python3 -m pip install --no-cache-dir . && \
    cd ../ufl && python3 -m pip install --no-cache-dir . && \
    cd ../dijitso && python3 -m pip install --no-cache-dir . && \
    cd ../ffc && python3 -m pip install --no-cache-dir . && \
    cd ../ && python3 -m pip install --no-cache-dir ipython

RUN cd dolfin_23 && \
    cmake -G Ninja -DCMAKE_BUILD_TYPE=${DOLFIN_CMAKE_BUILD_TYPE} -DCMAKE_CXX_FLAGS=${DOLFIN_CMAKE_CXX_FLAGS} -B build . && \
    ninja ${MAKEFLAGS} install -C build

RUN python3 -m pip install --no-dependencies ./dolfin_23/python

WORKDIR /root
RUN rm -rf /src

FROM fenics-end-user as fenics-plus
LABEL description="Plus image"

# Install pytest
RUN python3 -m pip install pytest

# Install dolfin-adjoint

RUN /bin/bash -l -c "pip3 install --no-cache git+https://github.com/dolfin-adjoint/pyadjoint.git@constant-adjfloat" 
RUN /bin/bash -l -c "pip3 install matplotlib"

# Install IPython
RUN python3 -m pip install IPython

# Install gmsh
RUN python3 -m pip install gmsh
RUN python3 -m pip install meshio
RUN python3 -m pip install pygmsh 

RUN apt-get update
RUN apt-get -y install libglu1 libxcursor-dev libxft2 libxinerama1 libfltk1.3-dev libfreetype6-dev libgl1-mesa-dev libocct-foundation-dev libocct-data-exchange-dev


# disable cache 
ARG CACHEBUST=01236

## Install Ipopt
WORKDIR /usr/local
RUN git clone https://github.com/coin-or/Ipopt.git
RUN git clone https://github.com/coin-or-tools/ThirdParty-Mumps.git
RUN cd ThirdParty-Mumps && ./get.Mumps && ./configure --prefix=/usr/local && make && make install
RUN cd Ipopt && mkdir build && cd build && ../configure --without-hsl --without-asl --with-lapack --with-mumps --prefix=/usr/local && make && make test && make install

ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
ENV PATH=/usr/local/bin:$PATH
ENV PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH


# Install cyipopt
RUN /bin/bash -l -c "pip3 install Cython"
RUN /bin/bash -l -c "pip3 install six"

RUN /bin/bash -l -c "pip3 install git+https://github.com/mechmotum/cyipopt.git"


FROM fenics-plus as fenics-pytorch
LABEL description="Pytorch image"

WORKDIR /src

# Install essential Python packages
RUN python3 -m pip --no-cache-dir install \
    blackcellmagic\
    pytest \
    pytest-cov \
    numpy \
    matplotlib \
    scipy \
    pandas \
    jupyter \
    scikit-learn \
    scikit-image \
    seaborn \
    graphviz \
    gpustat \
    h5py \
    gitpython \
    ptvsd \
    Pillow==6.1.0 \
    opencv-python
RUN python3 -m pip --no-cache-dir install nvidia-pyindex 
RUN python3 -m pip --no-cache-dir install nvidia-tensorrt 
RUN python3 -m pip --no-cache-dir install torch-tensorrt==v1.3.0 \
    -f https://github.com/pytorch/TensorRT/releases/expanded_assets/v1.3.0

RUN python3 -m pip --no-cache-dir install ogs5py
RUN python3 -m pip --no-cache-dir install dill



# Add profiling library support
ENV LD_LIBRARY_PATH /usr/local/cuda/extras/CUPTI/lib64:${LD_LIBRARY_PATH}
