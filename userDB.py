import db
from datetime import datetime, time
import utils

def getUserByEmail(email):
    """Récupère un utilisateur en fonction de son email."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM client WHERE email = %s""",(email,))
            return cur.fetchall()

def getAllCodeVille():
    """Récupère tous les codes postaux et noms des villes."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT codePostal, nom FROM ville""")
            villes = cur.fetchall()
            return villes

def ajouteVille(codePostal, nom):
    """Ajoute une nouvelle ville à la base de données si elle n'existe pas."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT 1 FROM ville WHERE codePostal = %s""", (codePostal,))
            if not cur.fetchone():  # Vérifie si la ville existe déjà
                cur.execute("""INSERT INTO ville(codePostal,nom) VALUES (%s,%s)""", (codePostal, nom))
                conn.commit()


def ajouterVilleTravail(matricule, codePostal):
    """Ajoute une ville où un livreur travaille, en évitant les doublons."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO travaille (matricule, codePostal) VALUES (%s, %s) ON CONFLICT DO NOTHING
            """, (matricule, codePostal))
            conn.commit()

def getVillesCouvreesParLivreur(matricule):
    """Récupère les villes couvertes par un livreur donné."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT v.nom, v.codePostal FROM ville v JOIN travaille t ON v.codePostal = t.codePostal
                WHERE t.matricule = %s""", (matricule,))
            villes = cur.fetchall()
            return villes

def inscritClient(nom,prenom,numtel,codepostal,adresse,email,mdp,parrain = None):
    """Ajoute un nouveau client à la base de données, avec un parrain optionnel."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO client(nom,prenom,numtel,codepostal,adresse,email,mdp,idParrain) VALUES(
                        %s,%s,%s,%s,%s,%s,%s,%s)""",(nom,prenom,numtel,codepostal,adresse,email,mdp,parrain,))
  
def getUserByIdClient(idClient):
    """Récupère un utilisateur client en fonction de son ID."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM client WHERE idClient = %s""",(idClient,))
            client = cur.fetchone()
            if not client:
                return False
            return client

def GetAllCommandeOfClient(idClient):
    """Récupère toutes les commandes passées par un client donné."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.idComm, c.statut, c.montant_total, c.idRest, r.nom FROM commande c
                JOIN restaurant r ON c.idRest = r.idRest WHERE c.idClient = %s""", (idClient,))
            commandes = cur.fetchall()
            return commandes

def getAllRestaurantsOuvert():
    """Récupère tous les restaurants ouverts avec leurs informations et notes moyennes."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.idRest, r.nom, r.adresse, r.statut, r.frais_prise_en_charge,
                       r.codePostal, COALESCE(ROUND(AVG(n.note), 1), 0) AS note_moyenne,
                       r.photo
                FROM restaurant r
                LEFT JOIN noter n ON r.idRest = n.idRest
                WHERE r.statut = 'Ouvert'
                GROUP BY r.idRest
            """)
            return cur.fetchall()


def getRestaurantsById(idRest):
    """Récupère les informations d'un restaurant donné par son ID."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM restaurant WHERE idRest = %s""",(idRest,))
            restaurant = cur.fetchone()
            return restaurant

def getPlatsByIdRest(IdRest):
    """Récupère les plats associés à un restaurant donné."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT idCarte FROM restaurant WHERE idRest = %s""", (IdRest,))
            carte = cur.fetchone()
            idCarte = carte[0]
            cur.execute("""SELECT p.idplat, p.nom, p.prix, p.description, p.photo FROM plats p
                JOIN propose pr ON p.idPlat = pr.idPlat WHERE pr.idCarte = %s""", (idCarte,))
            plats = cur.fetchall()
            return plats
       
def getPlatsByCommande(idComm):
    """Récupère les plats associés à une commande spécifique."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.nom, p.prix, co.quantite FROM contient co
                JOIN plats p ON co.idPlat = p.idPlat WHERE co.idComm = %s """, (idComm,))
            plats = cur.fetchall()
            return plats

