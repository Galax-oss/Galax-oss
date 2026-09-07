"""Genere la console du profil, en SVG.

Pourquoi un SVG et pas un bloc de code Markdown. Un bloc de code rend bien le
monospace mais ne permet ni couleur choisie, ni barre d'etat, ni curseur qui
clignote. Ici la forme fait partie du propos : un profil de cybersecurite qui
se lit comme une session shell se distingue d'un profil a badges, et il n'y a
rien a comprendre avant de le lire.

Pourquoi un fichier du depot et pas un service tiers. github-readme-stats
rendait 503 au moment d'ecrire ces lignes. Un profil dont les visuels dependent
d'un service gratuit affiche des images cassees le jour ou ce service tombe.

Pas de chrome de fenetre. Les trois pastilles rondes sont une convention macOS,
et elles situaient la scene au mauvais endroit. C'est une console Linux, avec
sa barre d'etat tmux en bas : le detail que seul quelqu'un qui vit dans un
terminal ajoute.

Le fond reste sombre dans les deux themes. Un terminal clair n'existe pas dans
l'imaginaire, et une fenetre qui change de peau perd ce qu'elle raconte.

    python assets/generer_console.py
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

SORTIE = Path(__file__).parent

MONO = (
    "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
    "'Liberation Mono', monospace"
)

LARGEUR = 880
MARGE_X = 24
DEBUT_Y = 38
INTERLIGNE = 21
TAILLE = 13.5
HAUTEUR_STATUT = 26

FOND = "#0d1117"
BORDURE = "#30363d"

INVITE_UTILISATEUR = "#3fb950"
INVITE_CHEMIN = "#58a6ff"
COMMANDE = "#e6edf3"
TEXTE = "#8b949e"
NOM_PROJET = "#58a6ff"
VERT = "#3fb950"
ORANGE = "#d29922"

# tmux par defaut : fond vert, texte sombre, fenetre active en clair.
STATUT_FOND = "#2f6f3e"
STATUT_TEXTE = "#0d1117"
STATUT_ACTIF = "#f0f6fc"

INVITE = "victor@srv-efrei"
CHEMIN = "~"

SESSION = [
    ("commande", "whoami"),
    ("sortie", [(COMMANDE, "Victor Norture"), (TEXTE, " - cybersécurité et réseaux")]),
    ("sortie", [(TEXTE, "Bachelor 3, EFREI Paris - Île-de-France")]),
    ("vide", None),

    ("commande", "cat objectif.txt"),
    ("sortie", [(TEXTE, "Alternance "), (COMMANDE, "2026-2027"),
                (TEXTE, " - administration systèmes et réseaux,")]),
    ("sortie", [(TEXTE, "sécurité opérationnelle, gestion des vulnérabilités")]),
    ("sortie", [(TEXTE, "Rythme    "), (COMMANDE, "1 semaine de formation / 2 semaines en entreprise")]),
    ("sortie", [(TEXTE, "Base      "), (COMMANDE, "Île-de-France"), (TEXTE, ", véhiculé")]),
    ("sortie", [(TEXTE, "Certifié  "), (ORANGE, "Microsoft Azure AZ-900")]),
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
    ("sortie", [(VERT, "146 passed"), (TEXTE, "  en 4.24s, sur les six projets")]),
    ("vide", None),

    ("commande", "contact"),
    ("sortie", [(TEXTE, "linkedin.com/in/victor-norture")]),
    ("sortie", [(TEXTE, "tryhackme.com/p/vnorture")]),
    ("vide", None),
]

LARGEUR_COLONNE = max(
    len(nom) for genre, valeur in SESSION if genre == "projet" for nom, _ in [valeur]
) + 3


def _empan(couleur: str, texte: str) -> str:
    return f'<tspan fill="{couleur}">{escape(texte)}</tspan>'


def _invite(y: int, commande: str) -> str:
    return (
        f'<text x="{MARGE_X}" y="{y}" class="mono">'
        f'{_empan(INVITE_UTILISATEUR, INVITE)}'
        f'{_empan(TEXTE, ":")}'
        f'{_empan(INVITE_CHEMIN, CHEMIN)}'
        f'{_empan(TEXTE, "$ ")}'
        f'{_empan(COMMANDE, commande)}'
        "</text>"
    )


def console() -> str:
    lignes: list[str] = []
    y = DEBUT_Y

    for genre, valeur in SESSION:
        if genre == "vide":
            y += INTERLIGNE
            continue
        if genre == "commande":
            lignes.append(_invite(y, valeur))
        elif genre == "sortie":
            empans = "".join(_empan(couleur, texte) for couleur, texte in valeur)
            lignes.append(f'<text x="{MARGE_X}" y="{y}" class="mono">{empans}</text>')
        elif genre == "projet":
            nom, resume = valeur
            rembourrage = " " * (LARGEUR_COLONNE - len(nom))
            lignes.append(
                f'<text x="{MARGE_X}" y="{y}" class="mono">'
                f'{_empan(NOM_PROJET, nom)}'
                f'{_empan(TEXTE, rembourrage + resume)}'
                "</text>"
            )
        y += INTERLIGNE

    # Derniere invite, avec le curseur qui clignote. Un seul element anime :
    # deux, et la page devient une vitrine.
    lignes.append(_invite(y, ""))
    decalage = MARGE_X + len(f"{INVITE}:{CHEMIN}$ ") * TAILLE * 0.6
    lignes.append(
        f'<rect x="{decalage:.0f}" y="{y - 11}" width="8" height="15" fill="{COMMANDE}">'
        '<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" repeatCount="indefinite"/>'
        "</rect>"
    )

    haut_statut = y + 16
    hauteur = haut_statut + HAUTEUR_STATUT

    statut = (
        f'<rect x="1" y="{haut_statut}" width="{LARGEUR - 2}" height="{HAUTEUR_STATUT - 1}" '
        f'fill="{STATUT_FOND}"/>'
        f'<text x="14" y="{haut_statut + 17}" class="mono" fill="{STATUT_TEXTE}">[victor]</text>'
        f'<text x="90" y="{haut_statut + 17}" class="mono" fill="{STATUT_ACTIF}">0:bash*</text>'
        f'<text x="166" y="{haut_statut + 17}" class="mono" fill="{STATUT_TEXTE}">'
        f'1:projets-  2:veille-</text>'
        f'<text x="{LARGEUR - 14}" y="{haut_statut + 17}" text-anchor="end" class="mono" '
        f'fill="{STATUT_TEXTE}">"srv-efrei"  08 sept. 2026</text>'
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{LARGEUR}" height="{hauteur}" \
viewBox="0 0 {LARGEUR} {hauteur}" role="img" \
aria-label="Console de Victor Norture : profil, projets et resultats de tests">
  <style>
    .mono {{ font: 400 {TAILLE}px {MONO}; white-space: pre; }}
  </style>
  <rect x="0.5" y="0.5" width="{LARGEUR - 1}" height="{hauteur - 1}" rx="6"
        fill="{FOND}" stroke="{BORDURE}"/>
{chr(10).join('  ' + ligne for ligne in lignes)}
  {statut}
</svg>
"""


def main() -> None:
    chemin = SORTIE / "console.svg"
    chemin.write_text(console(), encoding="utf-8")
    print(f"{chemin.name} genere, {len(chemin.read_text(encoding='utf-8'))} octets")


if __name__ == "__main__":
    main()
