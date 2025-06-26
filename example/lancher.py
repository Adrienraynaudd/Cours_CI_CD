import subprocess

# Chemin vers le script Python à exécuter
script_path = r".\example\client.py"

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
