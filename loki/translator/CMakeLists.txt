cmake_minimum_required(VERSION 3.2)
project(vm_core)

# --- General -----------------------------------------------------------------

find_program(CCACHE_PROGRAM ccache)
if(CCACHE_PROGRAM)
    set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE "${CCACHE_PROGRAM}")
endif()

# set(CMAKE_BUILD_TYPE "RelWithDebInfo")
set(CMAKE_BUILD_TYPE "Debug")

set(CMAKE_INSTALL_PREFIX "/usr/local")

set(CMAKE_PREFIX_PATH "${CMAKE_SOURCE_DIR}/llvm")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin")

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 14)

set(PROJECT_CXX_FLAGS -gdwarf-2 -g3)

list(APPEND PROJECT_INCLUDES ${CMAKE_CURRENT_BINARY_DIR})
list(APPEND PROJECT_INCLUDES ${CMAKE_CURRENT_SOURCE_DIR})

list(APPEND PROJECT_LINK_FLAGS -Wl,--gc-sections)

# This needs to match LLVM's configuration for a static build.
list(APPEND PROJECT_CXX_FLAGS -fno-exceptions -fno-rtti)
list(APPEND PROJECT_CXX_FLAGS -ffunction-sections -fdata-sections -pedantic)

# --- LLVM --------------------------------------------------------------------

# LLVM HEAD: e6f22596e5de7f4fc6f1de4725d4aa9b6aeef4aa
# LLVM build options:
#
# cmake \
#   -G "Ninja" \
#   -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
#   -DCMAKE_BUILD_TYPE=RelWithDebInfo \
#   -DCMAKE_INSTALL_PREFIX=$HOME/git/compiler/llvm-installed \
#   -DLLVM_CCACHE_DIR=$HOME/git/compiler/llvm-project/ccache \
#   -DLLVM_ENABLE_CXX1Y=On \
#   -DLLVM_ENABLE_IDE=On \
#   -DLLVM_ENABLE_PROJECTS=clang \
#   -DLLVM_TARGETS_TO_BUILD="X86;ARM" \
#   -DLLVM_PARALLEL_COMPILE_JOBS=6 \
#   -DLLVM_PARALLEL_LINK_JOBS=6 \
#   -DLLVM_USE_LINKER=gold \
#   -DLLVM_BUILD_LLVM_DYLIB=On \
#   ../llvm
#
# Alternatively, try -DBUILD_SHARED_LIBS instead of -DLLVM_BUILD_LLVM_DYLIB
# if it still links statically.
#
# After building, make sure to symlink the `llvm` directory in this project's
# root directory to the install directory of LLVM (here, `llvm-installed`).

find_package(LLVM REQUIRED CONFIG HINTS ${FINDPACKAGE_LLVM_HINTS})

string(REPLACE "." ";" LLVM_VERSION_LIST ${LLVM_PACKAGE_VERSION})

list(GET LLVM_VERSION_LIST 0 LLVM_MAJOR_VERSION)
list(GET LLVM_VERSION_LIST 1 LLVM_MINOR_VERSION)

set(LLVM_VERSION "${LLVM_MAJOR_VERSION}.${LLVM_MINOR_VERSION}")

set(LLVM_ENABLE_EH OFF)
set(LLVM_ENABLE_RTTI OFF)
set(LLVM_ENABLE_ASSERTIONS ON)

set(LLVM_LIBRARIES
    LLVMCore LLVMLTO LLVMSupport
    LLVMInstCombine
    LLVMMC
    LLVMIRReader
    LLVMBitReader LLVMBitWriter
    LLVMAnalysis
    LLVMipo LLVMTransformUtils LLVMScalarOpts
    LLVMX86CodeGen
    LLVMX86AsmParser
    LLVMX86AsmPrinter
    LLVMX86Desc
    LLVMX86Info
)

# TODO: This seems to be broken in some way.
#llvm_map_components_to_libnames(${LLVM_LIBRARIES}
#        core support mc ipo mcjit transformutils scalarops instcombine lto
#        x86codegen x86asmparser x86asmprinter x86desc x86info)

list(APPEND PROJECT_DEFINITIONS ${LLVM_DEFINITIONS})
list(APPEND PROJECT_INCLUDES ${LLVM_INCLUDE_DIRS})
list(APPEND PROJECT_LIBRARIES ${LLVM_LIBRARIES})

