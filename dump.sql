DROP TABLE IF EXISTS carteBancaire CASCADE;
DROP TABLE IF EXISTS commande CASCADE;
DROP TABLE IF EXISTS client CASCADE;
DROP TABLE IF EXISTS livreur CASCADE;
DROP TABLE IF EXISTS restaurant CASCADE;
DROP TABLE IF EXISTS plats CASCADE;
DROP TABLE IF EXISTS carte CASCADE;
DROP TABLE IF EXISTS ville CASCADE;
DROP TABLE IF EXISTS offre CASCADE;
DROP TABLE IF EXISTS noter CASCADE;
DROP TABLE IF EXISTS horaire CASCADE;
DROP TABLE IF EXISTS fermetureExceptionnelle CASCADE;
DROP TABLE IF EXISTS motCle CASCADE;
DROP TABLE IF EXISTS est_ouvert CASCADE;
DROP TABLE IF EXISTS propose CASCADE;
DROP TABLE IF EXISTS contient CASCADE;
DROP TABLE IF EXISTS utilise CASCADE;
DROP TABLE IF EXISTS avoir CASCADE;
DROP TABLE IF EXISTS contacte CASCADE;
DROP TABLE IF EXISTS travaille CASCADE;


--Table Ville

CREATE TABLE ville (
    codePostal CHAR(5) PRIMARY KEY,
    nom VARCHAR(25) NOT NULL
);
--Table Carte
CREATE TABLE carte (
    idCarte INT PRIMARY KEY
);
--Table Restaurant
CREATE TABLE restaurant(
    idRest INT PRIMARY KEY,
    nom VARCHAR(30) NOT NULL,
    adresse VARCHAR(100) NOT NULL,
    statut VARCHAR(50) DEFAULT 'Ouvert' CHECK (statut IN ('Ouvert', 'Fermé')), --'Ouvert' ou 'Fermé'
    frais_prise_en_charge DECIMAL(10, 2) CHECK (frais_prise_en_charge >= 0),
    codePostal CHAR(5) REFERENCES ville(codePostal) ON DELETE SET NULL,
    idCarte INT REFERENCES carte(idCarte) ON DELETE SET NULL,
    photo bytea
);
CREATE TABLE livreur (
    matricule INT PRIMARY KEY,
    nom VARCHAR(25) NOT NULL,
    prenom VARCHAR(25) NOT NULL,
    numTel VARCHAR(10) NOT NULL,
    mdp VARCHAR(255) NOT NULL,
    statut VARCHAR(50) DEFAULT 'Disponible' CHECK (statut IN ('Disponible', 'Indisponible'))
);
--Table Client
CREATE TABLE client (
    idClient serial PRIMARY KEY,
    nom VARCHAR(25) NOT NULL,
    prenom VARCHAR(25) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    numTel VARCHAR(15) NOT NULL,
    mdp VARCHAR(300) NOT NULL,
    adresse VARCHAR(100) NOT NULL,
    points_fidelite INT DEFAULT 0 CHECK (points_fidelite >= 0),
    codePostal CHAR(5) REFERENCES ville(codePostal),
    idParrain INT REFERENCES client(idClient) ON DELETE SET NULL
);
-- Table Offre
CREATE TABLE offre (
    idOffre SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    points_necessaires INT NOT NULL CHECK (points_necessaires > 0),
    date_debut DATE,
    date_fin DATE CHECK (date_debut <= date_fin),
    statut VARCHAR(10) DEFAULT 'Active' CHECK (statut IN ('Active', 'Inactive'))
);

