# 🛒 Mon Panier

**Mon Panier** est une intégration personnalisée pour [Home Assistant](https://www.home-assistant.io/) dédiée à la gestion des listes de courses.

L'objectif est de proposer une solution **locale, légère, simple et extensible**, directement intégrée à Home Assistant.

Le projet est conçu pour fonctionner sans serveur externe, sans compte utilisateur et sans abonnement.

---

## ✨ Fonctionnalités

Mon Panier propose notamment :

* 🏪 Plusieurs magasins, chacun avec sa propre liste
* 📝 Ajout rapide d'articles
* 🔎 Recherche locale de produits
* 📦 Gestion des quantités et unités
* 🗂️ Classement automatique par catégorie
* ⭐ Produits favoris
* 🏷️ Promotion
* 🟢 Produit bio
* 📦 Grand volume
* ☑️ Gestion des articles achetés
* 📜 Historique des achats
* 📷 Gestion des codes-barres
* 🌐 Recherche externe avec Open Food Facts
* 🧠 Mémorisation locale des produits validés
* 🤖 Aucun moteur IA requis
* 🏠 Fonctionnement local dans Home Assistant
* 🔌 Services Home Assistant utilisables par des automatisations et d'autres intégrations

---

## 🗂️ Catégories

Mon Panier utilise actuellement 17 catégories :

| Catégorie         | Icône |
| ----------------- | ----- |
| Fruits & légumes  | 🍎    |
| Viandes           | 🥩    |
| Poissonnerie      | 🐟    |
| Fromagerie        | 🧀    |
| Frais             | 🥚    |
| Produits laitiers | 🥛    |
| Boulangerie       | 🥖    |
| Épicerie          | 🥫    |
| Vrac              | 🥜    |
| Boissons          | 🥤    |
| Surgelés          | 🧊    |
| Bébé              | 👶    |
| Hygiène & beauté  | 🧴    |
| Entretien         | 🧹    |
| Maison            | 🏠    |
| Jardin            | 🌱    |
| Animaux           | 🐕    |

Les catégories sans article ne sont pas affichées.

La personnalisation de l'ordre des catégories reste prévue pour une évolution ultérieure.

---

## 🛒 Exemple

Une liste peut ressembler à ceci :

```text
🛒 Leclerc

🍎 Fruits & légumes
☐ Bananes × 5
☐ Pommes

🥩 Viandes
☐ Lardons × 500 g

🧀 Fromagerie
☐ Camembert

🥤 Boissons
☐ Eau × 6 bouteilles
```

Lorsqu'un article est acheté, il est automatiquement masqué de la liste active.

Il reste disponible dans l'historique des achats lorsque cette fonctionnalité est utilisée.

---

## 🔎 Recherche de produits

La recherche privilégie toujours les données locales.

Le fonctionnement général est :

```text
Saisie utilisateur
      ↓
Parsing de la quantité et de l'unité
      ↓
Recherche locale
      ├── produit connu → utilisation immédiate
      │
      └── produit inconnu
              ↓
        Open Food Facts
              ├── produit trouvé
              │      ↓
              │  confirmation utilisateur
              │      ↓
              │  mémorisation locale
              │
              └── aucun résultat
```

La recherche locale peut exploiter :

1. les produits personnels ;
2. les produits déjà mémorisés ;
3. les synonymes et variantes ;
4. les correspondances partielles.

Lorsqu'un produit n'est pas connu localement, Open Food Facts peut être utilisé comme source externe.

Un produit découvert sur Open Food Facts **n'est pas mémorisé automatiquement** : une confirmation utilisateur est nécessaire.

---

## 📦 Quantités et unités

Le parser intégré permet de distinguer la **quantité achetée** des informations concernant le conditionnement du produit.

Exemples :

```text
5 bananes
→ quantité : 5 pièces

2 pots de sauce
→ quantité : 2 pots

sauce mexicaine 300g
→ quantité : 1 pièce
→ quantité du produit : 300 g

2 pots de 300g de sauce mexicaine
→ quantité achetée : 2 pots
→ quantité du produit : information séparée
```

Les unités courantes comprennent notamment :

```text
pièce
paquet
boîte
bouteille
bidon
pot
sachet
barquette
rouleau
lot

g
kg
ml
cl
l
```

Les quantités décimales sont également prises en charge.

Exemples :

```text
5 bananes
500 g lardons
1,5 kg pommes de terre
6 bouteilles d'eau
2 barquettes de lardons
```

Lorsque le même produit possède les mêmes propriétés et la même unité, les quantités peuvent être regroupées.

```text
Bananes × 5
+
Bananes × 3
=
Bananes × 8
```

---

## 🌐 Open Food Facts

Mon Panier peut utiliser **Open Food Facts** comme source externe lorsqu'un produit n'est pas connu localement.

Les recherches utilisent l'API Open Food Facts et récupèrent notamment :

* le nom du produit ;
* la marque ;
* les catégories ;
* le code-barres ;
* la quantité du produit ;
* l'unité de quantité ;
* le conditionnement ;
* les informations de conditionnement.

Par exemple, un produit Open Food Facts peut fournir :

```text
Nom          : Sauce mexicaine medium
Marque       : Marque Repère, Tables du Monde
Quantité     : 315 g
Conditionnement : Verre, Bocal
Code-barres  : 3564700299067
```

Ces informations permettent de compléter la fiche produit locale.

### Confirmation utilisateur

Lorsqu'un produit est trouvé sur Open Food Facts, Mon Panier demande une confirmation avant de le mémoriser.

Le fonctionnement est :

```text
Recherche
   ↓
Open Food Facts
   ↓
Produit trouvé
   ↓
Confirmation utilisateur
   ├── confirmer → mémorisation locale + ajout à la liste
   │
   └── refuser   → aucune mémorisation
```

Une confirmation est associée au code-barres du produit trouvé.

Deux services permettent de gérer cette étape :

```text
mon_panier.confirm_product
mon_panier.reject_product
```

Après confirmation, le produit devient un produit local et pourra être retrouvé directement lors des recherches suivantes.

Le code-barres est également associé au produit local.

---

## 📷 Codes-barres

Les produits peuvent être associés à des codes-barres.

Lorsqu'un code-barres est connu localement, le produit peut être retrouvé sans effectuer de recherche externe.

Pour un produit inconnu, Open Food Facts peut être interrogé afin de récupérer ses informations.

Après validation, l'association est mémorisée localement :

```text
Code-barres
    ↓
Produit local
```

Les codes-barres de produits alimentaires courants sont principalement basés sur les formats EAN/UPC.

---

## 🧠 Mémorisation locale

Mon Panier privilégie les données locales.

Lorsqu'un produit Open Food Facts est confirmé :

```text
Open Food Facts
      ↓
Produit validé
      ↓
Produit local
      ↓
Mémorisation
```

Les informations récupérées peuvent notamment être conservées :

* nom ;
* marque ;
* quantité ;
* unité ;
* conditionnement ;
* catégories ;
* code-barres ;
* source du produit.

Les informations locales existantes ne sont pas écrasées inutilement par les données externes.

L'objectif est de construire progressivement un référentiel adapté à chaque installation Home Assistant.

---

## ⭐ Produits favoris

Un produit peut être marqué comme **favori**.

Les favoris sont destinés à améliorer la priorité des suggestions et la facilité d'utilisation.

Le statut favori appartient au **produit** et non à un article particulier de la liste.

---

## 🏪 Magasins

Chaque magasin possède sa propre liste.

Exemple :

```text
🛒 Leclerc
🛒 Carrefour
🛒 Lidl
```

Chaque magasin possède un identifiant interne stable indépendant de son nom affiché.

L'architecture permet de conserver les données des différents magasins indépendamment.

---

## 📜 Historique

L'historique permet de conserver les informations liées aux articles achetés.

Les données peuvent notamment comprendre :

* le magasin ;
* le produit ;
* la quantité ;
* l'unité ;
* le statut bio ;
* le statut promotion ;
* le statut grand volume ;
* la date d'achat.

L'historique est indépendant de la liste active.

---

## 🔌 Services Home Assistant

Mon Panier expose des services Home Assistant afin de pouvoir être utilisé depuis des automatisations ou d'autres intégrations.

### Ajouter un article

```yaml
action: mon_panier.add_item
data:
  store: leclerc
  product: piles AA
  quantity: 4
```

### Services disponibles

Les services actuellement intégrés comprennent notamment :

```text
mon_panier.add_item
mon_panier.remove_item
mon_panier.update_item
mon_panier.complete_item
mon_panier.uncomplete_item
mon_panier.clear_list
mon_panier.delete_list

mon_panier.create_store
mon_panier.rename_store
mon_panier.delete_store

mon_panier.confirm_product
mon_panier.reject_product
```

Les services de confirmation sont utilisés lorsqu'un produit a été trouvé sur Open Food Facts et attend une validation utilisateur.

L'intégration expose également des événements permettant aux autres composants de Home Assistant de réagir aux actions effectuées dans Mon Panier.

---

## 🏗️ Architecture

Le projet sépare le moteur métier de la couche Home Assistant.

Les principaux composants sont :

```text
Entrée utilisateur
       ↓
Parser
       ↓
ProductService
       ↓
Recherche locale
       ↓
Open Food Facts
       ↓
Confirmation
       ↓
Repository
       ↓
Liste de courses
```

Cette séparation permet notamment :

* de tester le moteur indépendamment de l'interface ;
* de conserver une logique métier locale ;
* de réutiliser les services depuis Home Assistant ;
* de faire évoluer l'interface sans réécrire le moteur.

---

## 📁 Structure du projet

```text
mon-panier/
├── .github/
│   └── workflows/
│
├── custom_components/
│   └── mon_panier/
│       ├── __init__.py
│       ├── manifest.json
│       ├── const.py
│       ├── config_flow.py
│       ├── coordinator.py
│       ├── sensor.py
│       ├── services.py
│       ├── services.yaml
│       ├── storage.py
│       ├── strings.json
│       │
│       ├── core/
│       │   ├── models.py
│       │   ├── repository.py
│       │   ├── search.py
│       │   ├── parser.py
│       │   ├── learning.py
│       │   ├── catalog.py
│       │   ├── product_service.py
│       │   └── category_mapper.py
│       │
│       ├── integrations/
│       │   └── openfoodfacts.py
│       │
│       ├── barcode/
│       │   ├── __init__.py
│       │   └── scanner.py
│       │
│       ├── data/
│       │   ├── categories.json
│       │   └── products.json
│       │
│       ├── frontend/
│       │
│       └── translations/
│
├── tests/
│
├── hacs.json
├── README.md
├── pyproject.toml
└── .gitignore
```

---

## 🧪 Tests

Les tests automatisés sont regroupés dans :

```text
tests/
```

Ils couvrent notamment :

* le parsing des quantités et unités ;
* les modèles de données ;
* le stockage ;
* la recherche de produits ;
* le service produit ;
* l'intégration Open Food Facts ;
* le mapping des catégories ;
* les services Home Assistant ;
* les confirmations de produits Open Food Facts.

L'état actuel du projet est vérifié par la suite de tests automatisés.

Dernière vérification :

```text
84 tests passed
```

Les tests sont exécutés avec :

```bash
pytest -q
```

---

## 🚧 État du projet

**Version actuelle : 0.1.0**

Le projet est toujours en développement, mais le socle de l'intégration est maintenant fonctionnel.

### Avancement

* [x] Architecture du projet
* [x] Modèle de données
* [x] Catégories
* [x] Produits
* [x] Listes et magasins
* [x] Repository
* [x] Stockage Home Assistant
* [x] Parser des quantités et unités
* [x] Recherche locale
* [x] Service produit
* [x] Mapping des catégories
* [x] Gestion des codes-barres
* [x] Intégration Open Food Facts
* [x] Récupération des métadonnées produit
* [x] Confirmation utilisateur des produits externes
* [x] Mémorisation locale des produits validés
* [x] Services Home Assistant principaux
* [x] Tests automatisés
* [x] Validation Hassfest
* [ ] Interface graphique complète
* [ ] Scanner intégré à l'interface
* [ ] Référentiel produit finalisé
* [ ] Recherche et suggestions avancées
* [ ] Apprentissage personnel complet
* [ ] Historique complet
* [ ] Personnalisation complète des catégories par magasin
* [ ] Première version stable
* [ ] Validation HACS

---

## 📦 Installation

### Développement

Pendant le développement, l'intégration peut être installée manuellement dans :

```text
/config/custom_components/mon_panier/
```

Puis redémarrer Home Assistant.

Pour le développement local, le dépôt peut également être lié symboliquement au dossier `custom_components` de Home Assistant.

### HACS

L'installation via HACS sera proposée lorsque l'intégration aura atteint un niveau de stabilité suffisant pour une première publication.

> ⚠️ La version 0.1.0 est une version de développement et ne doit pas encore être considérée comme une version stable.

---

## ⚙️ Configuration

Mon Panier utilise la configuration de Home Assistant.

Open Food Facts peut être activé ou désactivé selon la configuration de l'intégration.

Lorsque la recherche externe est activée, les requêtes utilisent les paramètres configurés pour Open Food Facts, notamment la langue et les informations nécessaires à l'identification du client.

Le fonctionnement local reste possible sans Open Food Facts.

---

## 🔐 Données et confidentialité

Les données personnelles de Mon Panier sont destinées à rester dans l'installation Home Assistant.

Les produits connus localement sont recherchés en priorité.

Open Food Facts est sollicité uniquement lorsqu'une recherche externe est nécessaire et que cette fonctionnalité est activée.

Lorsqu'une donnée est récupérée depuis Open Food Facts, elle n'est pas automatiquement mémorisée : une validation utilisateur est nécessaire.

---

## 🤝 Contribution

Les contributions sont les bienvenues.

Le projet étant encore en développement, il est recommandé de consulter les éventuelles instructions de contribution avant de proposer des modifications importantes.

Les contributions doivent préserver les objectifs principaux du projet :

* simplicité ;
* fonctionnement local ;
* faible consommation de ressources ;
* indépendance vis-à-vis de l'interface ;
* compatibilité Home Assistant ;
* absence de dépendance obligatoire à l'IA.

---

## 📄 Licence

La licence du projet sera définie avant la première version stable.

---

## ❤️ Projet

**Mon Panier** est développé pour Home Assistant avec l'objectif de fournir une gestion de courses locale, légère et facilement intégrable dans l'écosystème Home Assistant.

Dépôt :

`https://github.com/Eole35/mon_panier`
