import { Helmet } from 'react-helmet-async';
import Navbar from '../../components/navbar/Navbar';
import styles from './legal-page.module.css';

export default function TermsOfServicePage() {
  return (
    <>
      <Helmet>
        <title>CGU — Freelansign</title>
        <meta
          name="description"
          content="Conditions Générales d'Utilisation de Freelansign"
        />
      </Helmet>
      <Navbar />
      <main className={styles.legalPage}>
        <div className={styles.container}>
          <header className={styles.header}>
            <h1 className={styles.title}>Conditions Générales d'Utilisation</h1>
            <p className={styles.meta}>
              Dernière mise à jour : 15 décembre 2025
            </p>
          </header>

          <div className={styles.content}>
            {/* Sommaire */}
            <nav className="mb-8 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <h2 className="text-lg font-semibold mb-2">Sommaire</h2>
              <ol className="space-y-1 text-sm">
                <li>
                  <a href="#preambule" className="text-brand hover:underline">
                    1. Préambule
                  </a>
                </li>
                <li>
                  <a href="#definitions" className="text-brand hover:underline">
                    2. Définitions
                  </a>
                </li>
                <li>
                  <a
                    href="#mentions-legales"
                    className="text-brand hover:underline"
                  >
                    3. Mentions légales
                  </a>
                </li>
                <li>
                  <a href="#objet" className="text-brand hover:underline">
                    4. Objet du contrat
                  </a>
                </li>
                <li>
                  <a href="#acceptation" className="text-brand hover:underline">
                    5. Acceptation des CGU
                  </a>
                </li>
                <li>
                  <a href="#inscription" className="text-brand hover:underline">
                    6. Inscription et compte utilisateur
                  </a>
                </li>
                <li>
                  <a
                    href="#disponibilite"
                    className="text-brand hover:underline"
                  >
                    7. Disponibilité du service
                  </a>
                </li>
                <li>
                  <a
                    href="#protection-donnees"
                    className="text-brand hover:underline"
                  >
                    8. Protection des données personnelles
                  </a>
                </li>
                <li>
                  <a href="#securite" className="text-brand hover:underline">
                    9. Sécurité
                  </a>
                </li>
                <li>
                  <a
                    href="#tarification"
                    className="text-brand hover:underline"
                  >
                    10. Tarification
                  </a>
                </li>
                <li>
                  <a
                    href="#propriete-intellectuelle"
                    className="text-brand hover:underline"
                  >
                    11. Propriété intellectuelle
                  </a>
                </li>
                <li>
                  <a href="#resiliation" className="text-brand hover:underline">
                    12. Résiliation
                  </a>
                </li>
                <li>
                  <a
                    href="#responsabilite"
                    className="text-brand hover:underline"
                  >
                    13. Limitation de responsabilité
                  </a>
                </li>
                <li>
                  <a
                    href="#droit-applicable"
                    className="text-brand hover:underline"
                  >
                    14. Droit applicable
                  </a>
                </li>
              </ol>
            </nav>

            {/* Sections */}
            <section id="preambule" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                1. Préambule
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Freelansign est une plateforme SaaS (Software as a Service) de
                gestion de devis et factures destinée aux freelances et
                travailleurs indépendants.
              </p>
              <p className="text-gray-700 leading-relaxed">
                Les présentes Conditions Générales d'Utilisation (ci-après
                "CGU") régissent l'accès et l'utilisation de la plateforme
                Freelansign. L'utilisation de la plateforme implique
                l'acceptation sans réserve des présentes CGU.
              </p>
            </section>

            <section id="definitions" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                2. Définitions
              </h2>
              <ul className="space-y-2 text-gray-700">
                <li>
                  <strong>Service :</strong> désigne la plateforme Freelansign
                  accessible en ligne permettant la création et la gestion de
                  devis et factures.
                </li>
                <li>
                  <strong>Utilisateur :</strong> désigne toute personne physique
                  ou morale inscrite sur la plateforme Freelansign.
                </li>
                <li>
                  <strong>Compte :</strong> désigne l'espace personnel de
                  l'Utilisateur sur la plateforme.
                </li>
                <li>
                  <strong>Contenu :</strong> désigne l'ensemble des données
                  créées, stockées ou transmises par l'Utilisateur via le
                  Service.
                </li>
              </ul>
            </section>

            <section id="mentions-legales" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                3. Mentions légales
              </h2>
              <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4 rounded">
                <p className="text-sm text-blue-700 font-medium">
                  <strong>[À COMPLÉTER]</strong> : Informations juridiques à
                  fournir
                </p>
              </div>
              <ul className="space-y-2 text-gray-700 list-disc list-inside">
                <li>
                  <strong>Éditeur :</strong> [NOM DE LA SOCIÉTÉ]
                </li>
                <li>
                  <strong>Forme juridique :</strong> [FORME JURIDIQUE]
                </li>
                <li>
                  <strong>RCS :</strong> [NUMÉRO RCS + VILLE]
                </li>
                <li>
                  <strong>SIRET :</strong> [NUMÉRO SIRET]
                </li>
                <li>
                  <strong>Adresse du siège social :</strong> [ADRESSE COMPLÈTE]
                </li>
                <li>
                  <strong>Capital social :</strong> [MONTANT] euros
                </li>
                <li>
                  <strong>Contact :</strong> freelansign@gmail.com
                </li>
                <li>
                  <strong>Directeur de publication :</strong> [NOM PRÉNOM]
                </li>
                <li>
                  <strong>Hébergement :</strong> Scaleway SAS, BP 438, 75366
                  Paris Cedex 08, France - Serveurs situés en Allemagne (UE)
                </li>
              </ul>
            </section>

            <section id="objet" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                4. Objet du contrat
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Les présentes CGU ont pour objet de définir les modalités et
                conditions de mise à disposition à distance, via Internet, d'un
                droit d'accès aux services et d'un droit d'usage personnel, non
                exclusif et non transférable sur le logiciel fourni en mode
                SaaS.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                Le Service consiste en la mise à disposition d'une application
                web permettant de :
              </p>
              <ul className="space-y-2 text-gray-700 list-disc list-inside ml-4">
                <li>Créer et personnaliser des devis professionnels</li>
                <li>Gérer une base de clients</li>
                <li>Gérer des thèmes de personnalisation</li>
                <li>Suivre l'activité et les statistiques</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mt-4">
                L'Utilisateur reconnaît et accepte que le Service est fourni en
                location et non vendu. Freelansign conserve tous les droits de
                propriété intellectuelle sur le logiciel.
              </p>
            </section>

            <section id="acceptation" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                5. Acceptation des CGU
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                L'acceptation des présentes CGU est matérialisée par le fait de
                cocher la case prévue à cet effet lors de l'inscription.
                L'Utilisateur déclare avoir lu, compris et accepté les présentes
                CGU avant toute utilisation du Service.
              </p>
              <p className="text-gray-700 leading-relaxed">
                Freelansign se réserve le droit de modifier les présentes CGU à
                tout moment. Les Utilisateurs seront informés par email de toute
                modification substantielle au moins 30 jours avant son entrée en
                vigueur. L'utilisation continue du Service après l'entrée en
                vigueur des nouvelles CGU vaut acceptation de celles-ci.
              </p>
            </section>

            <section id="inscription" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                6. Inscription et compte utilisateur
              </h2>
              <h3 className="text-xl font-semibold mb-3 text-gray-800">
                6.1 Conditions d'inscription
              </h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                Le Service est réservé aux personnes physiques majeures (18 ans
                révolus) exerçant une activité professionnelle indépendante ou
                aux personnes morales.
              </p>
              <h3 className="text-xl font-semibold mb-3 text-gray-800">
                6.2 Exactitude des informations
              </h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                L'Utilisateur s'engage à fournir des informations exactes,
                complètes et à jour lors de son inscription et à les mettre à
                jour en cas de modification. Toute information fausse ou
                trompeuse peut entraîner la suspension ou la résiliation du
                compte.
              </p>
              <h3 className="text-xl font-semibold mb-3 text-gray-800">
                6.3 Sécurité du compte
              </h3>
              <p className="text-gray-700 leading-relaxed">
                L'Utilisateur est responsable de la confidentialité de ses
                identifiants de connexion. Toute utilisation du Service
                effectuée à partir de son compte est réputée avoir été effectuée
                par l'Utilisateur lui-même. L'Utilisateur s'engage à informer
                immédiatement Freelansign en cas d'utilisation non autorisée de
                son compte.
              </p>
            </section>

            <section id="disponibilite" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                7. Disponibilité du service
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Freelansign s'efforce d'assurer une disponibilité du Service
                24h/24 et 7j/7. Toutefois, Freelansign se réserve le droit
                d'interrompre temporairement l'accès au Service pour des raisons
                de maintenance, de mise à jour ou en cas de force majeure.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                Les opérations de maintenance programmées seront, dans la mesure
                du possible, notifiées aux Utilisateurs à l'avance.
              </p>
              <p className="text-gray-700 leading-relaxed">
                Freelansign ne saurait être tenu responsable des interruptions
                de service résultant de cas de force majeure, d'actes de tiers,
                de défaillances du réseau Internet, ou de tout événement
                indépendant de sa volonté.
              </p>
            </section>

            <section id="protection-donnees" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                8. Protection des données personnelles
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Freelansign s'engage à protéger les données personnelles de ses
                Utilisateurs conformément au Règlement Général sur la Protection
                des Données (RGPD) et à la loi Informatique et Libertés.
              </p>
              <p className="text-gray-700 leading-relaxed">
                Les modalités détaillées de collecte, traitement et protection
                des données personnelles sont décrites dans notre{' '}
                <a
                  href="/confidentialite"
                  className="text-brand hover:underline font-medium"
                >
                  Politique de Confidentialité
                </a>
                .
              </p>
            </section>

            <section id="securite" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                9. Sécurité
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Freelansign met en œuvre toutes les mesures techniques et
                organisationnelles appropriées pour assurer la sécurité et la
                confidentialité des données de ses Utilisateurs.
              </p>
              <h3 className="text-xl font-semibold mb-3 text-gray-800">
                9.1 Mesures de sécurité
              </h3>
              <ul className="space-y-2 text-gray-700 list-disc list-inside ml-4 mb-4">
                <li>
                  <strong>Cryptage des données sensibles :</strong> Les mots de
                  passe sont hashés avec des algorithmes sécurisés (bcrypt ou
                  Argon2)
                </li>
                <li>
                  <strong>Données bancaires :</strong> Gérées par Stripe,
                  certifié PCI-DSS niveau 1 (norme de sécurité la plus élevée
                  dans l'industrie du paiement)
                </li>
                <li>
                  <strong>Communications sécurisées :</strong> Toutes les
                  communications utilisent le protocole HTTPS avec chiffrement
                  TLS 1.3
                </li>
                <li>
                  <strong>Contrôle d'accès :</strong> Authentification forte et
                  gestion des permissions
                </li>
              </ul>
              <h3 className="text-xl font-semibold mb-3 text-gray-800">
                9.2 Notification des failles de sécurité
              </h3>
              <p className="text-gray-700 leading-relaxed">
                Conformément à l'article 33 du RGPD, en cas de violation de
                données à caractère personnel susceptible d'engendrer un risque
                pour les droits et libertés des Utilisateurs, Freelansign
                s'engage à notifier la CNIL dans les 72 heures et à informer les
                Utilisateurs concernés dans les meilleurs délais.
              </p>
            </section>

            <section id="tarification" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                10. Tarification
              </h2>
              <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4 rounded">
                <p className="text-sm text-blue-700 font-medium">
                  <strong>[À COMPLÉTER]</strong> : Informations tarifaires
                </p>
              </div>
              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>Version bêta :</strong> Freelansign est actuellement en
                phase de test bêta. Le Service est fourni gratuitement durant
                cette période. Les conditions tarifaires seront communiquées aux
                Utilisateurs avant toute facturation.
              </p>
              <p className="text-gray-700 leading-relaxed">
                Les Utilisateurs inscrits durant la phase bêta seront informés
                au moins 60 jours avant la mise en place d'une offre payante et
                pourront choisir de continuer ou de résilier leur compte sans
                frais.
              </p>
            </section>

            <section id="propriete-intellectuelle" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                11. Propriété intellectuelle
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                L'ensemble des éléments composant le Service (logiciels, bases
                de données, interfaces, textes, images, logos, marques, etc.)
                sont la propriété exclusive de Freelansign et sont protégés par
                le droit d'auteur, le droit des marques et le droit sui generis
                des bases de données.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                L'Utilisateur se voit concéder une licence d'utilisation
                personnelle, non-exclusive, non-transférable et révocable du
                Service, strictement limitée aux fonctionnalités prévues.
              </p>
              <p className="text-gray-700 leading-relaxed">
                L'Utilisateur conserve l'intégralité des droits de propriété
                intellectuelle sur les contenus qu'il crée via le Service
                (devis, factures, données clients). Freelansign ne revendique
                aucun droit sur ces contenus.
              </p>
            </section>

            <section id="resiliation" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                12. Résiliation
              </h2>
              <h3 className="text-xl font-semibold mb-3 text-gray-800">
                12.1 Résiliation par l'Utilisateur
              </h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                L'Utilisateur peut résilier son compte à tout moment depuis les
                paramètres de son compte ou en contactant freelansign@gmail.com.
                La résiliation est effective immédiatement.
              </p>
              <h3 className="text-xl font-semibold mb-3 text-gray-800">
                12.2 Résiliation par Freelansign
              </h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                Freelansign se réserve le droit de suspendre ou de résilier
                l'accès au Service en cas de :
              </p>
              <ul className="space-y-2 text-gray-700 list-disc list-inside ml-4 mb-4">
                <li>Violation des présentes CGU</li>
                <li>Utilisation frauduleuse ou abusive du Service</li>
                <li>Non-paiement (si applicable)</li>
                <li>Fourniture d'informations fausses ou trompeuses</li>
              </ul>
              <h3 className="text-xl font-semibold mb-3 text-gray-800">
                12.3 Conséquences de la résiliation
              </h3>
              <p className="text-gray-700 leading-relaxed">
                En cas de résiliation, l'accès au Service est immédiatement
                interrompu. L'Utilisateur dispose d'un délai de 30 jours pour
                exporter ses données avant leur suppression définitive. Passé ce
                délai, les données seront définitivement effacées conformément à
                notre Politique de Confidentialité.
              </p>
            </section>

            <section id="responsabilite" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                13. Limitation de responsabilité
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Freelansign s'engage à fournir un Service conforme aux
                fonctionnalités annoncées. Toutefois, la responsabilité de
                Freelansign ne peut être engagée que pour les dommages directs
                prouvés subis par l'Utilisateur.
              </p>
              <p className="text-gray-700 leading-relaxed mb-4">
                Freelansign ne saurait être tenu responsable :
              </p>
              <ul className="space-y-2 text-gray-700 list-disc list-inside ml-4 mb-4">
                <li>
                  De l'exactitude des informations saisies par l'Utilisateur
                </li>
                <li>
                  De la conformité fiscale et légale des documents générés
                  (l'Utilisateur reste responsable de la conformité de ses
                  documents)
                </li>
                <li>Des dommages indirects ou perte de chance</li>
                <li>
                  Des dysfonctionnements imputables à des cas de force majeure
                </li>
                <li>
                  Des dommages résultant d'une utilisation non conforme du
                  Service
                </li>
              </ul>
              <p className="text-gray-700 leading-relaxed">
                L'Utilisateur est invité à consulter un expert-comptable ou un
                conseiller fiscal pour s'assurer de la conformité de ses
                documents.
              </p>
            </section>

            <section id="droit-applicable" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                14. Droit applicable et juridiction
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Les présentes CGU sont régies par le droit français.
              </p>
              <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4 rounded">
                <p className="text-sm text-blue-700 font-medium">
                  <strong>[À COMPLÉTER]</strong> : Juridiction compétente
                </p>
              </div>
              <p className="text-gray-700 leading-relaxed mb-4">
                Tout litige relatif à l'interprétation ou à l'exécution des
                présentes CGU sera soumis, à défaut d'accord amiable, à la
                compétence exclusive des tribunaux de [VILLE], France.
              </p>
              <p className="text-gray-700 leading-relaxed">
                Conformément aux dispositions du Code de la consommation
                concernant le règlement amiable des litiges, Freelansign adhère
                [ou adhérera] à un service de médiation de la consommation dont
                les coordonnées seront communiquées sur demande.
              </p>
            </section>

            {/* Contact */}
            <div className="mt-12 pt-6 border-t border-gray-200 text-center">
              <p className="text-gray-600 text-sm">
                Pour toute question concernant ces CGU, contactez-nous à{' '}
                <a
                  href="mailto:freelansign@gmail.com"
                  className="text-brand hover:underline font-medium"
                >
                  freelansign@gmail.com
                </a>
              </p>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
