"""
enregistrements.py : Données de départ pour Quizzio
Peuple la base de données avec des catégories, thèmes, quiz, questions,
des utilisateurs fictifs et leurs interactions (scores, classement).
"""

import os
import random
from datetime import date, timedelta
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

from app import app, db, User, Category, Theme, Quiz, Question, AnswerChoice, QuizUser, UserAnswer

# ─────────────────────────────────────────
# UTILISATEURS FICTIFS
# ─────────────────────────────────────────
FAKE_USERS = [
    {"username": "alice_m",    "name": "Alice",   "lastname": "Martin",    "mail": "alice@quizzio.com",    "birthday": date(1998, 3, 14)},
    {"username": "bob_d",      "name": "Bob",     "lastname": "Dupont",    "mail": "bob@quizzio.com",      "birthday": date(1995, 7, 22)},
    {"username": "clara_v",    "name": "Clara",   "lastname": "Vidal",     "mail": "clara@quizzio.com",    "birthday": date(2000, 11, 5)},
    {"username": "david_r",    "name": "David",   "lastname": "Richard",   "mail": "david@quizzio.com",    "birthday": date(1993, 1, 30)},
    {"username": "emma_l",     "name": "Emma",    "lastname": "Leroy",     "mail": "emma@quizzio.com",     "birthday": date(2002, 6, 18)},
    {"username": "felix_b",    "name": "Félix",   "lastname": "Bernard",   "mail": "felix@quizzio.com",    "birthday": date(1997, 9, 9)},
    {"username": "grace_p",    "name": "Grace",   "lastname": "Petit",     "mail": "grace@quizzio.com",    "birthday": date(1999, 4, 25)},
    {"username": "hugo_s",     "name": "Hugo",    "lastname": "Simon",     "mail": "hugo@quizzio.com",     "birthday": date(1996, 12, 3)},
    {"username": "ines_c",     "name": "Inès",    "lastname": "Chevalier", "mail": "ines@quizzio.com",     "birthday": date(2001, 8, 15)},
    {"username": "jules_f",    "name": "Jules",   "lastname": "Fontaine",  "mail": "jules@quizzio.com",    "birthday": date(1994, 2, 28)},
    {"username": "lea_m",      "name": "Léa",     "lastname": "Moreau",    "mail": "lea@quizzio.com",      "birthday": date(2003, 5, 7)},
    {"username": "max_g",      "name": "Max",     "lastname": "Girard",    "mail": "max@quizzio.com",      "birthday": date(1991, 10, 19)},
    {"username": "nora_t",     "name": "Nora",    "lastname": "Thomas",    "mail": "nora@quizzio.com",     "birthday": date(2000, 3, 31)},
    {"username": "oscar_h",    "name": "Oscar",   "lastname": "Henry",     "mail": "oscar@quizzio.com",    "birthday": date(1988, 7, 11)},
    {"username": "pauline_n",  "name": "Pauline", "lastname": "Nicolas",   "mail": "pauline@quizzio.com",  "birthday": date(1999, 1, 22)},
]