def getNoteMoyenneByIdRest(idRest):
    """Calcule la note moyenne d'un restaurant donné."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ROUND(AVG(note), 1) FROM noter WHERE idRest = %s """, (idRest,))
            note_moyenne = cur.fetchone()
            return note_moyenne[0] if note_moyenne and note_moyenne[0] is not None else 0.0

def getHoraires(idRest):
    """Récupère les horaires d'ouverture d'un restaurant pour le jour actuel."""
    jour_actuel = datetime.now().strftime('%A')
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT heureDebut, heureFin FROM horaire h JOIN est_ouvert eo ON h.idH = eo.idH
                        WHERE eo.idRest = %s AND h.jour = %s""", (idRest, jour_actuel))
            horaires = cur.fetchone()
            if not horaires:
                return None
            return f"{horaires[0]} - {horaires[1]}"

def getMotClesByIdRest(idRest):
    """Récupère les mots-clés associés à un restaurant donné."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT mc.libelle FROM motCle mc WHERE mc.idRest = %s """, (idRest,))
            mots_cles = cur.fetchall()
            return [mot[0] for mot in mots_cles] 

def getCardByNumberAndCodeSecretAndDate(numero,hashed_code,date):
    """Récupère une carte bancaire en fonction de son numéro, code secret et date d'expiration."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM carteBancaire WHERE numero_carte = %s AND 
                        code_secret = %s AND date_expiration = %s""",(numero,hashed_code,date))
            carte = cur.fetchone()
            return carte
        
def ajouteNouvelleCarte(numero, code_secret, date_exp, id_client, proprietaire):
    """Ajoute une nouvelle carte bancaire pour un client."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO carteBancaire (numero_carte, code_secret, date_expiration, idclient, proprietaire)
                VALUES (%s, %s, %s, %s, %s)""", (numero, code_secret, date_exp, id_client, proprietaire))
            conn.commit()


def ajouteCommande(prix, idClient, matricule, idRest):
    """Ajoute une commande pour un client, avec mise à jour des points de fidélité pour un éventuel parrain."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO commande (statut, montant_total, idRest, matricule, idClient) VALUES (%s, %s, %s, %s, %s)
                RETURNING idComm; """, ("En attente", prix, idRest, matricule, idClient))
            id_commande = cur.fetchone()[0]
            print("Commande insérée avec ID :", id_commande)
            cur.execute("""SELECT idParrain FROM client WHERE idClient = %s """, (idClient,))
            parrain = cur.fetchone()
            print("ID Parrain récupéré :", parrain)
            if parrain and parrain[0]: 
                cur.execute("""UPDATE client SET points_fidelite = points_fidelite + %s
                    WHERE idClient = %s""", (prix, parrain[0]))
                print("Points ajoutés au parrain ID :", parrain[0])
            conn.commit()
            return id_commande

def ajoutePlatsCommande(id_commande, panier):
    """Ajoute les plats d'une commande à la table `contient`."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            for item in panier:
                cur.execute("""INSERT INTO contient (idPlat, idComm, quantite) VALUES (%s, %s, %s)
                """, (item['idPlat'], id_commande, item['quantity']))
            conn.commit()

def getIdPlatByName(nom_plat):
    """Récupère l'ID d'un plat en fonction de son nom."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT idPlat FROM plats WHERE nom = %s", (nom_plat,))
            id_plat = cur.fetchone()
            return id_plat[0] if id_plat else None

def getFraisLivraison(id_restaurant):
    """Récupère les frais de livraison pour un restaurant donné."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT frais_prise_en_charge FROM restaurant WHERE idRest = %s", (id_restaurant,))
            frais = cur.fetchone()
            return frais[0] if frais else 0

def getLivreurByNomAndPrenomAndNumAndPassword(nom,prenom,numtel,mdp):
    """Récupère un livreur à partir de son nom, prénom, numéro de téléphone et mot de passe."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM livreur WHERE nom=%s AND prenom=%s AND numtel=%s AND mdp=%s""",(nom,prenom,numtel,mdp))
            livreur = cur.fetchall()
            return livreur

def getAllMatricule():
    """Récupère tous les matricules des livreurs existants."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT matricule FROM livreur""")
            result = cur.fetchall()
            return [row[0] for row in result] if result else []


