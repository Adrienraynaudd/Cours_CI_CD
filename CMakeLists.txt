cmake_minimum_required(VERSION 4.0)
project(simeis)

add_custom_target(build-rust ALL
    COMMAND ${CMAKE_COMMAND} -E env
        RUSTFLAGS="-C code-model=kernel -C codegen-units=1 -C strip=symbols"
        cargo build --workspace --release
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Compilation du workspace Rust"
)

add_custom_target(manual
    COMMAND typst compile ${CMAKE_SOURCE_DIR}/doc/manual.typ ${CMAKE_SOURCE_DIR}/doc/manual.pdf
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Génération du rapport PDF via Typst"
)

add_custom_target(check
    COMMAND cargo check
    COMMENT "Vérification du code Rust"
)

add_custom_target(test
    COMMAND cargo test
    COMMENT "Lancement des tests Rust"
)

add_custom_target(clear
    COMMAND cargo clean
    COMMENT "Nettoyage de l'environnement de build"
)