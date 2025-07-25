cmake_minimum_required(VERSION 3.3)
project(SimeisBuild)

add_custom_target(build_simeis ALL
    COMMAND echo "building target build_simeis"
    SET ENV{RUSTFLAGS} "-C code-model=kernel -C codegen-units=1 -C strip=symbols"
    COMMAND cargo build --release
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

add_custom_target(build_manual
    COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_SOURCE_DIR}/doc
    COMMAND typst compile doc/manual.typ doc/manual.pdf
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

add_custom_target(check_code
    COMMAND cargo check
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

add_custom_target(run_tests
    COMMAND cargo test
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

add_custom_target(clean_dev
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_SOURCE_DIR}/target
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

