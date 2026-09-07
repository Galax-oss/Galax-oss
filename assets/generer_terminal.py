"""Genere le terminal du profil, en SVG.

Pourquoi un SVG et pas un bloc de code Markdown. Un bloc de code rend bien le
monospace mais ne permet ni chrome de fenetre, ni couleur choisie, ni curseur
qui clignote. Ici la forme fait partie du propos : un profil de cybersecurite
qui se lit comme une session shell se distingue immediatement d'un profil a
badges, et il n'y a rien a comprendre avant de le lire.

Pourquoi un fichier du depot et pas un service tiers. github-readme-stats
rendait 503 au moment d'ecrire ces lignes. Un profil dont les visuels dependent
d'un service gratuit affiche des images cassees le jour ou ce service tombe.

Le terminal est volontairement sombre dans les deux themes : un terminal clair
n'existe pas dans l'imaginaire, et une fenetre qui change de peau perd ce
qu'elle raconte.

    python assets/generer_terminal.py
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

SORTIE = Path(__file__).parent

MONO = (
    "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
    "'Liberation Mono', monospace"
)

MARGE_X = 26
DEBUT_Y = 74
INTERLIGNE = 21
TAILLE = 13.5
LARGEUR = 880
CHROME = 42

FOND = "#0d1117"
BARRE = "#161b22"
BORDURE = "#30363d"

INVITE_UTILISATEUR = "#3fb950"
INVITE_CHEMIN = "#58a6ff"
COMMANDE = "#e6edf3"
SORTIE_TEXTE = "#8b949e"
NOM_PROJET = "#58a6ff"
CHIFFRE = "#e6edf3"
VERT = "#3fb950"
ORANGE = "#d29922"

INVITE = "victor@efrei"
CHEMIN = "~"

# Chaque entree : ("commande", "texte") ou ("sortie", [(couleur, texte), ...])
# ou ("vide", None). Les colonnes des projets sont alignees a la main parce
# qu'une police monospace le permet, et que c'est precisement l'effet cherche.
SESSION = [
    ("commande", "whoami"),
    ("sortie", [(COMMANDE, "Victor Norture"), (SORTIE_TEXTE, " - cybersécurité et réseaux")]),
    ("sortie", [(SORTIE_TEXTE, "Bachelor 3, EFREI Paris - Île-de-France")]),
    ("vide", None),

    ("commande", "cat objectif.txt"),
    ("sortie", [(SORTIE_TEXTE, "Alternance "), (COMMANDE, "2026-2027"),
                (SORTIE_TEXTE, " - administration systèmes et réseaux,")]),
    ("sortie", [(SORTIE_TEXTE, "sécurité opérationnelle, gestion des vulnérabilités")]),
    ("sortie", [(SORTIE_TEXTE, "Rythme  "), (COMMANDE, "1 semaine de formation / 2 semaines en entreprise")]),
    ("sortie", [(SORTIE_TEXTE, "Base    "), (COMMANDE, "Île-de-France"), (SORTIE_TEXTE, ", véhiculé")]),
    ("sortie", [(SORTIE_TEXTE, "Certifié "), (ORANGE, "Microsoft Azure AZ-900")]),
    ("vide", None),

    ("commande", "ls -1 projets/"),
    ("projet", ("kev-triage", "238 vulnérabilités ramenées à 14 à traiter")),
    ("projet", ("ios-config-audit", "16 écarts sur une configuration d'usine")),
    ("projet", ("azure-sftp-lab", "10 contrôles de sécurité après déploiement")),
    ("projet", ("linux-hardening-audit", "18 règles, sshd_config et sysctl")),
    ("projet", ("authlog-watch", "4 alertes, la compromission en tête")),
    ("projet", ("veille-certfr", "100 avis par mois ramenés à 3 lignes utiles")),
    ("vide", None),

    ("commande", "pytest -q --tb=no"),
    ("sortie", [(VERT, "146 passed"), (SORTIE_TEXTE, "  en 4.24s, sur les six projets")]),
    ("vide", None),

    ("commande", "contact --court"),
    ("sortie", [(SORTIE_TEXTE, "linkedin.com/in/victor-norture")]),
    ("sortie", [(SORTIE_TEXTE, "tryhackme.com/p/vnorture")]),
    ("vide", None),
]

LARGEUR_COLONNE = max(len(nom) for genre, valeur in SESSION
                      if genre == "projet" for nom, _ in [valeur]) + 3


def _empan(couleur: str, texte: str) -> str:
    return f'<tspan fill="{couleur}">{escape(texte)}</tspan>'


def _ligne_invite(y: int, commande: str) -> str:
    return (
        f'<text x="{MARGE_X}" y="{y}" class="mono">'
        f'{_empan(INVITE_UTILISATEUR, INVITE)}'
        f'{_empan(SORTIE_TEXTE, ":")}'
        f'{_empan(INVITE_CHEMIN, CHEMIN)}'
        f'{_empan(SORTIE_TEXTE, "$ ")}'
        f'{_empan(COMMANDE, commande)}'
        "</text>"
    )


def terminal() -> str:
    lignes: list[str] = []
    y = DEBUT_Y

    for genre, valeur in SESSION:
        if genre == "vide":
            y += INTERLIGNE
            continue
        if genre == "commande":
            lignes.append(_ligne_invite(y, valeur))
        elif genre == "sortie":
            empans = "".join(_empan(couleur, texte) for couleur, texte in valeur)
            lignes.append(f'<text x="{MARGE_X}" y="{y}" class="mono">{empans}</text>')
        elif genre == "projet":
            nom, resume = valeur
            rembourrage = " " * (LARGEUR_COLONNE - len(nom))
            lignes.append(
                f'<text x="{MARGE_X}" y="{y}" class="mono">'
                f'{_empan(NOM_PROJET, nom)}'
                f'{_empan(SORTIE_TEXTE, rembourrage + resume)}'
                "</text>"
            )
        y += INTERLIGNE

    # Derniere invite, avec le curseur qui clignote. Un seul element anime :
    # deux, et la page devient une vitrine.
    lignes.append(_ligne_invite(y, ""))
    decalage = MARGE_X + len(f"{INVITE}:{CHEMIN}$ ") * TAILLE * 0.6
    lignes.append(
        f'<rect x="{decalage:.0f}" y="{y - 11}" width="8" height="15" fill="{COMMANDE}">'
        '<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" repeatCount="indefinite"/>'
        "</rect>"
    )
    hauteur = y + 28

    points = "".join(
        f'<circle cx="{x}" cy="21" r="6" fill="{couleur}"/>'
        for x, couleur in ((26, "#ff5f57"), (48, "#febc2e"), (70, "#28c840"))
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{LARGEUR}" height="{hauteur}" \
viewBox="0 0 {LARGEUR} {hauteur}" role="img" \
aria-label="Session terminal de Victor Norture, profil et projets">
  <style>
    .mono {{ font: 400 {TAILLE}px {MONO}; white-space: pre; }}
    .titre {{ font: 400 12px {MONO}; fill: {SORTIE_TEXTE}; }}
  </style>
  <rect x="0.5" y="0.5" width="{LARGEUR - 1}" height="{hauteur - 1}" rx="10"
        fill="{FOND}" stroke="{BORDURE}"/>
  <path d="M0.5 10.5 a10 10 0 0 1 10 -10 h{LARGEUR - 21} a10 10 0 0 1 10 10 v{CHROME - 10} h-{LARGEUR - 1} z"
        fill="{BARRE}" stroke="{BORDURE}"/>
  {points}
  <text x="{LARGEUR / 2}" y="26" text-anchor="middle" class="titre">{INVITE}: {CHEMIN}</text>
  {chr(10).join('  ' + l for l in lignes)}
</svg>
"""


def main() -> None:
    chemin = SORTIE / "terminal.svg"
    chemin.write_text(terminal(), encoding="utf-8")
    print(f"{chemin.name} genere, {len(chemin.read_text(encoding='utf-8'))} octets")


if __name__ == "__main__":
    main()
