from flask import Flask,render_template, request, redirect, url_for, session, flash, Response
import utils
import userDB
import db
from passlib.context import CryptContext
from datetime import datetime
password_ctx = CryptContext(schemes=['bcrypt'], deprecated="auto")

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
#pour que a chaque fois on relance le site on dois se connecté 
app.config['SESSION_PERMANENT'] = False 
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  
app.config['SESSION_COOKIE_HTTPONLY'] = True  


#*********************************Accueil****************************************
#accueil
@app.route("/")
def home():
    session.clear()
    return render_template("accueil.html")

@app.route("/accueil")
def accueil():
    return render_template("accueil.html")

#***********************************Client***************************************
#connexion
@app.route("/connexion")
def connexion():
    return render_template("connexion.html")

@app.route("/api/connexion", methods=['POST'])
def api_connexion():
    email = request.form.get("email")
    mdp = request.form.get("mdp")
    utilisateur = userDB.getUserByEmail(email)
    if utilisateur:
        hashed_password = utilisateur[0][5]  
        if password_ctx.verify(mdp, hashed_password):
            session['user_id'] = utilisateur[0][0]
            session['role'] = 'client' 
            session['logged_in'] = True
            return redirect("/accueil")
    flash("Email ou mot de passe invalide.")
    return redirect("/connexion")

#inscription
@app.route("/inscription")
def inscription():
    return render_template("inscription.html")

@app.route("/api/inscription", methods=['POST'])
def api_inscription():
    """ajouter un compte a la base de donnees"""
    nom_i = request.form.get("nom")
    prenom_i = request.form.get("prenom")
    numtel_i = request.form.get("numTel")
    codepostal_i = request.form.get("codePostal")
    ville_i = request.form.get("ville").strip().lower() 
    adresse_i = request.form.get("adresse")
    email_i = request.form.get("email")
    mdp_i = request.form.get("mdp")
    if not nom_i or not prenom_i:
        flash("Veuillez saisir un nom et prénoms valide.")
        return redirect("/inscription")
    if not numtel_i or not utils.isValidNumber(numtel_i):
        flash("Veuillez saisir un numéro de téléphone valide.")
        return redirect("/inscription")
    if not utils.isValidCodePostal(codepostal_i) or not codepostal_i:
        flash("Veuillez saisir un code postal valide.")
        return redirect("/inscription")
    if not ville_i:
        flash("Veuillez saisir le nom de la ville !")
        return redirect("/inscription")
    if (codepostal_i, ville_i) not in userDB.getAllCodeVille():
        userDB.ajouteVille(codepostal_i, ville_i)
    if not utils.isValidEmail(email_i) or not email_i:
        flash("Veuillez saisir un email valide.")
        return redirect("/inscription")
    if userDB.getUserByEmail(email_i):
        flash("Email déjà utilisé ! Saisissez un autre.")
        return redirect("/inscription")
    if not mdp_i or not utils.isValidPassword(mdp_i):
        flash("Saisissez un mot de passe valide.")
        return redirect("/inscription")
    hashed_password = password_ctx.hash(mdp_i)
    userDB.inscritClient(nom_i, prenom_i, numtel_i, codepostal_i, adresse_i, email_i, hashed_password)
    return redirect("/connexion")

#déconnexion
@app.route("/deconnexion")
def deconnexion():
    session.clear()  
    return redirect("/accueil")

#suppression de compte
@app.route("/supprimer_compte", methods=["POST"])
def supprimer_compte():
    if "user_id" not in session:
        flash("Veuillez vous connecter pour supprimer votre compte.")
        return redirect(url_for("connexion"))
    user_id = session["user_id"]
    role = session.get("role") 
    if role == "client":
        userDB.supprimerClient(user_id)
    elif role == "livreur":
        userDB.supprimerLivreur(user_id)
    else:
        flash("Rôle inconnu. Impossible de supprimer le compte.")
        return redirect(url_for("accueil"))
    session.clear() 
    flash("Votre compte a été supprimé avec succès.")
    return redirect(url_for("accueil"))

#profil
@app.route("/profil")
def profil_redirect():
    user_id = session.get("user_id") 
    if not user_id:
        flash("Veuillez vous connecter pour accéder à votre profil.")
        return redirect("/connexion")
    return redirect(url_for("profil", idClient=user_id))

