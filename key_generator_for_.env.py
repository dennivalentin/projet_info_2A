import secrets
import string


def generer_cle_securisee(longueur=32):
  # Définit les caractères utilisables (lettres, chiffres, symboles)
  alphabet = string.ascii_letters + string.digits + string.punctuation
  # Génère la clé
  cle = "".join(secrets.choice(alphabet) for _ in range(longueur))
  return cle


#  générer une clé de 32 caractères
print(generer_cle_securisee(32))