--Table Plats
CREATE TABLE plats (
    idPlat INT PRIMARY KEY,
    nom VARCHAR(30) NOT NULL,
    prix NUMERIC(5,2) NOT NULL CHECK (prix >= 0),
    description TEXT,
    photo bytea
);
-- Table Horaire
CREATE TABLE horaire (
    idH INT PRIMARY KEY,
    jour varchar(15) NOT NULL CHECK (jour IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    heureDebut TIME NOT NULL,
    heureFin TIME NOT NULL CHECK (heureDebut < heureFin)
);
-- Table FermetureExceptionnelle
CREATE TABLE fermetureExceptionnelle (
    idF INT PRIMARY KEY,
    date_debut DATE NOT NULL,
    date_fin DATE,
    motif TEXT,
    idRest INT REFERENCES restaurant(idRest)
);

-- Table Commande
CREATE TABLE commande (
    idComm SERIAL PRIMARY KEY, -- SERIAL crée automatiquement une séquence
    statut VARCHAR(25) NOT NULL CHECK (statut IN ('En attente', 'Livrée', 'Annulée')),
    montant_total NUMERIC(10,2) NOT NULL CHECK (montant_total >= 0),
    idRest INT REFERENCES restaurant(idRest) ON DELETE CASCADE,
    matricule INT REFERENCES livreur(matricule) ON DELETE CASCADE,
    idClient INT REFERENCES client(idClient) ON DELETE CASCADE
);

--Table motCle
CREATE TABLE motCle( 
    idMotcle int PRIMARY KEY,
    libelle varchar(20) NOT NULL, --"pizza" , "burger"...
    idRest int REFERENCES restaurant(idRest)

);
-- Table CarteBancaire
CREATE TABLE carteBancaire (
    idCarte SERIAL PRIMARY KEY,
    numero_carte VARCHAR(16) NOT NULL,
    code_secret CHAR(255) NOT NULL,
    proprietaire VARCHAR(255) NOT NULL,
    date_expiration DATE NOT NULL CHECK (date_expiration >= CURRENT_DATE),
    idClient INT REFERENCES client(idClient) ON DELETE CASCADE
);

--association PLATS CARTE
CREATE TABLE propose(
    idPlat INT REFERENCES plats(idPlat),
    idCarte INT REFERENCES carte(idCarte),
    PRIMARY KEY (idPlat,idCarte)
);

--association COMMANDE PLATS
CREATE TABLE contient(
    idPlat INT REFERENCES plats(idPlat) ON DELETE CASCADE,
    idComm INT REFERENCES commande(idComm) ON DELETE CASCADE,
    quantite INT CHECK (quantite > 0),
    PRIMARY KEY (idPlat,idComm) 
);
                                        
--association RESTAURANT HORRAIRE
CREATE TABLE est_ouvert(
    idH INT REFERENCES horaire(idH),
    idRest INT REFERENCES restaurant(idRest),
    PRIMARY KEY(idH,idRest)
);

--association RESTAURANT LIVREUR
CREATE TABLE avoir(
    idRest INT REFERENCES restaurant(idRest),
    Matricule INT REFERENCES livreur(Matricule),
    PRIMARY KEY (idRest , Matricule)
);
--association LIVREUR CLIENT
CREATE TABLE contacte (
    matricule INT REFERENCES livreur(matricule) ON DELETE CASCADE,
    idClient INT REFERENCES client(idClient) ON DELETE CASCADE,
    raison TEXT,
    PRIMARY KEY (matricule, idClient)
);

--association LIVREUR VILLE
CREATE TABLE travaille(
     matricule SERIAL  REFERENCES livreur(matricule),
     codePostal CHAR(5) REFERENCES ville(codePostal),
     PRIMARY KEY (matricule , codePostal)

);

--association CLIENT OFFRE
CREATE TABLE utilise (
    idClient INT REFERENCES client(idClient) ON DELETE CASCADE,
    idOffre INT REFERENCES offre(idOffre) ON DELETE CASCADE,
    PRIMARY KEY (idClient, idOffre)
);

--Association RESTAURANT CLIENT
CREATE TABLE noter (
    idRest INT REFERENCES restaurant(idRest) ON DELETE CASCADE,
    idClient INT REFERENCES client(idClient) ON DELETE CASCADE,
    idComm INT REFERENCES commande(idComm),
    note INT CHECK (note BETWEEN 1 AND 5),
    commentaire TEXT,
    PRIMARY KEY (idRest, idClient)
);


INSERT INTO ville (codePostal, nom) VALUES
('69001', 'Lyon'),
('33000', 'Bordeaux'),
('13001', 'Lille'),
('31000', 'Toulouse'), 
('34000', 'Montpellier'),
('75001', 'Paris'); 
INSERT INTO carte (idCarte) VALUES
(1), 
(2), 
(3), 
(4);
INSERT INTO restaurant (idRest, codePostal, nom, adresse, statut, frais_prise_en_charge, photo, idCarte) VALUES
(1, '69001', 'Le Gourmet Lyonnais', '12 Rue Mercière, Lyon', 'Ouvert', 2.50, 'static/Gourmet_Lyonnais.png', 1),
(2, '33000', 'Bordeaux Délices', '3 Place de Bordeaux, Bordeaux', 'Ouvert', 2.00, 'static/bordeaux_delices.png', 2),
(3, '33000', 'La Cave Bordelaise', '15 Rue Sainte-Catherine, Bordeaux', 'Ouvert', 1.50, 'static/la_cave_bordelaise.png', 3),
(4, '31000', 'Occitan Saveurs', '5 Rue de la Pomme, Toulouse', 'Ouvert', 3.00, 'static/occitan_saveurs.png', 4),
(5, '75001', 'Assiette Parisienne', '20 Rue Montorgueil, Paris', 'Ouvert', 3.50, 'static/assiette_parisienne.png', 1),
(6, '75001', 'Chez Dupont', '10 Avenue des Champs-Élysées, Paris', 'Ouvert', 3.00, 'static/chez_dupont.png', 3),
(7, '69001', 'Le Voyageur', '40 Boulevard de Lyon, Lyon', 'Ouvert', 1.90, 'static/le_voyageur.png', 2),
(8, '69001', 'Le Refuge Lyonnais', '25 Rue Victor Hugo, Lyon', 'Ouvert', 2.00, 'static/le_refuge_lyonnais.png', 4);        

INSERT INTO offre (description, points_necessaires, date_debut, date_fin) VALUES
('Réduction de 10% sur votre prochaine commande', 100, '2024-01-01', '2024-12-31'),
('Livraison gratuite', 150, '2024-01-01', '2024-06-30'),
('Offre spéciale de 5€', 50, NULL, NULL);
        

INSERT INTO plats (idPlat, nom, prix, description, photo)  VALUES
(1, 'Pizza Margherita', 8.50, 'Tomates, mozzarella, basilic', 'static/pizza.png'),
(2, 'Burger Classic', 10.00, NULL, 'static/burger.jpg'),
(3, 'Salade César', 7.75, 'Salade, poulet, parmesan, croutons', 'static/salade.png'),
(4, 'Pâtes Carbonara', 9.00, NULL, 'static/pates.jpg'),
(5, 'Sushi Mix', 12.50, 'Assortiment de sushi frais', 'static/sushi.jpg'),
(6, 'Steak Frites', 15.00, 'Steak tendre avec des frites croustillantes', 'static/steak_frites.jpg'),
(7, 'Poulet Tikka Masala', 13.50, 'Poulet mariné aux épices dans une sauce crémeuse', 'static/tikka_masala.jpg'),
(8, 'Pad Thaï', 11.50, 'Nouilles sautées aux crevettes, tofu et cacahuètes', 'static/pad_thai.jpg'),
(9, 'Tacos au Boeuf', 8.00, 'Tacos garnis de boeuf, fromage, et sauce piquante', 'static/tacos.jpg'),
(10, 'Ramen au Porc', 12.00, 'Nouilles dans un bouillon savoureux avec porc braisé', 'static/ramen.jpg'),
(11, 'Lasagnes', 10.50, 'Pâtes en couches avec viande hachée et fromage', 'static/lasagnes.jpg'),
(12, 'Curry de Légumes', 9.50, 'Mélange de légumes dans une sauce au curry', 'static/curry_legumes.jpg'),
(13, 'Fish & Chips', 11.00, 'Poisson pané et frites avec sauce tartare', 'static/fish_chips.jpg'),
(14, 'Quiche Lorraine', 7.00, 'Tarte salée au jambon et fromage', 'static/quiche.jpg'),
(15, 'Crêpes Suzette', 6.50, 'Crêpes au beurre, sucre et orange', 'static/crepes.jpg'),
(16, 'Falafel', 8.00, 'Boulettes de pois chiches avec sauce tahini', 'static/falafel.jpg'),
(17, 'Gyoza', 6.50, 'Raviolis japonais grillés', 'static/gyoza.jpg'),
(18, 'Soupe Pho', 10.00, 'Bouillon vietnamien aux herbes fraîches', 'static/pho.jpg'),
(19, 'Pizza Pepperoni', 9.00, 'Pizza garnie de pepperoni et fromage', 'static/pizza_pepperoni.jpg'),
(20, 'Cheesecake', 5.50, 'Dessert crémeux au fromage frais', 'static/cheesecake.jpg'),
(21, 'Brownie au Chocolat', 4.50, 'Brownie moelleux au chocolat noir', 'static/brownie.jpg'),
(22, 'Croissant', 2.50, 'Viennoiserie au beurre', 'static/croissant.jpg'),
(23, 'Muffin Myrtille', 3.50, 'Muffin moelleux aux myrtilles', 'static/muffin.jpg'),
(24, 'Pavé de Saumon', 14.50, 'Saumon grillé avec légumes vapeur', 'static/saumon.jpg'),
(25, 'couscous', 8.50, 'Couscous et légumes', 'static/couscous.jpg');


INSERT INTO horaire (idH, jour, heureDebut, heureFin) VALUES
(1, 'Monday', '00:00:00'::TIME, '23:59:59'::TIME),
(2, 'Tuesday', '00:00:00'::TIME, '23:59:59'::TIME),
(3, 'Wednesday', '00:00:00'::TIME, '23:59:59'::TIME),
(4, 'Thursday', '00:00:00'::TIME, '23:59:59'::TIME),
(5, 'Friday', '00:00:00'::TIME, '23:59:59'::TIME),
(6, 'Saturday', '00:00:00'::TIME, '23:59:59'::TIME),
(8, 'Friday', '00:00:00'::TIME, '23:59:59'::TIME),
(7, 'Sunday', '00:00:00'::TIME, '23:59:59'::TIME),
(99, 'Saturday', '08:00:00'::TIME, '16:00:00'::TIME),
(107, 'Monday', '08:00:00'::TIME, '16:59:59'::TIME),
(100, 'Sunday', '08:00:00'::TIME, '16:00:00'::TIME);

INSERT INTO fermetureExceptionnelle (idF, date_debut, date_fin, motif, idRest) VALUES
(1, '2024-12-22', '2024-12-24', 'Vacances', 2),
(2, '2024-01-01', '2024-01-01', NULL, 2),
(3, '2024-07-14', '2024-07-14', 'Fête Nationale', 1),
(4, '2024-08-01', '2024-08-15', 'Vacances dété', 3);

INSERT INTO motCle (idMotcle, libelle, idRest) VALUES
(1, 'gastronomique', 1),
(2, 'fastfood', 2),      
(3, 'fastfood', 3),      
(4, 'traditionnel', 4),  
(5, 'pizza', 5),        
(6, 'fastfood', 6),     
(7, 'pizza', 8),        
(8, 'burger', 3);      

-- Restaurant 1 (Le Gourmet Lyonnais)
INSERT INTO propose (idPlat, idCarte) VALUES
(1, 1), -- Pizza Margherita
(2, 1), -- Burger Classic
(3, 1), -- Salade César
(4, 1), -- Pâtes Carbonara
(5, 2), -- Sushi Mix
(6, 2), -- Steak Frites
(7, 2), -- Poulet Tikka Masala
(8, 2), -- Pad Thaï
(9, 3), -- Tacos au Boeuf
(10, 3), -- Ramen au Porc
(11, 3), -- Lasagnes
(12, 3), -- Curry de Légumes
(13, 4), -- Fish & Chips
(14, 4), -- Quiche Lorraine
(15, 4), -- Crêpes Suzette
(16, 4), -- Falafel
(17, 1), -- Gyoza
(18, 1), -- Soupe Pho
(19, 1), -- Pizza Pepperoni
(20, 1), -- Cheesecake
(21, 3), -- Brownie au Chocolat
(22, 3), -- Croissant
(23, 3), -- Muffin Myrtille
(24, 3), -- Pavé de Saumon
(25, 2), -- Couscous
(1, 4), -- Pizza Margherita
(2, 4), -- Burger Classic
(3, 4), -- Salade César
(4, 4); -- Pâtes Carbonara

INSERT INTO est_ouvert (idH, idRest) VALUES
(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), -- Restaurant 1
(1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), -- Restaurant 2
(1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), -- Restaurant 3
(1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), -- Restaurant 4
(1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), -- Restaurant 5
(1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), -- Restaurant 6
(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), -- Restaurant 7
(107, 8);

CREATE VIEW vue_nombre_restaurants_par_categorie AS
SELECT mc.libelle AS categorie, COUNT(r.idRest) AS nombre_restaurants
FROM restaurant r
JOIN motCle mc ON r.idRest = mc.idRest
GROUP BY mc.libelle;

