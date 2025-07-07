import subprocess
import time

# Chemin vers le script Python à exécuter
script_path = r".\example\newClient\main.py"

# Nombre d'instances à lancer
num_instances = 6

for i in range(1, num_instances + 1):
    client_name = f"Migroky_{i}"
    command = f'python {script_path} {client_name}'

    # Lance un nouveau terminal pour chaque commande
    subprocess.Popen(
        ["powershell", "-NoExit", "-Command", command],
        shell=True
    )
    time.sleep(0.1)  # Légère pause entre les lancements (facultatif)
