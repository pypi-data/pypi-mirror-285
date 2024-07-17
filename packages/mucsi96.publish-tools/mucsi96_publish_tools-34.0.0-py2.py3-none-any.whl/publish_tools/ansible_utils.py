from os import makedirs, path
from pathlib import Path
from secrets import choice
from string import ascii_letters, digits
from typing import cast
from ansible.parsing.vault import VaultSecret
from ansible.parsing.dataloader import DataLoader


def load_vars(vault_secret: str, vars_file: Path) -> dict[str, str]:
    loader = DataLoader()
    loader.set_vault_secrets(
        [('default', VaultSecret(vault_secret.encode()))])
    return cast(dict[str, str], loader.load_from_file(str(vars_file)))


def create_vault_key(vault_secret_file: Path):
    makedirs(path.dirname(vault_secret_file), exist_ok=True)

    if path.exists(vault_secret_file):
        raise Exception(f"The file '{vault_secret_file}' already exists.")

    alphabet = ascii_letters + digits + r"""#%*+,-.=?@[\]^_{}~"""
    password = ''.join(choice(alphabet) for i in range(50))
    with open(vault_secret_file, 'w') as file:
        file.write(password)
