# 🛒 Mon Panier

**Mon Panier** est une intégration personnalisée pour [Home Assistant](https://www.home-assistant.io/) dédiée à la gestion des listes de courses.

L'objectif est de proposer une solution **locale, légère, simple et extensible**, directement intégrée à Home Assistant.

Le projet est conçu pour fonctionner sans serveur externe, sans compte utilisateur et sans abonnement.

---

## ✨ Fonctionnalités

Mon Panier est conçu autour des fonctionnalités suivantes :

* 🏪 Plusieurs magasins, chacun avec sa propre liste
* 📝 Ajout rapide d'articles
* 🔎 Suggestions de produits dès 2 caractères
* 📦 Gestion des quantités et unités
* 🗂️ Classement automatique par catégorie
* ⭐ Produits favoris
* 🏷️ Promotion
* 🟢 Produit bio
* 📦 Grand volume
* ☑️ Gestion des articles achetés
* 📜 Historique des achats
* 📷 Lecture de codes-barres
* 🌐 Utilisation d'Open Food Facts comme source externe
* 🧠 Apprentissage des préférences et corrections personnelles
* 🤖 Aucun moteur IA requis
* 🏠 Fonctionnement local dans Home Assistant
* 🔌 Services et événements permettant à d'autres intégrations Home Assistant d'utiliser Mon Panier

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

L'ordre des catégories pourra être personnalisé pour chaque magasin.

Les catégories sans article ne sont pas affichées.

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

Il reste disponible dans l'historique des achats.

---

## 🔎 Recherche de produits

La recherche est conçue pour fonctionner **sans intelligence artificielle**.

Elle utilise progressivement plusieurs niveaux de recherche :

1. Produits personnels
2. Référentiel intégré
3. Synonymes et variantes
4. Correspondance partielle
5. Recherche approximative
6. Open Food Facts si nécessaire
7. Création manuelle si le produit reste inconnu

La recherche devient disponible à partir de **2 caractères**.

Exemples :

```text
pdt        → Pommes de terre
patates    → Pommes de terre
ban        → Bananes
lardon     → Lardons
```

Les produits favoris et les produits déjà utilisés sont pris en compte dans la recherche.

Les corrections personnelles sont mémorisées afin d'améliorer progressivement les résultats pour chaque installation.

---

## 📦 Quantités et unités

Mon Panier permet de gérer différentes unités :

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

Par exemple :

```text
Bananes × 5
+
Bananes × 3
=
Bananes × 8
```

---

## ⭐ Produits favoris

Un produit peut être marqué comme **favori**.

Les favoris sont utilisés pour améliorer la priorité des suggestions.

Le statut favori appartient au **produit** et non à un article particulier de la liste.

---

## 📷 Code-barres

Le fonctionnement prévu est :

```text
Code-barres
    ↓
Recherche locale
    ├── trouvé → ajout immédiat
    │
    └── inconnu
          ↓
    Open Food Facts
          ├── trouvé → validation utilisateur
          │
          └── inconnu → ajout manuel
```

Les formats pris en charge actuellement sont :

* EAN-8
* EAN-13
* UPC-A

Après validation d'un produit provenant d'Open Food Facts, l'association entre le code-barres et le produit est mémorisée localement.

---

## 🌐 Open Food Facts

Mon Panier peut utiliser **Open Food Facts** comme source externe lorsqu'un produit n'est pas connu localement.

Le fonctionnement privilégie toujours les données locales :

```text
Produit personnel
      ↓
Référentiel intégré
      ↓
Open Food Facts
      ↓
Création manuelle
```

Un produit découvert via Open Food Facts doit être validé avant d'être mémorisé dans la base locale.

Open Food Facts est donc utilisé comme **source de secours**, et non comme base obligatoire au fonctionnement de Mon Panier.

L'utilisation d'Open Food Facts peut être configurée dans les options de l'intégration.

---

## 🧠 Apprentissage personnel

Mon Panier ne nécessite aucun moteur IA.

L'apprentissage repose sur des associations locales entre les saisies de l'utilisateur et les produits.

Par exemple :

```text
"lardons allumette"
        ↓
Lardons allumettes
```

Une correction personnelle peut ensuite être réutilisée lors des recherches suivantes.

Les corrections personnelles ont priorité sur les données génériques du référentiel.

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

Chaque magasin peut également disposer de son propre ordre de catégories.

L'historique des achats est conservé indépendamment de la liste active.

---

## 📜 Historique

Lorsqu'un article est marqué comme acheté, il peut être conservé dans l'historique avec notamment :

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

## 🔌 Intégration avec Home Assistant

Mon Panier est conçu comme un véritable composant Home Assistant.

Des services permettront notamment de gérer les listes et les magasins :

```yaml
action: mon_panier.add_item
data:
  store: leclerc
  product: piles AA
  quantity: 4
```

Les services prévus comprennent notamment :

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
```

Les automatisations et d'autres intégrations pourront ainsi utiliser Mon Panier sans passer par son interface graphique.

Des événements permettront également de réagir aux actions effectuées dans les listes.

---

## 🏗️ Philosophie du projet

Mon Panier est conçu pour être :

* **Local** — les données personnelles restent dans Home Assistant
* **Léger** — adapté aux installations Home Assistant sur matériel limité
* **Indépendant** — le moteur de gestion des courses ne dépend pas de l'interface
* **Extensible** — utilisable par d'autres intégrations et automatisations
* **Simple** — pas de serveur externe obligatoire, pas de compte et pas d'abonnement

L'interface graphique n'est qu'une des façons d'utiliser Mon Panier.

Le moteur métier est séparé de l'interface afin de permettre son utilisation par d'autres composants Home Assistant.

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
│       ├── services.yaml
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
│   ├── test_parser.py
│   ├── test_search.py
│   ├── test_repository.py
│   ├── test_learning.py
│   ├── test_services.py
│   ├── test_barcode.py
│   ├── test_product_service.py
│   └── test_category_mapper.py
│
├── hacs.json
├── README.md
├── CHANGELOG.md
├── LICENSE
├── CONTRIBUTING.md
├── pyproject.toml
└── .gitignore
```

---

## 🧪 Tests

Les tests sont regroupés dans le dossier :

```text
tests/
```

Ils couvrent progressivement les différentes parties du projet :

```text
tests/
├── test_parser.py
├── test_search.py
├── test_repository.py
├── test_learning.py
├── test_services.py
├── test_barcode.py
├── test_product_service.py
└── test_category_mapper.py
```

L'objectif est de tester le moteur métier indépendamment de l'interface graphique.

Les tests seront complétés au fur et à mesure de l'avancement du projet.

---

## 🚧 État du projet

**Version actuelle : 0.1.0**

Le projet est actuellement en développement.

L'architecture et les principaux composants du moteur sont en cours de construction et de validation.

### Avancement

* [x] Définition de l'architecture
* [x] Définition des catégories
* [x] Définition du modèle de données
* [x] Définition du fonctionnement des listes
* [x] Définition du fonctionnement des magasins
* [x] Définition du fonctionnement du scanner
* [x] Choix d'Open Food Facts
* [x] Définition des services Home Assistant
* [x] Moteur de recherche
* [x] Parser des quantités et unités
* [x] Modèle produits
* [x] Gestion des codes-barres
* [x] Mapping des catégories Open Food Facts
* [x] Service produit
* [x] Premiers tests automatisés
* [ ] Socle complet de l'intégration Home Assistant
* [ ] Stockage persistant Home Assistant
* [ ] Création et gestion complète des magasins
* [ ] Gestion complète des listes
* [ ] Référentiel produits final
* [ ] Recherche et suggestions intégrées à Home Assistant
* [ ] Historique complet
* [ ] Apprentissage personnel complet
* [ ] Intégration Open Food Facts complète
* [ ] Scanner intégré à l'interface
* [ ] Interface graphique
* [ ] Tests complets
* [ ] Validation HACS
* [ ] Première version stable

---

## 📦 Installation

### HACS

L'installation via HACS sera disponible lorsque l'intégration aura atteint un niveau suffisamment stable pour une première publication.

Le dépôt est conçu pour être compatible avec HACS.

### Installation manuelle

Pendant le développement, l'intégration peut être installée manuellement dans :

```text
/config/custom_components/mon_panier/
```

Après installation, redémarrez Home Assistant.

> ⚠️ La version 0.1.0 est une version de développement et ne doit pas encore être considérée comme une version stable.

---

## ⚙️ Configuration

Mon Panier utilise la configuration de Home Assistant.

Les options d'Open Food Facts permettent notamment de configurer :

* l'activation ou la désactivation d'Open Food Facts ;
* l'URL du service ;
* le pays ;
* la langue ;
* le User-Agent utilisé pour les requêtes.

Le fonctionnement local reste possible lorsque Open Food Facts est désactivé.

---

## 🔐 Données et confidentialité

Les données personnelles de Mon Panier sont destinées à rester dans l'installation Home Assistant.

Open Food Facts est uniquement utilisé lorsqu'une recherche externe est nécessaire et que cette fonctionnalité est activée.

Les produits déjà connus localement n'ont pas besoin d'être recherchés sur Open Food Facts.

---

## 🤝 Contribution

Les contributions sont les bienvenues.

Le projet étant encore en développement, il est recommandé de consulter :

```text
CONTRIBUTING.md
```

avant de proposer des modifications importantes.

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
