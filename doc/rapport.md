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

## Prépartion des releases

## Déploiement des releases

## Retour d'expérience