# DONNÉES DE QUIZ
SEED_DATA = [
    {
        "category": "Sciences",
        "themes": [
            {
                "name": "Astronomie",
                "quizzes": [
                    {
                        "name": "Le système solaire",
                        "difficulty": 1,
                        "questions": [
                            {
                                "label": "Quelle est la planète la plus proche du Soleil ?",
                                "answers": [("Mercure", True), ("Vénus", False), ("Mars", False), ("Terre", False)]
                            },
                            {
                                "label": "Combien de planètes composent le système solaire ?",
                                "answers": [("8", True), ("9", False), ("7", False), ("10", False)]
                            },
                            {
                                "label": "Quelle planète est surnommée la planète rouge ?",
                                "answers": [("Mars", True), ("Jupiter", False), ("Saturne", False), ("Vénus", False)]
                            },
                            {
                                "label": "Quelle planète possède les anneaux les plus visibles ?",
                                "answers": [("Saturne", True), ("Jupiter", False), ("Uranus", False), ("Neptune", False)]
                            },
                            {
                                "label": "Quelle est l'étoile la plus proche de la Terre hors Soleil ?",
                                "answers": [("Proxima Centauri", True), ("Sirius", False), ("Bételgeuse", False), ("Vega", False)]
                            },
                        ]
                    },
                    {
                        "name": "Trous noirs et étoiles",
                        "difficulty": 3,
                        "questions": [
                            {
                                "label": "Qu'est-ce qu'un trou noir ?",
                                "answers": [("Une région où la gravité est si forte que rien n'en échappe", True), ("Une étoile morte", False), ("Un vide dans l'univers", False), ("Une planète sombre", False)]
                            },
                            {
                                "label": "Comment s'appelle la limite d'un trou noir au-delà de laquelle rien ne peut s'échapper ?",
                                "answers": [("L'horizon des événements", True), ("La singularité", False), ("Le point de Lagrange", False), ("La nébuleuse", False)]
                            },
                            {
                                "label": "Quel type d'étoile devient une supernova ?",
                                "answers": [("Une étoile massive en fin de vie", True), ("Une naine blanche", False), ("Une étoile de faible masse", False), ("Une géante rouge", False)]
                            },
                            {
                                "label": "Qu'est-ce que la voie lactée ?",
                                "answers": [("La galaxie qui contient notre système solaire", True), ("Une nébuleuse", False), ("Un amas d'étoiles", False), ("Une constellation", False)]
                            },
                            {
                                "label": "Quelle est l'unité de mesure des distances astronomiques ?",
                                "answers": [("L'année-lumière", True), ("Le kilomètre", False), ("Le parsec", False), ("L'unité astronomique", False)]
                            },
                        ]
                    },
                    {
                        "name": "Exploration spatiale",
                        "difficulty": 2,
                        "questions": [
                            {
                                "label": "Quelle est la première nation à avoir envoyé un homme sur la Lune ?",
                                "answers": [("Les États-Unis", True), ("L'URSS", False), ("La Chine", False), ("La France", False)]
                            },
                            {
                                "label": "En quelle année Neil Armstrong a-t-il marché sur la Lune ?",
                                "answers": [("1969", True), ("1967", False), ("1971", False), ("1965", False)]
                            },
                            {
                                "label": "Quel est le nom du premier satellite artificiel lancé dans l'espace ?",
                                "answers": [("Spoutnik", True), ("Explorer", False), ("Vostok", False), ("Gemini", False)]
                            },
                            {
                                "label": "Quelle agence spatiale a lancé la station spatiale internationale ?",
                                "answers": [("Une collaboration internationale dont NASA et ESA", True), ("La NASA seule", False), ("L'ESA seule", False), ("Roscosmos seule", False)]
                            },
                            {
                                "label": "Quel rover de la NASA explore Mars depuis 2021 ?",
                                "answers": [("Perseverance", True), ("Curiosity", False), ("Opportunity", False), ("Spirit", False)]
                            },
                        ]
                    },
                ]
            },
            {
                "name": "Biologie",
                "quizzes": [
                    {
                        "name": "Le corps humain",
                        "difficulty": 1,
                        "questions": [
                            {
                                "label": "Quel est l'organe le plus grand du corps humain ?",
                                "answers": [("La peau", True), ("Le foie", False), ("Le cerveau", False), ("Les poumons", False)]
                            },
                            {
                                "label": "Combien d'os compte le corps humain adulte ?",
                                "answers": [("206", True), ("212", False), ("198", False), ("220", False)]
                            },
                            {
                                "label": "Quel organe produit l'insuline ?",
                                "answers": [("Le pancréas", True), ("Le foie", False), ("Les reins", False), ("La rate", False)]
                            },
                            {
                                "label": "Quelle est la partie du cerveau responsable de l'équilibre ?",
                                "answers": [("Le cervelet", True), ("Le cortex", False), ("L'hippocampe", False), ("L'amygdale", False)]
                            },
                            {
                                "label": "Combien de litres de sang contient le corps humain en moyenne ?",
                                "answers": [("5 litres", True), ("3 litres", False), ("8 litres", False), ("10 litres", False)]
                            },
                        ]
                    },
                    {
                        "name": "La cellule et l'ADN",
                        "difficulty": 3,
                        "questions": [
                            {
                                "label": "Où se trouve l'ADN dans une cellule eucaryote ?",
                                "answers": [("Dans le noyau", True), ("Dans les mitochondries uniquement", False), ("Dans le cytoplasme", False), ("Dans la membrane cellulaire", False)]
                            },
                            {
                                "label": "Combien de paires de chromosomes possède l'être humain ?",
                                "answers": [("23", True), ("24", False), ("46", False), ("22", False)]
                            },
                            {
                                "label": "Quel processus permet à une cellule de se diviser ?",
                                "answers": [("La mitose", True), ("La méiose", False), ("La cytokinèse", False), ("La transcription", False)]
                            },
                            {
                                "label": "Quel organite est surnommé la centrale énergétique de la cellule ?",
                                "answers": [("La mitochondrie", True), ("Le ribosome", False), ("Le noyau", False), ("L'appareil de Golgi", False)]
                            },
                            {
                                "label": "Que signifie ADN ?",
                                "answers": [("Acide désoxyribonucléique", True), ("Acide dinitronucléique", False), ("Acide désoxyribose naturel", False), ("Acide dinucléotide naturel", False)]
                            },
                        ]
                    },
                ]
            },
            {
                "name": "Physique",
                "quizzes": [
                    {
                        "name": "Les lois de la physique",
                        "difficulty": 2,
                        "questions": [
                            {
                                "label": "Quelle est la vitesse de la lumière dans le vide ?",
                                "answers": [("300 000 km/s", True), ("150 000 km/s", False), ("500 000 km/s", False), ("1 000 000 km/s", False)]
                            },
                            {
                                "label": "Qui a formulé la théorie de la relativité générale ?",
                                "answers": [("Albert Einstein", True), ("Isaac Newton", False), ("Niels Bohr", False), ("Max Planck", False)]
                            },
                            {
                                "label": "Quelle est l'unité de mesure de la force ?",
                                "answers": [("Le Newton", True), ("Le Joule", False), ("Le Watt", False), ("Le Pascal", False)]
                            },
                            {
                                "label": "Quelle loi décrit la relation entre la force, la masse et l'accélération ?",
                                "answers": [("La deuxième loi de Newton", True), ("La loi de Hooke", False), ("La loi de Coulomb", False), ("La loi de Boyle", False)]
                            },
                            {
                                "label": "Quelle est la formule de l'énergie cinétique ?",
                                "answers": [("½mv²", True), ("mv²", False), ("mgh", False), ("Fd", False)]
                            },
                        ]
                    },
                ]
            },
        ]
    },
    {
        "category": "Histoire",
        "themes": [
            {
                "name": "Histoire de France",
                "quizzes": [
                    {
                        "name": "La Révolution française",
                        "difficulty": 2,
                        "questions": [
                            {
                                "label": "En quelle année a débuté la Révolution française ?",
                                "answers": [("1789", True), ("1792", False), ("1776", False), ("1799", False)]
                            },
                            {
                                "label": "Quelle prison fut prise d'assaut le 14 juillet 1789 ?",
                                "answers": [("La Bastille", True), ("La Conciergerie", False), ("Le Temple", False), ("Vincennes", False)]
                            },
                            {
                                "label": "Qui fut guillotiné le 21 janvier 1793 ?",
                                "answers": [("Louis XVI", True), ("Marie-Antoinette", False), ("Robespierre", False), ("Danton", False)]
                            },
                            {
                                "label": "Quel document proclame les droits fondamentaux des citoyens en 1789 ?",
                                "answers": [("La Déclaration des droits de l'homme et du citoyen", True), ("La Constitution", False), ("Le Code civil", False), ("Le Contrat social", False)]
                            },
                            {
                                "label": "Qui mit fin à la Révolution en prenant le pouvoir en 1799 ?",
                                "answers": [("Napoléon Bonaparte", True), ("Robespierre", False), ("Louis XVIII", False), ("Talleyrand", False)]
                            },
                        ]
                    },
                    {
                        "name": "Napoléon Bonaparte",
                        "difficulty": 2,
                        "questions": [
                            {
                                "label": "Dans quelle île est né Napoléon Bonaparte ?",
                                "answers": [("La Corse", True), ("La Sardaigne", False), ("L'Elbe", False), ("Sainte-Hélène", False)]
                            },
                            {
                                "label": "En quelle année Napoléon est-il sacré empereur ?",
                                "answers": [("1804", True), ("1800", False), ("1799", False), ("1807", False)]
                            },
                            {
                                "label": "Quelle bataille Napoléon a-t-il perdue en 1815 mettant fin à son règne ?",
                                "answers": [("Waterloo", True), ("Austerlitz", False), ("Borodino", False), ("Leipzig", False)]
                            },
                            {
                                "label": "Dans quelle île Napoléon est-il mort en exil ?",
                                "answers": [("Sainte-Hélène", True), ("L'Elbe", False), ("La Corse", False), ("La Sardaigne", False)]
                            },
                            {
                                "label": "Quel grand code juridique Napoléon a-t-il institué ?",
                                "answers": [("Le Code civil", True), ("Le Code pénal", False), ("La Constitution", False), ("Le Concordat", False)]
                            },
                        ]
                    },
                ]
            },
            {
                "name": "Guerres mondiales",
                "quizzes": [
                    {
                        "name": "La Première Guerre mondiale",
                        "difficulty": 2,
                        "questions": [
                            {
                                "label": "En quelle année a débuté la Première Guerre mondiale ?",
                                "answers": [("1914", True), ("1916", False), ("1912", False), ("1918", False)]
                            },
                            {
                                "label": "Quel événement a déclenché la Première Guerre mondiale ?",
                                "answers": [("L'assassinat de l'archiduc François-Ferdinand", True), ("L'invasion de la Belgique", False), ("La déclaration de guerre de la France", False), ("La révolution russe", False)]
                            },
                            {
                                "label": "Quel traité a mis fin à la Première Guerre mondiale ?",
                                "answers": [("Le traité de Versailles", True), ("Le traité de Paris", False), ("Le traité de Berlin", False), ("Le traité de Genève", False)]
                            },
                            {
                                "label": "Quelle bataille a été la plus meurtrière de la Première Guerre mondiale ?",
                                "answers": [("La bataille de la Somme", True), ("La bataille de Verdun", False), ("La bataille de la Marne", False), ("La bataille d'Ypres", False)]
                            },
                            {
                                "label": "En quelle année les États-Unis sont-ils entrés dans la Première Guerre mondiale ?",
                                "answers": [("1917", True), ("1915", False), ("1916", False), ("1914", False)]
                            },
                        ]
                    },
                    {
                        "name": "La Seconde Guerre mondiale",
                        "difficulty": 2,
                        "questions": [
                            {
                                "label": "En quelle année Hitler est-il arrivé au pouvoir en Allemagne ?",
                                "answers": [("1933", True), ("1935", False), ("1930", False), ("1939", False)]
                            },
                            {
                                "label": "Quel événement a déclenché l'entrée des États-Unis dans la Seconde Guerre mondiale ?",
                                "answers": [("L'attaque de Pearl Harbor", True), ("L'invasion de la Pologne", False), ("Le bombardement de Londres", False), ("La chute de Paris", False)]
                            },
                            {
                                "label": "En quelle année s'est terminée la Seconde Guerre mondiale en Europe ?",
                                "answers": [("1945", True), ("1944", False), ("1946", False), ("1943", False)]
                            },
                            {
                                "label": "Quel nom de code portait le débarquement allié en Normandie ?",
                                "answers": [("Opération Overlord", True), ("Opération Neptune", False), ("Opération Torch", False), ("Opération Market Garden", False)]
                            },
                            {
                                "label": "Dans quelle ville les bombes atomiques ont-elles été larguées en 1945 ?",
                                "answers": [("Hiroshima et Nagasaki", True), ("Tokyo et Osaka", False), ("Hiroshima et Tokyo", False), ("Nagasaki et Kyoto", False)]
                            },
                        ]
                    },
                ]
            },
            {
                "name": "Antiquité",
                "quizzes": [
                    {
                        "name": "La Rome antique",
                        "difficulty": 2,
                        "questions": [
                            {
                                "label": "Selon la légende, qui a fondé Rome ?",
                                "answers": [("Romulus", True), ("Rémus", False), ("César", False), ("Auguste", False)]
                            },
                            {
                                "label": "Quel général romain a dit 'Je suis venu, j'ai vu, j'ai vaincu' ?",
                                "answers": [("Jules César", True), ("Pompée", False), ("Auguste", False), ("Cicéron", False)]
                            },
                            {
                                "label": "Quel édifice romain était utilisé pour les combats de gladiateurs ?",
                                "answers": [("Le Colisée", True), ("Le Panthéon", False), ("Le Forum", False), ("Le Circus Maximus", False)]
                            },
                            {
                                "label": "Qui a assassiné Jules César ?",
                                "answers": [("Brutus et des sénateurs", True), ("Marc Antoine", False), ("Pompée", False), ("Auguste", False)]
                            },
                            {
                                "label": "Quelle est la langue officielle de Rome antique ?",
                                "answers": [("Le latin", True), ("Le grec", False), ("L'étrusque", False), ("L'osque", False)]
                            },
                        ]
                    },
                ]
            },
        ]
    },
    {
        "category": "Culture générale",
        "themes": [
            {
                "name": "Géographie",
                "quizzes": [
                    {
                        "name": "Capitales du monde",
                        "difficulty": 1,
                        "questions": [
                            {
                                "label": "Quelle est la capitale du Japon ?",
                                "answers": [("Tokyo", True), ("Osaka", False), ("Kyoto", False), ("Hiroshima", False)]
                            },
                            {
                                "label": "Quelle est la capitale du Brésil ?",
                                "answers": [("Brasília", True), ("São Paulo", False), ("Rio de Janeiro", False), ("Salvador", False)]
                            },
                            {
                                "label": "Quelle est la capitale de l'Australie ?",
                                "answers": [("Canberra", True), ("Sydney", False), ("Melbourne", False), ("Brisbane", False)]
                            },
                            {
                                "label": "Quelle est la capitale du Canada ?",
                                "answers": [("Ottawa", True), ("Toronto", False), ("Montréal", False), ("Vancouver", False)]
                            },
                            {
                                "label": "Quelle est la capitale de l'Argentine ?",
                                "answers": [("Buenos Aires", True), ("Córdoba", False), ("Rosario", False), ("Mendoza", False)]
                            },
                        ]
                    },
                    {
                        "name": "Fleuves et montagnes",
                        "difficulty": 2,
                        "questions": [
                            {
                                "label": "Quel est le plus long fleuve du monde ?",
                                "answers": [("Le Nil", True), ("L'Amazone", False), ("Le Mississippi", False), ("Le Yangtsé", False)]
                            },
                            {
                                "label": "Quelle est la plus haute montagne du monde ?",
                                "answers": [("L'Everest", True), ("Le K2", False), ("Le Kangchenjunga", False), ("Le Mont Blanc", False)]
                            },
                            {
                                "label": "Dans quel pays se trouve le désert du Sahara ?",
                                "answers": [("Il s'étend sur plusieurs pays d'Afrique du Nord", True), ("En Algérie uniquement", False), ("En Égypte uniquement", False), ("Au Maroc uniquement", False)]
                            },
                            {
                                "label": "Quel est le plus grand océan du monde ?",
                                "answers": [("L'océan Pacifique", True), ("L'océan Atlantique", False), ("L'océan Indien", False), ("L'océan Arctique", False)]
                            },
                            {
                                "label": "Quelle chaîne de montagnes sépare l'Europe de l'Asie ?",
                                "answers": [("L'Oural", True), ("Les Alpes", False), ("Les Carpates", False), ("Le Caucase", False)]
                            },
                        ]
                    },
                ]
            },
            {
                "name": "Cinéma",
                "quizzes": [
                    {
                        "name": "Films cultes",
                        "difficulty": 2,
                        "questions": [
                            {
                                "label": "Qui a réalisé le film Inception ?",
                                "answers": [("Christopher Nolan", True), ("Steven Spielberg", False), ("James Cameron", False), ("Ridley Scott", False)]
                            },
                            {
                                "label": "Dans quel film trouve-t-on la réplique 'Je serai de retour' ?",
                                "answers": [("Terminator", True), ("RoboCop", False), ("Die Hard", False), ("Predator", False)]
                            },
                            {
                                "label": "Quel film a remporté l'Oscar du meilleur film en 1994 ?",
                                "answers": [("Forrest Gump", True), ("Pulp Fiction", False), ("Le Silence des agneaux", False), ("Schindler's List", False)]
                            },
                            {
                                "label": "Qui joue le rôle de Jack Dawson dans Titanic ?",
                                "answers": [("Leonardo DiCaprio", True), ("Brad Pitt", False), ("Tom Hanks", False), ("Matt Damon", False)]
                            },
                            {
                                "label": "Quel réalisateur a créé la saga Star Wars ?",
                                "answers": [("George Lucas", True), ("Steven Spielberg", False), ("James Cameron", False), ("Ridley Scott", False)]
                            },
                        ]
                    },
                    {
                        "name": "Réalisateurs légendaires",
                        "difficulty": 3,
                        "questions": [
                            {
                                "label": "Quel réalisateur est connu pour ses films Vertigo et Psychose ?",
                                "answers": [("Alfred Hitchcock", True), ("Stanley Kubrick", False), ("Orson Welles", False), ("Billy Wilder", False)]
                            },
                            {
                                "label": "Qui a réalisé 2001 : L'Odyssée de l'espace ?",
                                "answers": [("Stanley Kubrick", True), ("Steven Spielberg", False), ("Ridley Scott", False), ("George Lucas", False)]
                            },
                            {
                                "label": "Quel réalisateur français est l'auteur d'Amélie Poulain ?",
                                "answers": [("Jean-Pierre Jeunet", True), ("Luc Besson", False), ("François Truffaut", False), ("Claude Lelouch", False)]
                            },
                            {
                                "label": "Qui a réalisé Schindler's List ?",
                                "answers": [("Steven Spielberg", True), ("Martin Scorsese", False), ("Francis Ford Coppola", False), ("Oliver Stone", False)]
                            },
                            {
                                "label": "Quel réalisateur a créé la trilogie Le Seigneur des Anneaux ?",
                                "answers": [("Peter Jackson", True), ("Ridley Scott", False), ("James Cameron", False), ("Christopher Nolan", False)]
                            },
                        ]
                    },
                ]
            },
            {
                "name": "Littérature",
                "quizzes": [
                    {
                        "name": "Classiques de la littérature",
                        "difficulty": 2,
                        "questions": [
                            {
                                "label": "Qui a écrit Les Misérables ?",
                                "answers": [("Victor Hugo", True), ("Émile Zola", False), ("Gustave Flaubert", False), ("Alexandre Dumas", False)]
                            },
                            {
                                "label": "Quel auteur a créé le personnage de Sherlock Holmes ?",
                                "answers": [("Arthur Conan Doyle", True), ("Agatha Christie", False), ("Edgar Allan Poe", False), ("G.K. Chesterton", False)]
                            },
                            {
                                "label": "Qui a écrit Don Quichotte ?",
                                "answers": [("Miguel de Cervantes", True), ("Lope de Vega", False), ("Federico García Lorca", False), ("Jorge Luis Borges", False)]
                            },
                            {
                                "label": "Quel auteur a écrit 1984 ?",
                                "answers": [("George Orwell", True), ("Aldous Huxley", False), ("Ray Bradbury", False), ("Philip K. Dick", False)]
                            },
                            {
                                "label": "Qui est l'auteur de La Divine Comédie ?",
                                "answers": [("Dante Alighieri", True), ("Pétrarque", False), ("Boccace", False), ("Virgile", False)]
                            },
                        ]
                    },
                ]
            },
        ]
    },
    {
        "category": "Technologie",
        "themes": [
            {
                "name": "Informatique",
                "quizzes": [
                    {
                        "name": "Bases de l'informatique",
                        "difficulty": 1,
                        "questions": [
                            {
                                "label": "Que signifie l'acronyme HTML ?",
                                "answers": [("HyperText Markup Language", True), ("High Transfer Markup Language", False), ("HyperText Machine Language", False), ("Hyperlink and Text Markup Language", False)]
                            },
                            {
                                "label": "Quel langage est principalement utilisé pour le style des pages web ?",
                                "answers": [("CSS", True), ("JavaScript", False), ("Python", False), ("PHP", False)]
                            },
                            {
                                "label": "Que signifie CPU ?",
                                "answers": [("Central Processing Unit", True), ("Computer Personal Unit", False), ("Central Program Utility", False), ("Core Processing Unit", False)]
                            },
                            {
                                "label": "Quel est le système de numération utilisé par les ordinateurs ?",
                                "answers": [("Binaire", True), ("Décimal", False), ("Hexadécimal", False), ("Octal", False)]
                            },
                            {
                                "label": "Que signifie RAM ?",
                                "answers": [("Random Access Memory", True), ("Read Access Memory", False), ("Rapid Access Module", False), ("Runtime Access Memory", False)]
                            },
                        ]
                    },
                    {
                        "name": "Internet et réseaux",
                        "difficulty": 2,
                        "questions": [
                            {
                                "label": "Que signifie HTTP ?",
                                "answers": [("HyperText Transfer Protocol", True), ("High Transfer Text Protocol", False), ("HyperText Transmission Process", False), ("Hyperlink Transfer Protocol", False)]
                            },
                            {
                                "label": "Quel port est utilisé par défaut par HTTPS ?",
                                "answers": [("443", True), ("80", False), ("8080", False), ("22", False)]
                            },
                            {
                                "label": "Que signifie DNS ?",
                                "answers": [("Domain Name System", True), ("Dynamic Network Service", False), ("Domain Network Server", False), ("Direct Name Service", False)]
                            },
                            {
                                "label": "Qu'est-ce qu'une adresse IP ?",
                                "answers": [("Un identifiant numérique attribué à chaque appareil sur un réseau", True), ("Un mot de passe réseau", False), ("Un protocole de communication", False), ("Un type de câble réseau", False)]
                            },
                            {
                                "label": "Quel protocole est utilisé pour envoyer des e-mails ?",
                                "answers": [("SMTP", True), ("FTP", False), ("HTTP", False), ("SSH", False)]
                            },
                        ]
                    },
                    {
                        "name": "Programmation",
                        "difficulty": 3,
                        "questions": [
                            {
                                "label": "Quel paradigme de programmation utilise des objets ?",
                                "answers": [("La programmation orientée objet", True), ("La programmation fonctionnelle", False), ("La programmation impérative", False), ("La programmation logique", False)]
                            },
                            {
                                "label": "Quelle structure de données fonctionne en LIFO ?",
                                "answers": [("Une pile (stack)", True), ("Une file (queue)", False), ("Un tableau", False), ("Une liste chaînée", False)]
                            },
                            {
                                "label": "Que signifie API ?",
                                "answers": [("Application Programming Interface", True), ("Application Process Integration", False), ("Automated Programming Interface", False), ("Application Protocol Interface", False)]
                            },
                            {
                                "label": "Quel algorithme de tri a une complexité moyenne de O(n log n) ?",
                                "answers": [("Le tri rapide (quicksort)", True), ("Le tri à bulles", False), ("Le tri par insertion", False), ("Le tri par sélection", False)]
                            },
                            {
                                "label": "Qu'est-ce qu'une fonction récursive ?",
                                "answers": [("Une fonction qui s'appelle elle-même", True), ("Une fonction qui s'exécute en boucle", False), ("Une fonction sans paramètres", False), ("Une fonction qui retourne une autre fonction", False)]
                            },
                        ]
                    },
                ]
            },
        ]
    },
    {
        "category": "Sport",
        "themes": [
            {
                "name": "Football",
                "quizzes": [
                    {
                        "name": "Coupe du monde de football",
                        "difficulty": 1,
                        "questions": [
                            {
                                "label": "Quelle nation a remporté le plus de Coupes du monde ?",
                                "answers": [("Le Brésil (5 titres)", True), ("L'Allemagne", False), ("L'Italie", False), ("L'Argentine", False)]
                            },
                            {
                                "label": "Dans quel pays s'est déroulée la Coupe du monde 1998 ?",
                                "answers": [("La France", True), ("L'Allemagne", False), ("L'Italie", False), ("L'Espagne", False)]
                            },
                            {
                                "label": "Qui a remporté le Ballon d'or le plus de fois ?",
                                "answers": [("Lionel Messi", True), ("Cristiano Ronaldo", False), ("Ronaldo", False), ("Zinedine Zidane", False)]
                            },
                            {
                                "label": "Combien de joueurs composent une équipe de football sur le terrain ?",
                                "answers": [("11", True), ("10", False), ("12", False), ("9", False)]
                            },
                            {
                                "label": "Quelle équipe a remporté la Coupe du monde 2018 ?",
                                "answers": [("La France", True), ("La Croatie", False), ("La Belgique", False), ("L'Angleterre", False)]
                            },
                        ]
                    },
                ]
            },
            {
                "name": "Jeux olympiques",
                "quizzes": [
                    {
                        "name": "Histoire des Jeux olympiques",
                        "difficulty": 2,
                        "questions": [
                            {
                                "label": "Dans quelle ville se sont déroulés les premiers Jeux olympiques modernes ?",
                                "answers": [("Athènes", True), ("Paris", False), ("Londres", False), ("Stockholm", False)]
                            },
                            {
                                "label": "En quelle année ont eu lieu les premiers Jeux olympiques modernes ?",
                                "answers": [("1896", True), ("1900", False), ("1892", False), ("1904", False)]
                            },
                            {
                                "label": "Quelle ville a accueilli les Jeux olympiques d'été en 2024 ?",
                                "answers": [("Paris", True), ("Los Angeles", False), ("Londres", False), ("Tokyo", False)]
                            },
                            {
                                "label": "Combien de fois la flamme olympique est-elle allumée par les rayons du soleil ?",
                                "answers": [("Une seule fois, à Olympie en Grèce", True), ("À chaque ville hôte", False), ("Deux fois par Jeux", False), ("La flamme n'est pas allumée par le soleil", False)]
                            },
                            {
                                "label": "Quel athlète a remporté 8 médailles d'or aux JO de Pékin 2008 ?",
                                "answers": [("Michael Phelps", True), ("Usain Bolt", False), ("Carl Lewis", False), ("Mark Spitz", False)]
                            },
                        ]
                    },
                ]
            },
        ]
    },
    {
        "category": "Art et musique",
        "themes": [
            {
                "name": "Peinture",
                "quizzes": [
                    {
                        "name": "Grands peintres",
                        "difficulty": 2,
                        "questions": [
                            {
                                "label": "Qui a peint la Joconde ?",
                                "answers": [("Léonard de Vinci", True), ("Michel-Ange", False), ("Raphaël", False), ("Botticelli", False)]
                            },
                            {
                                "label": "Qui a peint La Nuit étoilée ?",
                                "answers": [("Vincent van Gogh", True), ("Paul Gauguin", False), ("Claude Monet", False), ("Paul Cézanne", False)]
                            },
                            {
                                "label": "Quel mouvement artistique Picasso a-t-il cofondé ?",
                                "answers": [("Le cubisme", True), ("Le surréalisme", False), ("L'impressionnisme", False), ("Le fauvisme", False)]
                            },
                            {
                                "label": "Dans quel musée se trouve la Joconde ?",
                                "answers": [("Le Louvre à Paris", True), ("Le Prado à Madrid", False), ("La National Gallery à Londres", False), ("Les Offices à Florence", False)]
                            },
                            {
                                "label": "Qui a peint le plafond de la Chapelle Sixtine ?",
                                "answers": [("Michel-Ange", True), ("Léonard de Vinci", False), ("Raphaël", False), ("Botticelli", False)]
                            },
                        ]
                    },
                ]
            },
            {
                "name": "Musique classique",
                "quizzes": [
                    {
                        "name": "Compositeurs célèbres",
                        "difficulty": 2,
                        "questions": [
                            {
                                "label": "Qui a composé la Cinquième Symphonie ?",
                                "answers": [("Ludwig van Beethoven", True), ("Wolfgang Amadeus Mozart", False), ("Johann Sebastian Bach", False), ("Franz Schubert", False)]
                            },
                            {
                                "label": "À quel âge Mozart a-t-il commencé à composer ?",
                                "answers": [("5 ans", True), ("10 ans", False), ("7 ans", False), ("3 ans", False)]
                            },
                            {
                                "label": "Qui a composé Les Quatre Saisons ?",
                                "answers": [("Antonio Vivaldi", True), ("Johann Sebastian Bach", False), ("Georg Friedrich Haendel", False), ("Claudio Monteverdi", False)]
                            },
                            {
                                "label": "Quelle était la nationalité de Frédéric Chopin ?",
                                "answers": [("Polonaise", True), ("Française", False), ("Autrichienne", False), ("Allemande", False)]
                            },
                            {
                                "label": "Qui a composé Le Lac des cygnes ?",
                                "answers": [("Tchaïkovski", True), ("Debussy", False), ("Ravel", False), ("Stravinski", False)]
                            },
                        ]
                    },
                ]
            },
        ]
    },
]