@app.route("/profil/<int:idClient>")
def profil(idClient):
    client = userDB.getUserByIdClient(idClient)
    commandes = userDB.GetAllCommandeOfClient(idClient)
    points_fidelite = userDB.getPointsFidelite(idClient)
    commandes_details = []
    for commande in commandes:
        plats = userDB.getPlatsByCommande(commande[0])  
        commandes_details.append({"idComm": commande[0], "statut": commande[1], "montant_total": commande[2],
            "restaurant": commande[4], "plats": plats })
    return render_template("profil.html", client_p=client, commandes=commandes_details, points_fidelite=points_fidelite)

#ajouter une note
@app.route("/api/noter_commande", methods=["POST"])
def api_noter_commande():
    if "user_id" not in session:
        flash("Veuillez vous connecter pour noter une commande.")
        return redirect(url_for("connexion"))
    id_commande = request.form.get("idCommande")
    note = int(request.form.get("note")) 
    commentaire = request.form.get("commentaire")
    if not id_commande or not note:
        flash("Veuillez fournir une note et un commentaire.")
        return redirect(url_for("profil", idClient=session["user_id"]))
    id_rest = userDB.getIdRestFromCommande(id_commande)
    if not id_rest:
        flash("Impossible de trouver le restaurant pour cette commande.")
        return redirect(url_for("profil", idClient=session["user_id"]))
    userDB.enregistrer_note(id_rest, session["user_id"], id_commande, note, commentaire)
    flash("Votre note a été enregistrée avec succès.")
    return redirect(url_for("profil", idClient=session["user_id"]))

#ajouter un parrain
@app.route("/api/ajouter_parrain", methods=["POST"])
def ajouter_parrain():
    if "user_id" not in session:
        flash("Veuillez vous connecter pour ajouter un parrain.")
        return redirect(url_for("connexion"))
    email_parrain = request.form.get("email_parrain").strip().lower()
    id_client = session["user_id"]
    client = userDB.getUserByIdClient(id_client)
    if client and client[3].lower() == email_parrain: 
        flash("Vous ne pouvez pas être votre propre parrain.")
        return redirect(url_for("profil", idClient=id_client))
    parrain = userDB.getUserByEmail(email_parrain)
    if not parrain:
        flash("Aucun utilisateur trouvé avec cet email.")
        return redirect(url_for("profil", idClient=id_client))
    userDB.ajouterParrain(id_client, parrain[0][0]) 
    flash("Votre parrain a été ajouté avec succès.")
    return redirect(url_for("profil", idClient=id_client))

#annulation d'une commande qui est pas encore livrée
@app.route("/api/annuler_commande/<int:idComm>", methods=["POST"])
def annuler_commande(idComm):
    commandes = userDB.GetAllCommandeOfClient(session.get("user_id"))
    commande_annulable = next((cmd for cmd in commandes if cmd[0] == idComm and cmd[1] == "En attente"), None)
    if not commande_annulable:
        flash("Cette commande ne peut pas être annulée.")
        return redirect(url_for("profil", idClient=session.get("user_id")))
    userDB.annulerCommande(idComm)
    flash("Commande annulée avec succès.")
    return redirect(url_for("profil", idClient=session.get("user_id")))
#*********************************************restaurants**********************************************

#la liste des restaurants ouverts
@app.route("/restaurants")
def restaurants():
    userDB.mettre_a_jour_statut_restaurants()
    all_restaurants = userDB.getAllRestaurantsOuvert()
    print(all_restaurants)
    restaurants = [restaurant[:7] + (utils.decode_photo(restaurant[7]) if restaurant[7] else None,)
        for restaurant in all_restaurants]
    return render_template("restaurants.html", restaurants=restaurants)

#chercher un restaurant par rapport a : nom, mot clé, note, prix de prise en charge, code postal 
@app.route("/search", methods=["GET"])
def search_restaurants():
    nom_ou_mot_cle = request.args.get("query", "").strip().lower()
    frais_max = request.args.get("max_price", type=float)
    code_postal = request.args.get("location", "").strip()
    note_min = request.args.get("min_rating", type=float)
    restaurants = userDB.rechercher_restaurants(nom_ou_mot_cle=nom_ou_mot_cle,frais_max=frais_max,code_postal=code_postal,note_min=note_min)
    restaurants_modifies = [restaurant[:7] + (utils.decode_photo(restaurant[7]) if restaurant[7] else None,) +(userDB.getNoteMoyenneByIdRest(restaurant[0]),)for restaurant in restaurants]
    return render_template("restaurants.html", restaurants=restaurants_modifies)

