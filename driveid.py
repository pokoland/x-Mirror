import os
import re
print("\n\n"\
      "        Le bot peut rechercher des fichiers de manière récursive, mais vous devez ajouter la liste des drives à rechercher.\n"\
      "        Utilisez le format suivant : (Vous pouvez utiliser 'root' comme ID si vous souhaitez utiliser le drive principal.)\n"\
      "        teamdrive NOM      -->   ce que vous voulez, un nom personnalisé\n"\
      "        teamdrive ID       -->   id des teamdrives que vous souhaitez rechercher ('root' pour le drive principal)\n"\
      "        teamdrive INDEX URL -->  entrez l'URL d'index pour ce drive.\n" \
      "                                  allez sur le drive concerné et copiez l'URL depuis la barre d'adresse\n")
msg = ''
if os.path.exists('drive_folder'):
    with open('drive_folder', 'r+') as f:
        lines = f.read()
    if not re.match(r'^\s*$', lines):
        print(lines)
        print("\n\n"\
              "      SOUHAITEZ-VOUS GARDER LES INFORMATIONS CI-DESSUS QUE VOUS AVEZ AJOUTÉES PRÉCÉDEMMENT ? ENTREZ (o/n)\n"\
              "      SI RIEN N'APPARAÎT, ENTREZ n")
        while 1:
            choice = input()
            if choice in ['o', 'O']:
                msg = f'{lines}'
                break
            elif choice in ['n', 'N']:
                break
            else:
                print("\n\n      SOUHAITEZ-VOUS GARDER LES INFORMATIONS CI-DESSUS ? o/n <=== ceci est une option... OUVREZ LES YEUX & LISEZ...")
num = int(input("    Combien de Drive/Dossier souhaitez-vous ajouter : "))
for count in range(1, num + 1):
    print(f"\n        > DRIVE - {count}\n")
    name  = input("    Entrez le NOM du Drive  (n'importe quoi)     : ")
    id    = input("    Entrez l'ID du Drive                        : ")
    index = input("    Entrez l'URL d'INDEX du Drive (optionnel)   : ")
    if not name or not id:
        print("\n\n        ERREUR : Ne laissez pas le nom/l'id vide.")
        exit(1)
    name=name.replace(" ", "_")
    if index:
        if index[-1] == "/":
            index = index[:-1]
    else:
        index = ''
    msg += f"{name} {id} {index}\n"
with open('drive_folder', 'w') as file:
    file.truncate(0)
    file.write(msg)
print("\n\n    Terminé !")
