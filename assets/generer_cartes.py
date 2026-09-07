"""Genere les cartes SVG du profil.

Pourquoi ne pas utiliser github-readme-stats. Le service etait en panne au
moment d'ecrire ces lignes, et rendait 503 sur les trois points de terminaison
utilises. Un profil dont les visuels dependent d'un service tiers gratuit
affiche des images cassees le jour ou ce service tombe, et ce jour arrive
toujours au mauvais moment.

Les cartes sont donc des fichiers du depot. Elles sont servies par GitHub,
elles ne peuvent pas tomber, et elles portent les chiffres reels des projets
plutot que des compteurs generiques.

Le theme suit celui du lecteur : une requete `prefers-color-scheme` dans le SVG
lui-meme, qui fonctionne meme charge via une balise `img`.

    python assets/generer_cartes.py
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

SORTIE = Path(__file__).parent

LARGEUR = 420
HAUTEUR = 150

POLICE = (
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
)

# Palette claire, puis les jetons redefinis en sombre. Aucune couleur n'existe
# uniquement dans le bloc sombre : une carte a fond transparent emprunterait le
# fond de la page et deviendrait illisible dans l'autre theme.
STYLE = """
    .fond   {{ fill: #ffffff; stroke: #d1d9e0; }}
    .titre  {{ fill: #0969da; font: 600 15px {police}; }}
    .desc   {{ fill: #59636e; font: 400 12px {police}; }}
    .metric {{ fill: #1f2328; font: 700 30px {police}; }}
    .unite  {{ fill: #59636e; font: 400 11px {police}; }}
    .pied   {{ fill: #59636e; font: 400 10.5px {police}; }}
    .accent {{ fill: {accent}; }}
    @media (prefers-color-scheme: dark) {{
      .fond   {{ fill: #0d1117; stroke: #3d444d; }}
      .titre  {{ fill: #4493f8; }}
      .desc   {{ fill: #9198a1; }}
      .metric {{ fill: #f0f6fc; }}
      .unite  {{ fill: #9198a1; }}
      .pied   {{ fill: #9198a1; }}
    }}
"""

CARTES = [
    {
        "fichier": "kev-triage.svg",
        "titre": "kev-triage",
        "desc": "Triage de vulnérabilités par risque réel",
        "metrique": "238 → 14",
        "unite": "vulnérabilités trouvées, à traiter",
        "pied": "OSV + EPSS + KEV de la CISA",
        "tests": "31 tests",
        "accent": "#cf222e",
    },
    {
        "fichier": "ios-config-audit.svg",
        "titre": "ios-config-audit",
        "desc": "Durcissement d'une configuration Cisco IOS",
        "metrique": "16 / 16",
        "unite": "écarts sur une config d'usine",
        "pied": "acces, auth, services, logs, interfaces",
        "tests": "47 tests",
        "accent": "#1BA0D7",
    },
    {
        "fichier": "azure-sftp-lab.svg",
        "titre": "azure-sftp-lab",
        "desc": "Service SFTP sur Azure, décrit en Bicep",
        "metrique": "10",
        "unite": "contrôles après déploiement",
        "pied": "sans mot de passe ni clé de compte",
        "tests": "11 tests",
        "accent": "#0078D4",
    },
    {
        "fichier": "linux-hardening-audit.svg",
        "titre": "linux-hardening-audit",
        "desc": "Durcissement SSH et noyau d'un hôte Linux",
        "metrique": "18",
        "unite": "règles, sshd_config et sysctl",
        "pied": "la première occurrence gagne, et ça se voit",
        "tests": "22 tests",
        "accent": "#E95420",
    },
    {
        "fichier": "authlog-watch.svg",
        "titre": "authlog-watch",
        "desc": "Détection d'anomalies dans un auth.log",
        "metrique": "4",
        "unite": "alertes, la compromission en tête",
        "pied": "force brute, pulvérisation, succès avérés",
        "tests": "19 tests",
        "accent": "#8250df",
    },
    {
        "fichier": "veille-certfr.svg",
        "titre": "veille-certfr",
        "desc": "Veille CERT-FR filtrée sur un inventaire",
        "metrique": "100 → 3",
        "unite": "avis par mois, lignes utiles",
        "pied": "avis, alertes et actualités séparés",
        "tests": "16 tests",
        "accent": "#1a7f37",
    },
]


def carte(donnees: dict) -> str:
    style = STYLE.format(police=POLICE, accent=donnees["accent"])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{LARGEUR}" height="{HAUTEUR}" \
viewBox="0 0 {LARGEUR} {HAUTEUR}" role="img" aria-label="{escape(donnees['titre'])}">
  <style>{style}</style>
  <rect class="fond" x="0.5" y="0.5" width="{LARGEUR - 1}" height="{HAUTEUR - 1}" rx="10"/>
  <rect class="accent" x="0.5" y="0.5" width="4" height="{HAUTEUR - 1}" rx="2"/>
  <text class="titre" x="22" y="30">{escape(donnees['titre'])}</text>
  <text class="desc" x="22" y="50">{escape(donnees['desc'])}</text>
  <text class="metric" x="22" y="92">{escape(donnees['metrique'])}</text>
  <text class="unite" x="22" y="110">{escape(donnees['unite'])}</text>
  <line x1="22" y1="122" x2="{LARGEUR - 22}" y2="122" stroke="#d1d9e0" stroke-width="1" opacity="0.5"/>
  <text class="pied" x="22" y="138">{escape(donnees['pied'])}</text>
  <text class="pied" x="{LARGEUR - 22}" y="138" text-anchor="end">{escape(donnees['tests'])}</text>
</svg>
"""


def bandeau() -> str:
    """Une bande unique qui remplace la carte de statistiques du service tiers."""
    largeur, hauteur = 860, 104
    style = STYLE.format(police=POLICE, accent="#0969da")
    chiffres = [("6", "projets"), ("146", "tests verts"), ("0", "dépendance tierce")]
    blocs = []
    pas = largeur / len(chiffres)
    for index, (valeur, libelle) in enumerate(chiffres):
        x = pas * (index + 0.5)
        blocs.append(f'<text class="metric" x="{x:.0f}" y="50" text-anchor="middle">{valeur}</text>')
        blocs.append(f'<text class="unite" x="{x:.0f}" y="68" text-anchor="middle">{libelle}</text>')
        if index < len(chiffres) - 1:
            sep = pas * (index + 1)
            blocs.append(
                f'<line x1="{sep:.0f}" y1="26" x2="{sep:.0f}" y2="66" '
                'stroke="#d1d9e0" stroke-width="1" opacity="0.6"/>'
            )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{largeur}" height="{hauteur}" \
viewBox="0 0 {largeur} {hauteur}" role="img" aria-label="En bref">
  <style>{style}</style>
  <rect class="fond" x="0.5" y="0.5" width="{largeur - 1}" height="{hauteur - 1}" rx="10"/>
  {''.join(blocs)}
  <text class="pied" x="{largeur / 2:.0f}" y="88" text-anchor="middle">chaque chiffre est mesuré en exécutant le code</text>
</svg>
"""


def main() -> None:
    for donnees in CARTES:
        (SORTIE / donnees["fichier"]).write_text(carte(donnees), encoding="utf-8")
        print(f"  {donnees['fichier']}")
    (SORTIE / "en-bref.svg").write_text(bandeau(), encoding="utf-8")
    print("  en-bref.svg")
    print(f"{len(CARTES) + 1} cartes generees dans {SORTIE}")


if __name__ == "__main__":
    main()