#une page par restaurant
@app.route("/restaurants/<int:idRest>")
def page_restaurants(idRest):
    restaurant = userDB.getRestaurantsById(idRest)
    horaires = userDB.getHoraires(idRest)
    notes_clients = userDB.getAllNotesByIdRest(idRest)
    m = userDB.getMotClesByIdRest(idRest)
    mots_cles = ". ".join(m) if m else "Aucun mot-clé"
    chemin_photo = utils.decode_photo(restaurant[7])
    plats = userDB.getPlatsByIdRest(idRest)
    plats_decoded = []
    for plat in plats:
        print(plat)
        description = plat[3] if plat[3] else "Description non disponible"
        photo = utils.decode_photo(plat[4]) if plat[4] else None
        plats_decoded.append([plat[0], plat[1], plat[2], description, photo])
    restaurant_data = [restaurant[0], restaurant[1], restaurant[2], restaurant[3], restaurant[4],
    chemin_photo, horaires, mots_cles, plats_decoded]
    print(restaurant_data)
    return render_template("menu.html", restaurant=restaurant_data, notes_clients=notes_clients, length=len(plats_decoded))

#******************************************commande***********************************************
@app.route("/api/restaurants/<int:idRest>", methods=["POST"])
def api_page_restaurants(idRest):
    print("Requête POST reçue :", request.form)
    restaurant = userDB.getRestaurantsById(idRest)
    plats = userDB.getPlatsByIdRest(idRest)
    panier = []
    for i in range(len(plats)):
        quantity = request.form.get(f"quantity-{i}")
        if quantity and int(quantity) > 0:
            panier.append({"idPlat": plats[i][0], "nom": plats[i][1], "prix": float(plats[i][2]), "quantity": int(quantity)})
    prix = sum(item['prix'] * item['quantity'] for item in panier)
    session["restaurant"] = idRest 
    session["panier"] = panier
    session["prix"] = prix
    return redirect(url_for("paiement"))

#paiement
@app.route("/paiement")
def paiement():
    panier = session.get('panier', [])
    prix = session.get('prix', 0)
    frais_livraison = float(userDB.getFraisLivraison(session.get('restaurant'))) 
    return render_template("paiement.html", panier=panier, prix=prix, frais_livraison=frais_livraison)

@app.route("/api/paiement", methods=["POST"])
def api_paiment():
    numero = request.form.get("numero")
    code = request.form.get("codesecret")
    date = request.form.get("date_exp")
    proprietaire = request.form.get("proprietaire")
    if not numero or not code or not date or not proprietaire:
        flash("Veuillez remplir tous les champs de la carte bancaire.")
        return redirect(url_for("paiement"))
    try:
        date_expiration = datetime.strptime(date, "%Y-%m-%d").date()
        if date_expiration <= datetime.today().date():
            flash("La date d'expiration de la carte doit être ultérieure à aujourd'hui.")
            return redirect(url_for("paiement"))
    except ValueError:
        flash("Le format de la date d'expiration est incorrect. Utilisez AAAA-MM-JJ.")
        return redirect(url_for("paiement"))
    id_client = session.get('user_id')
    if not id_client:
        flash("Vous devez être connecté pour effectuer un paiement.")
        return redirect(url_for("connexion"))
    hashed_code = password_ctx.hash(code)
    carte = userDB.getCardByNumberAndCodeSecretAndDate(numero, hashed_code, date)
    if not carte:
        userDB.ajouteNouvelleCarte(numero, hashed_code, date, id_client, proprietaire)
        flash("Carte ajoutée avec succès.")
    else:
        flash("Carte déjà enregistrée.")
    id_commande = userDB.ajouteCommande(session.get('prix'), id_client, None, session.get('restaurant'))
    panier = session.get('panier', [])
    print(panier)
    for item in panier:
        item['idPlat'] = userDB.getIdPlatByName(item['nom']) 
    userDB.ajoutePlatsCommande(id_commande, panier)
    session.pop("panier", None)
    session.pop("prix", None)
    session.pop("restaurant", None)
    return redirect(url_for("accueil"))

#*********************************************Livreur**************************************************

#connexion
@app.route("/connexion_priv")
def connexion_priv():
    return render_template("connexion_priv.html")

@app.route("/api/connexion_priv", methods=['POST'])
def connexion_priv_api():
    matricule = request.form.get('matricule')
    mdp = request.form.get('mdp')
    if not matricule or not mdp:
        flash("Veuillez remplir tous les champs.")
        return redirect("/connexion_priv")
    livreur = userDB.getLivreurByMatricule(matricule)
    if not livreur:
        flash("Les données que vous avez saisies sont invalides.")
        return redirect("/connexion_priv")
    hashed_password = livreur[4] 
    print("Mot de passe haché :", hashed_password) 
    if not password_ctx.verify(mdp, hashed_password):
        print("Mot de passe incorrect.")  
        flash("Les données que vous avez saisies sont invalides.")
        return redirect("/connexion_priv")
    session['user_id'] = livreur[0]
    session['role'] = 'livreur'
    session['logged_in'] = True
    flash("Connexion réussie en tant que livreur.")
    return redirect(f"/profil_priv/{matricule}")


