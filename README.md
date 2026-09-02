# 🛒 Mon Panier

**Mon Panier** est une intégration personnalisée pour [Home Assistant](https://www.home-assistant.io/) dédiée à la gestion des listes de courses.

L'objectif est de proposer une solution **locale, légère et simple**, directement intégrée à Home Assistant.

## ✨ Fonctionnalités prévues

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
* 🌐 Utilisation d'Open Food Facts comme référentiel externe
* 🧠 Apprentissage des préférences et corrections personnelles
* 🤖 **Aucun moteur IA requis**
* 🏠 Fonctionnement local dans Home Assistant
* 🔌 Services et événements permettant à d'autres intégrations Home Assistant d'utiliser Mon Panier

## 🏗️ Philosophie du projet

Mon Panier est conçu pour être :

* **Local** — les données personnelles restent dans Home Assistant
* **Léger** — adapté aux installations Home Assistant sur matériel limité
* **Indépendant** — le moteur de gestion des courses ne dépend pas de l'interface
* **Extensible** — utilisable par d'autres intégrations et automatisations
* **Simple** — pas de serveur externe obligatoire, pas de compte et pas d'abonnement

L'interface graphique n'est qu'une des façons d'utiliser Mon Panier.

Les services Home Assistant permettront également à d'autres intégrations ou automatisations d'ajouter et de modifier des articles.

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

Les catégories sans article ne sont pas affichées.

Lorsqu'un article est acheté, il est automatiquement masqué de la liste active. Il reste disponible dans l'historique.

## 🔎 Recherche de produits

La recherche est conçue pour fonctionner sans IA.

Elle utilise plusieurs niveaux :

1. Produits personnels
2. Référentiel intégré
3. Synonymes et variantes
4. Correspondance partielle
5. Recherche approximative
6. Open Food Facts si nécessaire
7. Création manuelle si le produit reste inconnu

Par exemple :

```text
pdt        → Pommes de terre
patates    → Pommes de terre
ban        → Bananes
lardon     → Lardons
```

Les corrections personnelles sont mémorisées afin d'améliorer progressivement les résultats pour chaque installation.

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
          ├── trouvé → validation
          │
          └── inconnu → ajout manuel
```

Une association entre le code-barres et le produit est ensuite mémorisée localement.

## 🔌 Intégration avec Home Assistant

Mon Panier est conçu comme un véritable composant Home Assistant.

Des services permettront notamment de :

```yaml
action: mon_panier.add_item
data:
  store: leclerc
  product: piles AA
  quantity: 4
```

Les automatisations et d'autres intégrations pourront ainsi utiliser Mon Panier sans passer par son interface graphique.

Des événements permettront également de réagir aux actions effectuées dans les listes.

## 🏪 Magasins

Chaque magasin possède sa propre liste.

Exemple :

```text
🛒 Leclerc
🛒 Carrefour
🛒 Lidl
```

Chaque magasin possède un identifiant interne stable indépendant de son nom affiché.

## 📂 Structure du projet

```text
mon-panier/
├── .github/
│   └── workflows/
├── custom_components/
│   └── mon_panier/
│       ├── core/
│       ├── integrations/
│       ├── barcode/
│       ├── data/
│       ├── frontend/
│       └── translations/
├── tests/
├── hacs.json
├── README.md
├── CHANGELOG.md
├── LICENSE
├── CONTRIBUTING.md
├── pyproject.toml
└── .gitignore
```

## 🚧 État du projet

**Version actuelle : 0.1.0**

Le projet est actuellement en développement.

L'architecture est construite progressivement afin de tester chaque composant avant d'ajouter le suivant.

### Développement prévu

* [x] Définition de l'architecture
* [x] Définition des catégories
* [x] Définition du modèle de données
* [x] Définition du fonctionnement des listes
* [x] Définition du fonctionnement des magasins
* [x] Définition du fonctionnement du scanner
* [x] Choix d'Open Food Facts
* [x] Définition des services Home Assistant
* [ ] Socle de l'intégration
* [ ] Création des magasins
* [ ] Stockage des données
* [ ] Référentiel produits
* [ ] Recherche et suggestions
* [ ] Gestion des articles
* [ ] Historique
* [ ] Apprentissage personnel
* [ ] Open Food Facts
* [ ] Scanner
* [ ] Interface graphique
* [ ] Tests
* [ ] Compatibilité HACS
* [ ] Première version stable

## 📦 Installation

> L'installation HACS sera documentée lorsque la première version installable sera prête.

Pendant le développement, l'intégration peut être placée manuellement dans :

```text
/config/custom_components/mon_panier/
```

Puis Home Assistant peut être redémarré.

## 🧪 Développement

Le projet utilise Python pour le backend Home Assistant et des Web Components pour l'interface.

Les tests seront ajoutés progressivement dans :

```text
tests/
```

L'objectif est de tester le moteur indépendamment de l'interface graphique.

## 🌐 Open Food Facts

Mon Panier peut utiliser **Open Food Facts** comme source externe lorsque le produit n'est pas connu localement.

Open Food Facts reste une source de secours : les données et préférences personnelles de Mon Panier conservent la priorité.

## 📄 Licence

La licence du projet sera définie avant la première publication publique.

## ❤️ Projet

**Mon Panier** est développé pour Home Assistant avec l'objectif de fournir une gestion de courses locale, légère et facilement intégrable dans l'écosystème Home Assistant.

Dépôt :

`https://github.com/Eole35/mon_panier`