def simulate_quiz_attempt(questions, skill_level: float) -> tuple[int, list[AnswerChoice]]:
    """
    Simule une tentative de quiz pour un utilisateur avec un niveau de compétence donné.
    skill_level : 0.0 (très mauvais) → 1.0 (parfait)
    Retourne (score, liste de AnswerChoice sélectionnés).
    """
    score = 0
    chosen_answers = []

    for question in questions:
        choices = question.answer_choice  # liste d'AnswerChoice
        correct = [c for c in choices if c.is_answer]
        wrong = [c for c in choices if not c.is_answer]

        # Pour chaque bonne réponse attendue, l'utilisateur la choisit selon son skill
        for correct_choice in correct:
            if random.random() < skill_level:
                chosen_answers.append(correct_choice)
            else:
                # Il choisit une mauvaise réponse à la place
                if wrong:
                    chosen_answers.append(random.choice(wrong))

        # Score = nombre de bonnes réponses choisies
        good_chosen = sum(1 for c in chosen_answers if c.is_answer and c.question_id == question.id)
        score += good_chosen

    return score, chosen_answers


def compute_max_score(questions) -> int:
    return sum(q.nb_good_answers for q in questions)



def seed():
    with app.app_context():

        # Création d'un admin 
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                mail='admin@quizzio.com',
                hashed_password=generate_password_hash('admin1234'),
                account_activated=True,
                name='Admin'
            )
            db.session.add(admin)
            db.session.flush()
            print("Utilisateur admin créé (admin / admin1234)")

        # Création d'utilisateurs fictifs 
        created_users = []
        for ud in FAKE_USERS:
            user = User.query.filter_by(username=ud["username"]).first()
            if not user:
                user = User(
                    username=ud["username"],
                    name=ud["name"],
                    lastname=ud["lastname"],
                    mail=ud["mail"],
                    birthday=ud["birthday"],
                    hashed_password=generate_password_hash('password123'),
                    account_activated=True,
                )
                db.session.add(user)
                db.session.flush()
                print(f"Utilisateur créé : {ud['username']}")
            created_users.append(user)

        db.session.flush()

        # Création de Catégories, thèmes, quiz, questions
        quiz_count = 0
        all_quizzes = []  # [(quiz, [questions])]

        for cat_data in SEED_DATA:
            category = Category.query.filter_by(name=cat_data["category"]).first()
            if not category:
                category = Category(name=cat_data["category"])
                db.session.add(category)
                db.session.flush()
            print(f"\nCatégorie : {category.name}")

            for theme_data in cat_data["themes"]:
                theme = Theme.query.filter_by(name=theme_data["name"]).first()
                if not theme:
                    theme = Theme(name=theme_data["name"], category_id=category.id)
                    db.session.add(theme)
                    db.session.flush()
                print(f"  Thème : {theme.name}")

                for quiz_data in theme_data["quizzes"]:
                    if Quiz.query.filter_by(name=quiz_data["name"], theme_id=theme.id).first():
                        existing = Quiz.query.filter_by(name=quiz_data["name"], theme_id=theme.id).first()
                        questions = Question.query.filter_by(quiz_id=existing.id).all()
                        for q in questions:
                            q.answer_choice  
                        all_quizzes.append((existing, questions))
                        print(f"    Quiz déjà existant, ignoré : {quiz_data['name']}")
                        continue

                    quiz = Quiz(
                        name=quiz_data["name"],
                        theme_id=theme.id,
                        difficulty=quiz_data["difficulty"],
                        nb_questions=len(quiz_data["questions"]),
                        timer=0,
                        created_by='admin'
                    )
                    db.session.add(quiz)
                    db.session.flush()
                    quiz_count += 1
                    print(f"    Quiz créé : {quiz.name}")

                    quiz_questions = []
                    for order, q_data in enumerate(quiz_data["questions"], 1):
                        nb_good = sum(1 for _, is_ans in q_data["answers"] if is_ans)
                        question = Question(
                            quiz_id=quiz.id,
                            label=q_data["label"],
                            nb_answers=len(q_data["answers"]),
                            nb_good_answers=nb_good,
                            order_in_quiz=order
                        )
                        db.session.add(question)
                        db.session.flush()

                        # Rendre l'ordre de la bonne réponse aléatoire
                        shuffled_answers = list(q_data["answers"])
                        random.shuffle(shuffled_answers)

                        for label, is_answer in shuffled_answers:
                            db.session.add(AnswerChoice(
                                question_id=question.id,
                                label=label,
                                is_answer=is_answer
                            ))
                        db.session.flush()
                        quiz_questions.append(question)

                    all_quizzes.append((quiz, quiz_questions))

        db.session.commit()

        # Chaque utilisateur a un skill_level aléatoire (entre 0.4 et 1.0)
        user_skills = {u.username: round(random.uniform(0.4, 1.0), 2) for u in created_users}

        for user in created_users:
            skill = user_skills[user.username]
            # Chaque utilisateur joue entre 3 et len(all_quizzes) quiz
            nb_quizzes_played = random.randint(3, min(len(all_quizzes), 10))
            quizzes_played = random.sample(all_quizzes, nb_quizzes_played)

            total_pts = 0.0
            scores_list = []

            for quiz, questions in quizzes_played:
                if not questions:
                    continue

                # Recharger les answer_choice pour chaque question
                for q in questions:
                    db.session.refresh(q)

                max_score = compute_max_score(questions)
                if max_score == 0:
                    continue

                # Simule 1 à 3 tentatives (meilleur score retenu)
                nb_attempts = random.randint(1, 3)
                best = 0
                last = 0
                last_choices = []

                for attempt in range(nb_attempts):
                    score, chosen = simulate_quiz_attempt(questions, skill)
                    last = score
                    last_choices = chosen
                    if score > best:
                        best = score

                # Vérifier si QuizUser existe déjà
                existing_qu = QuizUser.query.filter_by(
                    user_id=user.username, quiz_id=quiz.id
                ).first()
                if existing_qu:
                    continue

                is_finished = random.random() < 0.75  # 75% chance de terminer

                qu = QuizUser(
                    user_id=user.username,
                    quiz_id=quiz.id,
                    last_score=last,
                    best_score=best,
                    is_favorite=random.random() < 0.3,
                    is_finished=is_finished,
                    last_question_opened_id=questions[-1].id if is_finished else random.choice(questions).id
                )
                db.session.add(qu)

                # Enregistrer les UserAnswer pour la dernière tentative
                seen_pairs = set()
                for choice in last_choices:
                    pair = (user.username, choice.id)
                    if pair in seen_pairs:
                        continue
                    seen_pairs.add(pair)
                    existing_ua = UserAnswer.query.filter_by(
                        user_id=user.username, answer_choice_id=choice.id
                    ).first()
                    if not existing_ua:
                        db.session.add(UserAnswer(
                            user_id=user.username,
                            answer_choice_id=choice.id
                        ))

                # Calcul des points (score normalisé sur 100, pondéré par difficulté)
                normalized = (best / max_score) * 100 * quiz.difficulty
                total_pts += normalized
                scores_list.append(normalized)

            # Mise à jour des stats utilisateur
            if scores_list:
                user.total_points = round(total_pts, 2)
                user.average = round(sum(scores_list) / len(scores_list), 2)

            db.session.flush()
            print(f"  {user.username} (skill={skill}) → {len(scores_list)} quiz, "
                  f"{user.total_points} pts, moyenne {user.average}")

        db.session.commit()


if __name__ == "__main__":
    seed()