def getLivreurByMatriculeAndMdp(Matricule,mdp):
    """Récupère un livreur en fonction de son matricule et mot de passe."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM livreur WHERE matricule = %s AND mdp = %s""",(Matricule,mdp))
            livreur = cur.fetchall()
            return livreur

def getLivreurByMatricule(matricule):
    """Récupère un livreur à partir de son matricule."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM livreur WHERE matricule = %s""",(matricule,))
            livreur = cur.fetchone()
            return livreur

def getAllCommande():
    """Récupère toutes les commandes de la table commande."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM commande""")
            commandes = cur.fetchall()
            return commandes      

def updateLivreurStatut(matricule,statut):
    """Met à jour le statut d'un livreur (ex: Disponible, Indisponible)."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""UPDATE livreur SET statut = %s WHERE matricule = %s""",(statut,matricule))
        
def inscritLivreur(nom,prenom,numtel,hashed_password):
    """Inscrit un nouveau livreur en générant un matricule unique."""
    matricule = str(utils.genererMatricule())
    lst_matricules = getAllMatricule()
    while True:
        if matricule in lst_matricules:
            matricule = str(utils.genererMatricule())
        else:
            break
        
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO livreur(matricule,nom,prenom,numTel,mdp,statut) VALUES(%s,%s,%s,%s,
                        %s,%s)""",(matricule,nom,prenom,numtel,hashed_password,"Indisponible"))

def annulerCommande(idComm):
    """Annule une commande en mettant à jour son statut à 'Annulée'."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE commande SET statut = 'Annulée' WHERE idComm = %s """, (idComm,))
            conn.commit()

def getCommandesDisponiblesPourLivreur(matricule):
    """Récupère les commandes disponibles pour un livreur en fonction de ses villes de travail."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.idComm, c.statut, c.montant_total, r.nom AS restaurant,
                       cl.nom AS client_nom, cl.prenom AS client_prenom
                FROM commande c
                JOIN restaurant r ON c.idRest = r.idRest
                JOIN client cl ON c.idClient = cl.idClient
                JOIN travaille t1 ON t1.codePostal = r.codePostal
                JOIN travaille t2 ON t2.codePostal = cl.codePostal
                WHERE t1.matricule = t2.matricule
                  AND t1.matricule = %s
                  AND c.statut = 'En attente';""", (matricule,))
            commandes = cur.fetchall()
        commandes_detaillees = []
        for commande in commandes:
            plats = getPlatsByCommande(commande[0])  
            commandes_detaillees.append({"idCommande": commande[0], "statut": commande[1], "montant_total": commande[2],
                "restaurant": commande[3], "client": f"{commande[4]} {commande[5]}", "plats": plats})
        return commandes_detaillees

def retirerVilleTravail(matricule, codePostal):
    """Supprime une association entre un livreur et une ville de travail."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""DELETE FROM travaille WHERE matricule = %s AND codePostal = %s""", (matricule, codePostal))
            conn.commit()

def affecterCommandeAuLivreur(idComm, matricule):
    """Affecte une commande à un livreur et change son statut à 'Livrée'."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""UPDATE commande SET matricule = %s, statut = 'Livrée' WHERE idComm = %s """, (matricule, idComm))
            conn.commit()

def ajouterVilleTravail(matricule, codePostal):
    """Ajoute une nouvelle ville de travail à un livreur."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO travaille (matricule, codePostal) VALUES (%s, %s)
                ON CONFLICT DO NOTHING """, (matricule, codePostal))
            conn.commit()

def mettre_a_jour_statut_restaurants():
    """Met à jour le statut des restaurants en fonction de leurs horaires et des fermetures exceptionnelles."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""UPDATE restaurant SET statut = 'Fermé'""")
             #fermeture exceptionnelle
            cur.execute("""UPDATE restaurant SET statut = 'Fermé'
                           WHERE idRest IN ( SELECT idRest FROM fermetureExceptionnelle 
                           WHERE CURRENT_DATE BETWEEN date_debut AND date_fin)""")
            #horaires 
            cur.execute("""UPDATE restaurant SET statut = 'Ouvert'
                            WHERE idRest IN (
                            SELECT eo.idRest FROM est_ouvert eo
                            JOIN horaire h ON eo.idH = h.idH
                            WHERE CURRENT_TIME BETWEEN h.heureDebut AND h.heureFin
                            AND h.jour = TO_CHAR(CURRENT_DATE, 'FMDay'))
                        AND idRest NOT IN (
                        SELECT idRest
                            FROM fermetureExceptionnelle
                            WHERE CURRENT_DATE BETWEEN date_debut AND date_fin)""")
            conn.commit()
        
