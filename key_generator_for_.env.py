import secrets
import string


def generer_cle_securisee(longueur):
    # Définit les caractères utilisables (lettres, chiffres, symboles)
    alphabet = string.ascii_letters
    # Génère la clé
    cle = "".join(secrets.choice(alphabet) for _ in range(longueur))
    return cle


#  générer une clé de 64 caractères
print(generer_cle_securisee(64))
