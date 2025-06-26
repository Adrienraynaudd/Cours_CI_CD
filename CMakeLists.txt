cmake_minimum_required(VERSION 4.0)
project(simeis)

set(SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR})

add_custom_command(
    OUTPUT ${SOURCE_DIR}/target/release/simeis
    COMMAND ${CMAKE_COMMAND} -E env RUSTFLAGS=-C\ code-model=kernel\ -C\ strip=symbols\ -C\ codegen-units=1 cargo build --release
    WORKING_DIRECTORY ${SOURCE_DIR}
    COMMENT "Compilation du projet Rust en mode release avec options codegen"
)

add_custom_target(build_rust ALL
    DEPENDS ${SOURCE_DIR}/target/release/simeis
)


install(PROGRAMS ${SOURCE_DIR}/target/release/simeis DESTINATION bin)

find_program(TYPST_EXECUTABLE typst REQUIRED)
set(MANUAL_SOURCE ${SOURCE_DIR}/doc/manual.typ)
set(MANUAL_OUTPUT ${SOURCE_DIR}/doc/manual.pdf)

add_custom_command(
    OUTPUT ${MANUAL_OUTPUT}
    COMMAND ${TYPST_EXECUTABLE} compile ${MANUAL_SOURCE} ${MANUAL_OUTPUT}
    DEPENDS ${MANUAL_SOURCE}
    COMMENT "Compilation du manuel avec Typst"
)

add_custom_target(build_manual
    DEPENDS ${MANUAL_OUTPUT}
)

add_custom_target(rust_check
    COMMAND cargo check
    WORKING_DIRECTORY ${SOURCE_DIR}
    COMMENT "Analyse statique du code avec cargo check"
)

add_custom_target(rust_test
    COMMAND cargo test
    WORKING_DIRECTORY ${SOURCE_DIR}
    COMMENT "Lancement des tests unitaires avec cargo test"
)

add_custom_target(rust_clean
    COMMAND cargo clean
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${SOURCE_DIR}/target/release
    COMMAND ${CMAKE_COMMAND} -E remove ${MANUAL_OUTPUT}
    COMMENT "Nettoyage de l'environnement de développement (build, manuel, etc.)"
)

add_custom_target(full_build
    DEPENDS build_rust build_manual rust_check rust_test
    COMMENT "Build complet du projet : Rust + Doc + Check + Tests"
)