def rechercher_restaurants(nom_ou_mot_cle=None, frais_max=None, code_postal=None, note_min=None):
    """Recherche des restaurants ouverts en fonction de plusieurs critères :
    - nom ou mot-clé
    - frais de prise en charge maximum
    - code postal
    - note minimale
    """
    with db.connect() as connexion:
        with connexion.cursor() as curseur:
            requete_sql = """
                SELECT DISTINCT r.idRest, r.nom, r.adresse, r.statut, r.frais_prise_en_charge,
                                r.codepostal, r.idcarte, r.photo, COALESCE(AVG(n.note), 0) AS note_moyenne
                FROM restaurant r
                LEFT JOIN noter n ON r.idRest = n.idRest
                LEFT JOIN motCle mc ON r.idRest = mc.idRest
                WHERE r.statut = 'Ouvert'
            """
            valeurs = []

            if nom_ou_mot_cle:
                requete_sql += " AND (LOWER(r.nom) LIKE %s OR LOWER(mc.libelle) LIKE %s)"
                valeurs.append(f"%{nom_ou_mot_cle}%")
                valeurs.append(f"%{nom_ou_mot_cle}%")

            if frais_max is not None:
                requete_sql += " AND r.frais_prise_en_charge <= %s"
                valeurs.append(frais_max)

            if code_postal:
                requete_sql += " AND r.codePostal = %s"
                valeurs.append(code_postal)

            requete_sql += " GROUP BY r.idRest"

            if note_min is not None:
                requete_sql += " HAVING COALESCE(AVG(n.note), 0) >= %s"
                valeurs.append(note_min)

            curseur.execute(requete_sql, tuple(valeurs))
            return curseur.fetchall()


def enregistrer_note(id_rest, id_client, id_commande, note, commentaire):
    """Enregistre une note et un commentaire pour un restaurant. 
    Met à jour la note si le client a déjà noté ce restaurant."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO noter (idRest, idClient, idComm, note, commentaire)
                VALUES (%s, %s, %s, %s, %s) ON CONFLICT (idRest, idClient)
                DO UPDATE SET note = EXCLUDED.note, commentaire = EXCLUDED.commentaire;
            """, (id_rest, id_client, id_commande, note, commentaire))
            conn.commit()

def getIdRestFromCommande(id_commande):
    """Récupère l'ID d'un restaurant à partir d'une commande spécifique."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT idRest FROM commande WHERE idComm = %s """, (id_commande,))
            result = cur.fetchone()
            return result[0] if result else None

def ajouterParrain(id_client, id_parrain):
    """Associe un parrain à un client s'il n'a pas déjà de parrain."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""UPDATE client SET idParrain = %s WHERE idClient = %s AND idParrain IS NULL """, (id_parrain, id_client))
            conn.commit()

def getPointsFidelite(idClient):
    """Récupère le nombre de points de fidélité d'un client donné."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT points_fidelite FROM client WHERE idClient = %s """, (idClient,))
            result = cur.fetchone()
            return result[0] if result else 0
        
def supprimerClient(idClient):
    """Supprime un client de la base de données."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""DELETE FROM client WHERE idClient = %s""", (idClient,))
            conn.commit()

def supprimerLivreur(matricule):
    """Supprime un livreur de la base de données."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""DELETE FROM livreur WHERE matricule = %s""", (matricule,))
            conn.commit()


def getAllNotesByIdRest(idRest):
    """Récupère toutes les notes et commentaires pour un restaurant donné."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.nom, c.prenom, n.note, n.commentaire
                FROM noter n
                JOIN client c ON n.idClient = c.idClient
                WHERE n.idRest = %s
            """, (idRest,))
            return cur.fetchall()