#inscription
@app.route("/inscription_priv")
def inscription_priv():
    return render_template("inscription_priv.html")

@app.route("/api/inscription_priv",methods = ['post'])
def api_inscription_priv():
    nom_i = request.form.get("nom")
    prenom_i = request.form.get("prenom")
    numtel_i = request.form.get("numtel")
    mdp_i = request.form.get("mdp")
    if not nom_i or not prenom_i:
        flash("Remplissez les 2 champs s'il vous plais!")
        return redirect("/inscription_priv")
    if not numtel_i or not utils.isValidNumber(numtel_i):
        flash("Entrez un numero de telephone valide!")
        return redirect("/inscription_priv")
    if not mdp_i or not utils.isValidPassword(mdp_i):
        flash("Entrez un mot de pass valide!")
        return redirect("/inscription_priv")
    livreur = userDB.getLivreurByNomAndPrenomAndNumAndPassword(nom_i,prenom_i,numtel_i,mdp_i)
    if livreur:
        flash("Donnes deja utiliser!")
        return redirect("/inscription_priv")  
    hashed_password = password_ctx.hash(mdp_i)
    
    userDB.inscritLivreur(nom_i,prenom_i,numtel_i,hashed_password)
    livreur = userDB.getLivreurByNomAndPrenomAndNumAndPassword(nom_i,prenom_i,numtel_i,hashed_password)
    session['user_id'] = livreur[0][0] 
    session['role'] = 'livreur' 
    session['logged_in'] = True
    matricule = livreur[0][0]
    return redirect(f"/profil_priv/{matricule}")

#profil de livreur
@app.route("/profil_priv/<matricule>")
def profil_priv(matricule):
    livreur = userDB.getLivreurByMatricule(matricule)
    villes_disponibles = userDB.getAllCodeVille()
    villes_couvrees = userDB.getVillesCouvreesParLivreur(matricule)
    if livreur[5] == "Disponible":
        commandes = userDB.getCommandesDisponiblesPourLivreur(matricule)
    else:
        commandes = []  
    return render_template("profil_prive.html", livreur=livreur, matricule=matricule, villes_couvrees=villes_couvrees,
        villes_disponibles=villes_disponibles, commandes=commandes)

@app.route("/api/profil_priv/<matricule>",methods = ['post'])
def api_profil_priv(matricule):
    statut = request.form.get('statut')
    userDB.updateLivreurStatut(matricule,statut)
    return redirect(f"/profil_priv/{matricule}")

#les villes ou un livreur travaille
@app.route("/api/ajouter_villes_travail/<matricule>", methods=["POST"])
def ajouter_villes_travail(matricule):
    codes_postaux = request.form.getlist("codePostal")
    for code in codes_postaux:
        userDB.ajouterVilleTravail(matricule, code)
    flash("Les villes ont été ajoutées avec succès.")
    return redirect(url_for("profil_priv", matricule=matricule))

#retirer une ville 
@app.route("/api/retirer_ville_travail/<matricule>", methods=["POST"])
def retirer_ville_travail(matricule):
    code_postal = request.form.get("codePostal")
    userDB.retirerVilleTravail(matricule, code_postal)
    flash(f"La ville avec le code postal {code_postal} a été retirée.")
    return redirect(url_for("profil_priv", matricule=matricule))

#prendre en charge une commande
@app.route("/api/prendre_commande/<int:idComm>", methods=["POST"])
def prendre_commande(idComm):
    matricule = session.get("user_id")
    print(matricule)
    if not matricule:
        flash("Vous devez être connecté pour effectuer cette action.")
        return redirect(url_for("connexion"))
    userDB.affecterCommandeAuLivreur(idComm, matricule)
    flash(f"La commande {idComm} a été prise en charge avec succès.")
    return redirect(url_for("profil_priv", matricule=matricule))

@app.route("/api/accepter_commande/<int:idComm>", methods=["POST"])
def accepter_commande(idComm):
    matricule = session.get("user_id")
    commande = userDB.getCommandeById(idComm)
    if commande and commande[1] == "En attente": 
        userDB.affecterCommandeAuLivreur(idComm, matricule)
        flash("Commande acceptée avec succès.")
    else:
        flash("La commande n'est plus disponible.")
    return redirect(url_for("profil_priv", matricule=matricule))

#**********************************************main*****************************************************
if __name__ == '__main__':
  app.run()