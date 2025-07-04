# Rapport, retour d'expérience

## Le projet: Simeis

Simeis est un jeu par API (inspiré de SpaceTraders), dont le but est de faire fructifier votre
empire économique dans toute la galaxie.

### Le principe

Dans ce jeu, vous devez gérer votre flotte de vaisseaux miniers. Pour cela, vous pouvez acheter des vaisseaux et leur affecter un équipage. Ensuite, vous pouvez les envoyer sur différentes planètes afin de récupérer les ressources disponibles. Après quoi, elles peuvent être transférées à la station pour pouvoir les vendre. Vous pouvez également améliorer votre station ainsi que vos vaisseaux ou membre d'équipage afin de produire plus, stocker plus et vendre plus pour optimiser votre empire. Plus de détails sont disponibles dans le [manuel du jeu](./manual.pdf).

### technologie

Le projet est développé en Rust et build avec Cargo.
Pour lancé le serveur, il suffit de lancer la commande `cargo run --release` à la racine du projet.
Cargo ce chargeras de télécharger les dépendances ainsi que de compiler le projet.
Si vous souhaitez lancer le serveur en mode debug, il suffit de lancer la commande `cargo run`.
Vous pouvez également build le projet avec la commande `cargo build --release` pour générer un binaire dans le dossier `target/release/simeis-server`.
La variante debug est également disponible via la commande `cargo build`, le binaire sera alors dans le dossier `target/debug/simeis-server`.

### Architecture

L'API est composer de deux dossiers principaux :
- `simeis-data` : contient les modèles de données ainsi que les fonctions métier.
- `simeis-api` : contient les routes de l'API ainsi que la configuration

```
├── simeis-data
│   ├── src
│   │   ├── galaxy
│   │   │   ├── planet.rs
│   │   │   ├── scan.rs
│   │   │   └── station.rs
│   │   ├── ship
│   │   │   ├── cargo.rs
│   │   │   ├── module.rs
│   │   │   ├── navigation.rs
│   │   │   ├── resource.rs
│   │   │   ├── shipstats.rs
│   │   │   └── upgrade.rs
│   │   ├── crew.rs
│   │   ├── error.rs
│   │   ├── galaxy.rs
│   │   ├── game.rs
│   │   ├── lib.rs
│   │   ├── market.rs
│   │   ├── player.rs
│   │   ├── ship.rs
│   │   ├── syslog.rs
│   │   └── tests.rs
│   └── Cargo.toml
├── simeis-api
│   ├── src
│   │   ├── api.rs
│   │   └── main.rs
│   └── Cargo.toml
└── Cargo.toml
```



## Workflow développement

Pour optimiser la CI plusieurs workflows ont été mis en place :
- `dependabot` :  Le workflow dependabot permet de mettre à jour les dépendances du projet automatiquement, à minuit, tous les jours.
- `dev-workflow` :  dev-workflow est executé à chaque pull request sur la branche `main`. Il va lancer tout les tests afin de verifier que le code ajouté sur `main` n'apporte pas de problemes au projet.
- `matrice-check` :  Lors d'une pull request sur `main`, si la branche source commence par `feature/`, ce workflow va tester si le projet fonctionne sur different systemes d'exploitation (Linux, MacOS, Windows) mais aussi sur differente version de Rust.
- `propagate-workflow` :  Lorsqu'une pull request est fermée, si elle a été fusionnée, que la branche source commence par `bug/` et que le label contient `propagate`, ce workflow va créer une nouvelle pull request sur chaque release afin de propager les changements sur toutes les versions du projet.
- `PR-workflow` :  Ce workflow est executé lors d'une pull request sur les branches `main` ou `release/*`. Il va lancer plusieurs verification sur le nouveau code :  

    **Verification Rust/Cargo** :  
    - Verifie que le code compile grace a `cargo check`
    - Verifie que le code respecte les conventions de formattage grace a `cargo fmt--check`
    - Verification supplementaire pour detecter les problemes grace a `cargo clippy`  
    
    **Verification CMake** :  
    - Verifie que le code peut build correctement grace a `cmake --build . --target check_code`  
    - Build le code grace a `cmake --build . --target build_simeis`  
    - Genere la documentation grace a `cmake --build . --target build_manual`  
    - Execute les tests grace a `cmake --build . --target run_tests`  
    - Nettoie les fichiers de build grace a `cmake --build . --target clean_dev`  
    
    **Verification des TODO** :  
    - Verifie que les TODO et les FIXME sont bien lié a une issue  
    


### Prépartion des releases  
`release-workflow` : release-workflow est executé lors d'une pull request sur `release/*`.  
Il va lancer plusieurs Jobs :  
- **heavy-testing** :  
        Ce job va lancer les tests sur le projet pour verifier que toute les fonctionnalitées sont bien fonctionnelles.  
- **cargo-audit** :  
        Cargo-audit va venir verifier que les dépendances du projet ne contiennent pas de vulnérabilités.  
- **check-dep** :  
        Ici on va verifier que toutes les dépendances sont utilisées dans le projet.  
- **functional-tests** :  
        Ce job va executer les tests fonctionnels du projet.
- **coverage** :  
        Le job coverage va verifier que les tests couvrent au moins 50 % du code.
- **verificationSource** :  
        Ce job verifie que le code source vient soit de la branche `bug/` soit de la branche `main/` pour pouvoir être fusionné dans la branche `release/*`.  
### Déploiement des releases   
`auto-release` : Ce workflow est executé lorsqu'on push sur `release/*`. Avec le job `auto-create-update-release`, la branche release est créée avec le tag de la nouvelle version. Si la version de la release existe deja , le workflow va mettre à jour la release existante.   
Ensuite le job `package-deb` recupere le binaire puis créé un package debian pour executer le serveur sur Linux enfin le job renoie l'artefact.
## Retour d'expérience