"""
Script pour créer des documents de test pour le chatbot
"""
import os

def create_test_documents():
    """Crée des documents de test dans le dossier uploads/test_documents"""
    
    # Créer le dossier test_documents
    test_dir = "uploads/test_documents"
    os.makedirs(test_dir, exist_ok=True)
    
    documents = {
        "emploi_du_temps.txt": """EMPLOI DU TEMPS - LICENCE INFORMATIQUE
Semestre 1 - Année 2024/2025

LUNDI
08h00-10h00 : Programmation Python - Salle A101 - Prof. Ahmed Ben Salem
10h15-12h15 : Mathématiques - Salle A102 - Prof. Leila Khiari
14h00-16h00 : TP Python - Lab Info 1

MARDI
08h00-10h00 : Base de données - Salle B201 - Prof. Mohamed Trabelsi
10h15-12h15 : Anglais technique - Salle C301 - Prof. Sarah Johnson
14h00-17h00 : Projet Base de données - Lab Info 2

MERCREDI
08h00-10h00 : Algorithmique - Salle A103 - Prof. Fatma Bouazizi
10h15-12h15 : Système d'exploitation - Salle A104 - Prof. Karim Messaoudi
14h00-16h00 : TP Système - Lab Info 3

JEUDI
08h00-10h00 : Réseaux informatiques - Salle B202 - Prof. Nadia Chakroun
10h15-12h15 : Développement Web - Salle A105 - Prof. Youssef Gharbi
14h00-17h00 : Projet Web - Lab Info 1

VENDREDI
08h00-10h00 : Architecture des ordinateurs - Salle A106 - Prof. Slim Hadj Ali
10h15-12h15 : Gestion de projet - Salle C302 - Prof. Ines Ferchichi

EXAMENS
Python : 15 Décembre 2024 - 09h00 - Amphi 1
Mathématiques : 18 Décembre 2024 - 09h00 - Amphi 2
Base de données : 20 Décembre 2024 - 14h00 - Amphi 1
Algorithmique : 22 Décembre 2024 - 09h00 - Amphi 3

CONTACTS
Secrétariat : secretariat@faculte.tn - Tél: 71 123 456
""",

        "procedures_administratives.txt": """PROCÉDURES ADMINISTRATIVES
Faculté des Sciences de Tunis

INSCRIPTION
Documents requis :
- Copie certifiée conforme du baccalauréat
- 4 photos d'identité récentes
- Copie de la carte d'identité nationale
- Certificat de naissance
- Frais d'inscription : 200 TND

Dates d'inscription :
- Première session : 1-15 Septembre 2024
- Deuxième session : 16-25 Septembre 2024

Où s'inscrire :
Bureau des inscriptions - Bâtiment A - Rez-de-chaussée
Horaires : 8h00-16h00 (Lundi à Vendredi)

DEMANDE DE STAGE
1. Remplir le formulaire de demande de stage
2. Joindre une lettre de motivation et un CV
3. Obtenir l'accord de l'encadrant académique
4. Soumettre le dossier 1 mois avant le début du stage

ATTESTATIONS
- Attestation d'inscription : Gratuite (délai 24h)
- Attestation de réussite : 5 TND (délai 48h)
- Relevé de notes : 10 TND (délai 3 jours)
- Diplôme : 50 TND (délai 1 mois)

BOURSE UNIVERSITAIRE
Conditions :
- Revenu familial < 5000 TND/mois
- Moyenne générale > 10/20
- Ne pas avoir redoublé plus d'une fois

Montants :
- Excellence (moyenne > 15) : 200 TND/mois
- Normale (moyenne > 12) : 150 TND/mois
- Minimale (moyenne > 10) : 100 TND/mois

Date limite : 31 Octobre 2024

RATTRAPAGE
Conditions : Moyenne entre 8/20 et 10/20
Dates : 15-20 Janvier 2025 (Session 1)
Frais : 30 TND par matière

CONTACT
Email : info@faculte.tn
Téléphone : 71 123 456
Site web : www.faculte.tn
""",

        "informations_generales.txt": """INFORMATIONS GÉNÉRALES
Faculté des Sciences de Tunis

ADRESSE
Avenue de la Liberté, 2000 Tunis, Tunisie
Tél : 71 123 456
Fax : 71 123 457
Email : contact@faculte.tn

HORAIRES D'OUVERTURE
Lundi - Vendredi : 8h00 - 17h00
Samedi : 8h00 - 12h00
Dimanche : Fermé

BIBLIOTHÈQUE
Horaires : 8h00 - 19h00 (Lundi-Samedi)
Plus de 50,000 ouvrages disponibles
Accès gratuit pour tous les étudiants inscrits
Salle de lecture : 200 places
Ordinateurs : 30 postes disponibles

RESTAURANT UNIVERSITAIRE
Horaires : 12h00 - 14h30
Prix du repas : 1 TND pour les boursiers, 3 TND pour les autres
Menu varié et équilibré

SERVICES INFORMATIQUES
- WiFi gratuit dans tout le campus
- Identifiant : Numéro de carte étudiante
- Mot de passe initial : Date de naissance (JJMMAAAA)

CLUBS ET ASSOCIATIONS
- Club Informatique : Tous les mercredis 14h00
- Club Robotique : Tous les jeudis 15h00
- Association des étudiants : Bureau B301
- Club Sport : Stade universitaire

TRANSPORT
Ligne de métro : Station Bab Saadoun (10 min à pied)
Bus : Lignes 3, 5, 12, 20
Parking étudiant : Gratuit avec carte étudiante

SERVICE MÉDICAL
Infirmerie ouverte 8h00-16h00
Médecin présent : Lundi, Mercredi, Vendredi
Consultations gratuites pour les étudiants

DATES IMPORTANTES 2024-2025
Rentrée universitaire : 15 Septembre 2024
Vacances d'hiver : 23 Décembre - 7 Janvier
Vacances de printemps : 24 Mars - 7 Avril
Fin des cours : 15 Juin 2025
""",

        "faq.txt": """QUESTIONS FRÉQUENTES (FAQ)

Q: Comment obtenir ma carte étudiante ?
R: La carte étudiante est délivrée lors de l'inscription. En cas de perte, vous devez payer 20 TND pour un duplicata au bureau des inscriptions.

Q: Puis-je changer de spécialité ?
R: Oui, durant les deux premières semaines de chaque semestre. Rendez-vous au secrétariat avec une demande écrite.

Q: Comment accéder au WiFi ?
R: Utilisez votre numéro de carte étudiante comme identifiant et votre date de naissance (JJMMAAAA) comme mot de passe initial.

Q: Où puis-je imprimer mes documents ?
R: À la bibliothèque (0.100 TND/page noir et blanc, 0.500 TND/page couleur) ou au centre de reprographie (Bâtiment C).

Q: Comment contacter un professeur ?
R: Les heures de permanence sont affichées sur la porte du bureau de chaque professeur. Vous pouvez aussi les contacter par email (prenom.nom@faculte.tn).

Q: Que faire en cas d'absence à un examen ?
R: Vous devez présenter un certificat médical ou un justificatif valable dans les 48h au bureau des examens.

Q: Comment obtenir un stage ?
R: Le bureau des stages peut vous aider. Apportez votre CV et lettre de motivation. De nombreuses offres sont affichées sur le panneau d'affichage.

Q: Puis-je suivre des cours en ligne ?
R: Oui, la plateforme Moodle est accessible sur moodle.faculte.tn avec vos identifiants universitaires.

Q: Où trouver les anciens examens ?
R: À la bibliothèque, section "Annales" ou sur la plateforme Moodle de chaque cours.

Q: Comment faire une réclamation de note ?
R: Dans les 5 jours suivant l'affichage des résultats, remplissez un formulaire au bureau des examens (frais : 10 TND).
"""
    }
    
    print("🔨 Création des documents de test...")
    print("=" * 50)
    
    for filename, content in documents.items():
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {filename} créé")
    
    print("=" * 50)
    print(f"\n✅ {len(documents)} documents créés dans {test_dir}/")
    print("\nVous pouvez maintenant :")
    print("1. Vous connecter en tant qu'admin")
    print("2. Uploader ces documents depuis l'interface web")
    print(f"3. Les fichiers se trouvent dans : {os.path.abspath(test_dir)}")

if __name__ == "__main__":
    create_test_documents()