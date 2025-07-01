from __future__ import print_function
from google.oauth2.service_account import Credentials
import googleapiclient.discovery, json, progress.bar, glob, sys, argparse, time
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os, pickle

stt = time.time()

parse = argparse.ArgumentParser(
    description='Un outil pour ajouter des comptes de service à un drive partagé à partir d\'un dossier contenant des fichiers d\'identifiants.')
parse.add_argument('--path', '-p', default='accounts',
                   help='Spécifier un chemin alternatif vers le dossier des comptes de service.')
parse.add_argument('--credentials', '-c', default='./credentials.json',
                   help='Spécifier le chemin relatif du fichier credentials.')
parse.add_argument('--yes', '-y', default=False, action='store_true', help='Ignore la demande de confirmation.')
parsereq = parse.add_argument_group('arguments requis')
parsereq.add_argument('--drive-id', '-d', help='ID du Drive Partagé.', required=True)

args = parse.parse_args()
acc_dir = args.path
did = args.drive_id
credentials = glob.glob(args.credentials)

try:
    open(credentials[0], 'r')
    print('>> Identifiants trouvés.')
except IndexError:
    print('>> Aucun identifiant trouvé.')
    sys.exit(0)

if not args.yes:
    input('>> Assurez-vous que le **compte Google** ayant généré credentials.json\n   a été ajouté à votre Drive partagé '
          'en tant que Gestionnaire\n>> (Appuyez sur une touche pour continuer)')

creds = None
if os.path.exists('token_sa.pickle'):
    with open('token_sa.pickle', 'rb') as token:
        creds = pickle.load(token)
# Si aucun identifiant (valide) n’est disponible, demander à l’utilisateur de se connecter.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(credentials[0], scopes=[
            'https://www.googleapis.com/auth/admin.directory.group',
            'https://www.googleapis.com/auth/admin.directory.group.member'
        ])
        creds = flow.run_console()
    # Sauvegarder les identifiants pour la prochaine exécution
    with open('token_sa.pickle', 'wb') as token:
        pickle.dump(creds, token)

drive = googleapiclient.discovery.build("drive", "v3", credentials=creds)
batch = drive.new_batch_http_request()

aa = glob.glob('%s/*.json' % acc_dir)
pbar = progress.bar.Bar("Préparation des comptes", max=len(aa))
for i in aa:
    ce = json.loads(open(i, 'r').read())['client_email']
    batch.add(drive.permissions().create(fileId=did, supportsAllDrives=True, body={
        "role": "organizer",
        "type": "user",
        "emailAddress": ce
    }))
    pbar.next()
pbar.finish()
print('Ajout en cours...')
batch.execute()

print('Terminé.')
hours, rem = divmod((time.time() - stt), 3600)
minutes, sec = divmod(rem, 60)
print("Temps écoulé :\n{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), sec))