message(STATUS "Using LLVM version ${LLVM_MAJOR_VERSION}.${LLVM_MINOR_VERSION}")
message(STATUS "Available libraries: ${LLVM_AVAILABLE_LIBS}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")
message(STATUS "Using includes: ${PROJECT_INCLUDES}")
message(STATUS "Using libraries: ${PROJECT_LIBRARIES}")

# --- Clang -------------------------------------------------------------------

find_package(Clang REQUIRED)
set(CLANG_LIBRARIES clangIndex clangCodeGen clangASTMatchers clangTooling)
list(APPEND PROJECT_LIBRARIES ${CLANG_LIBRARIES})

# --- Target ------------------------------------------------------------------

set(BINARY_NAME generate-vm-${LLVM_MAJOR_VERSION}.${LLVM_MINOR_VERSION})

if(NOT DEFINED LLVM_INSTALL_PREFIX)
	set(LLVM_INSTALL_PREFIX ${CMAKE_SOURCE_DIR}/llvm)
endif()

set(VM_TEMPLATE_COMPILER ${LLVM_INSTALL_PREFIX}/bin/clang)
message(STATUS "Using template compiler: ${VM_TEMPLATE_COMPILER}")

set(VM_TEMPLATE_IN ${CMAKE_SOURCE_DIR}/src/template.cpp)
set(VM_TEMPLATE ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/template.bc)

set(VM_LIFT_ME_IN ${CMAKE_SOURCE_DIR}/src/input_program.cpp)
set(VM_LIFT_ME ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/input_program.bc)

add_custom_command(OUTPUT ${VM_TEMPLATE}
    COMMAND ${VM_TEMPLATE_COMPILER}
    ARGS -c -emit-llvm --std=c++14 -O3 ${VM_TEMPLATE_IN} -o ${VM_TEMPLATE}
    DEPENDS ${VM_TEMPLATE_IN}
    IMPLICIT_DEPENDS CXX
)

add_custom_command(OUTPUT ${VM_LIFT_ME}
    COMMAND ${VM_TEMPLATE_COMPILER}
    ARGS -c -emit-llvm --std=c++14 -O3 -Xclang -disable-llvm-passes
         ${VM_LIFT_ME_IN} -o ${VM_LIFT_ME}
    DEPENDS ${VM_LIFT_ME_IN}
    IMPLICIT_DEPENDS CXX
)

add_custom_target(vm_template DEPENDS ${VM_TEMPLATE})
add_custom_target(test_input DEPENDS ${VM_LIFT_ME})

add_executable(${BINARY_NAME}
    src/generate_vm.cpp
)

add_executable(vm_template_standalone
    src/template.cpp
)

add_executable(lift_input
    src/lift_input.cpp
)

if (${LLVM_ENABLE_ASSERTIONS})
    target_compile_options(${BINARY_NAME} PRIVATE -UNDEBUG)
else()
    target_compile_definitions(${BINARY_NAME} PRIVATE -DNDEBUG)
endif()
 
link_directories(${BINARY_NAME} PRIVATE ${LLVM_DIR}/lib)
target_link_libraries(${BINARY_NAME} PRIVATE
    ${PROJECT_LIBRARIES}
    ${PROJECT_LINK_FLAGS}
)

link_directories(lift_input PRIVATE ${LLVM_DIR}/lib)
target_link_libraries(lift_input PRIVATE
    ${PROJECT_LIBRARIES}
    ${PROJECT_LINK_FLAGS}
)

target_include_directories(${BINARY_NAME} SYSTEM PUBLIC ${PROJECT_INCLUDES})
target_include_directories(lift_input SYSTEM PUBLIC ${PROJECT_INCLUDES})

target_compile_definitions(${BINARY_NAME} PUBLIC ${PROJECT_DEFINITIONS})
target_compile_options(${BINARY_NAME} PRIVATE ${PROJECT_CXX_FLAGS})

target_compile_definitions(lift_input PUBLIC ${PROJECT_DEFINITIONS})
target_compile_options(lift_input PRIVATE ${PROJECT_CXX_FLAGS})

add_dependencies(lift_input test_input)
add_dependencies(${BINARY_NAME} lift_input vm_template)
