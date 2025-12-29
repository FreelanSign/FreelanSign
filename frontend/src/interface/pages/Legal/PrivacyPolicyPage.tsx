import { Helmet } from 'react-helmet-async';
import Navbar from '../../components/navbar/Navbar';
import styles from './legal-page.module.css';

export default function PrivacyPolicyPage() {
  return (
    <>
      <Helmet>
        <title>Politique de Confidentialité — Freelansign</title>
        <meta
          name="description"
          content="Politique de Confidentialité et protection des données personnelles de Freelansign - Conformité RGPD"
        />
      </Helmet>
      <Navbar />
      <main className={styles.legalPage}>
        <div className={styles.container}>
          <header className={styles.header}>
            <h1 className={styles.title}>Politique de Confidentialité</h1>
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
                  <a
                    href="#responsable-traitement"
                    className="text-brand hover:underline"
                  >
                    2. Responsable de traitement
                  </a>
                </li>
                <li>
                  <a
                    href="#donnees-collectees"
                    className="text-brand hover:underline"
                  >
                    3. Données collectées et finalités
                  </a>
                </li>
                <li>
                  <a
                    href="#destinataires"
                    className="text-brand hover:underline"
                  >
                    4. Destinataires des données
                  </a>
                </li>
                <li>
                  <a
                    href="#conservation"
                    className="text-brand hover:underline"
                  >
                    5. Durée de conservation
                  </a>
                </li>
                <li>
                  <a href="#securite" className="text-brand hover:underline">
                    6. Sécurité des données
                  </a>
                </li>
                <li>
                  <a href="#hebergement" className="text-brand hover:underline">
                    7. Hébergement des données
                  </a>
                </li>
                <li>
                  <a href="#droits" className="text-brand hover:underline">
                    8. Vos droits
                  </a>
                </li>
                <li>
                  <a href="#cookies" className="text-brand hover:underline">
                    9. Cookies et traceurs
                  </a>
                </li>
                <li>
                  <a href="#transferts" className="text-brand hover:underline">
                    10. Transferts internationaux
                  </a>
                </li>
                <li>
                  <a href="#mineurs" className="text-brand hover:underline">
                    11. Mineurs
                  </a>
                </li>
                <li>
                  <a
                    href="#modifications"
                    className="text-brand hover:underline"
                  >
                    12. Modifications
                  </a>
                </li>
                <li>
                  <a href="#reclamation" className="text-brand hover:underline">
                    13. Réclamation
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
                Freelansign accorde une importance particulière à la protection
                de votre vie privée et de vos données personnelles. Cette
                Politique de Confidentialité a pour objectif de vous informer de
                manière claire et transparente sur la façon dont nous
                collectons, utilisons, protégeons et stockons vos données
                personnelles.
              </p>
              <p className="text-gray-700 leading-relaxed">
                Nous nous engageons à respecter le Règlement Général sur la
                Protection des Données (RGPD - Règlement UE 2016/679) ainsi que
                la loi Informatique et Libertés modifiée.
              </p>
            </section>

            <section id="responsable-traitement" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                2. Responsable de traitement
              </h2>
              <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4 rounded">
                <p className="text-sm text-blue-700 font-medium">
                  <strong>[À COMPLÉTER]</strong> : Informations sur le
                  responsable de traitement
                </p>
              </div>
              <p className="text-gray-700 leading-relaxed mb-4">
                Le responsable du traitement de vos données personnelles est :
              </p>
              <ul className="space-y-2 text-gray-700 list-disc list-inside ml-4">
                <li>
                  <strong>Raison sociale :</strong> [NOM DE LA SOCIÉTÉ]
                </li>
                <li>
                  <strong>Adresse :</strong> [ADRESSE COMPLÈTE]
                </li>
                <li>
                  <strong>Email :</strong> freelansign@gmail.com
                </li>
                <li>
                  <strong>
                    Contact DPO (Délégué à la Protection des Données) :
                  </strong>{' '}
                  freelansign@gmail.com
                </li>
              </ul>
            </section>

            <section id="donnees-collectees" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                3. Données collectées et finalités
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Nous collectons uniquement les données nécessaires au
                fonctionnement du service et au respect de nos obligations
                légales.
              </p>

              <div className="overflow-x-auto mb-6">
                <table className="min-w-full border border-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b">
                        Type de données
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b">
                        Finalités
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b">
                        Base légale
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    <tr>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        <strong>Données d'identité</strong>
                        <br />
                        Nom, prénom, email
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        Création et gestion du compte, communication avec
                        l'utilisateur
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        Exécution du contrat (Art. 6.1.b RGPD)
                      </td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        <strong>Données professionnelles</strong>
                        <br />
                        SIRET, raison sociale, adresse, téléphone
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        Génération de devis et factures conformes aux
                        obligations légales
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        Exécution du contrat (Art. 6.1.b RGPD)
                      </td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        <strong>Données bancaires</strong>
                        <br />
                        Informations de paiement
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        Traitement des paiements (abonnements futurs)
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        Exécution du contrat (Art. 6.1.b RGPD)
                      </td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        <strong>Données de connexion</strong>
                        <br />
                        Adresse IP, logs d'accès, date et heure de connexion
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        Sécurité du service, prévention de la fraude,
                        statistiques d'utilisation
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        Intérêt légitime (Art. 6.1.f RGPD)
                      </td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        <strong>Données de contenu</strong>
                        <br />
                        Devis, factures, clients créés par l'utilisateur
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        Fourniture du service SaaS
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        Exécution du contrat (Art. 6.1.b RGPD)
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <p className="text-gray-700 leading-relaxed">
                Nous ne collectons aucune donnée sensible au sens de l'article 9
                du RGPD (origine raciale ou ethnique, opinions politiques,
                convictions religieuses, données de santé, etc.).
              </p>
            </section>

            <section id="destinataires" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                4. Destinataires des données
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Vos données personnelles sont destinées aux catégories de
                destinataires suivantes :
              </p>
              <ul className="space-y-3 text-gray-700">
                <li>
                  <strong>Personnel habilité de Freelansign :</strong> Nos
                  équipes techniques et support ont accès à vos données dans la
                  limite de leurs attributions respectives.
                </li>
                <li>
                  <strong>Prestataires techniques :</strong>
                  <ul className="ml-6 mt-2 space-y-1 list-disc list-inside">
                    <li>
                      <strong>Hébergement :</strong> Scaleway (Allemagne, UE) -
                      Hébergement des serveurs et bases de données
                    </li>
                    <li>
                      <strong>Paiement :</strong> Stripe - Traitement sécurisé
                      des paiements (certifié PCI-DSS niveau 1)
                    </li>
                  </ul>
                </li>
                <li>
                  <strong>Aucune cession à des tiers :</strong> Nous ne vendons,
                  ne louons et ne cédons pas vos données à des tiers à des fins
                  commerciales.
                </li>
              </ul>
            </section>

            <section id="conservation" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                5. Durée de conservation
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Vos données sont conservées uniquement le temps nécessaire aux
                finalités pour lesquelles elles ont été collectées :
              </p>
              <ul className="space-y-2 text-gray-700 list-disc list-inside ml-4">
                <li>
                  <strong>Données de compte :</strong> Pendant la durée de votre
                  abonnement + 3 ans en archivage intermédiaire (délai de
                  prescription)
                </li>
                <li>
                  <strong>Données de facturation :</strong> 10 ans (obligation
                  légale comptable et fiscale)
                </li>
                <li>
                  <strong>Données de connexion :</strong> 12 mois maximum
                  (exigence de sécurité)
                </li>
                <li>
                  <strong>Données de contenu (devis, factures) :</strong> Durée
                  de l'abonnement + 30 jours après résiliation pour permettre
                  l'export
                </li>
              </ul>
              <p className="text-gray-700 leading-relaxed mt-4">
                À l'issue de ces durées, vos données sont définitivement
                supprimées ou anonymisées de manière irréversible.
              </p>
            </section>

            <section id="securite" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                6. Sécurité des données
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Nous mettons en œuvre des mesures techniques et
                organisationnelles appropriées pour assurer un niveau de
                sécurité adapté au risque, conformément à l'article 32 du RGPD.
              </p>

              <h3 className="text-xl font-semibold mb-3 text-gray-800">
                6.1 Mesures de cryptage et chiffrement
              </h3>
              <ul className="space-y-2 text-gray-700 list-disc list-inside ml-4 mb-4">
                <li>
                  <strong>Mots de passe :</strong> Vos mots de passe sont hashés
                  avec des algorithmes sécurisés (bcrypt ou Argon2) et ne sont
                  jamais stockés en clair
                </li>
                <li>
                  <strong>Données bancaires :</strong> Gérées exclusivement par
                  Stripe (certifié PCI-DSS niveau 1). Nous ne stockons aucune
                  donnée bancaire complète sur nos serveurs
                </li>
                <li>
                  <strong>Communications :</strong> Toutes les communications
                  entre votre navigateur et nos serveurs utilisent le protocole
                  HTTPS avec chiffrement TLS 1.3
                </li>
                <li>
                  <strong>Base de données :</strong> Chiffrement des données au
                  repos (encryption at rest)
                </li>
              </ul>

              <h3 className="text-xl font-semibold mb-3 text-gray-800">
                6.2 Contrôle d'accès et surveillance
              </h3>
              <ul className="space-y-2 text-gray-700 list-disc list-inside ml-4 mb-4">
                <li>
                  Authentification forte avec gestion des sessions sécurisées
                </li>
                <li>Gestion des permissions et des rôles</li>
                <li>Logs d'accès et détection des activités suspectes</li>
                <li>Sauvegardes régulières et chiffrées</li>
                <li>Tests de sécurité et audits réguliers</li>
              </ul>

              <h3 className="text-xl font-semibold mb-3 text-gray-800">
                6.3 Notification des violations de données
              </h3>
              <p className="text-gray-700 leading-relaxed">
                Conformément à l'article 33 du RGPD, en cas de violation de
                données à caractère personnel susceptible d'engendrer un risque
                élevé pour vos droits et libertés, nous nous engageons à :
              </p>
              <ul className="space-y-2 text-gray-700 list-disc list-inside ml-4 mt-2">
                <li>
                  Notifier la CNIL dans les <strong>72 heures</strong> suivant
                  la découverte de la violation
                </li>
                <li>
                  Vous informer personnellement dans les{' '}
                  <strong>meilleurs délais</strong> si vos données sont
                  concernées
                </li>
                <li>
                  Vous communiquer les mesures prises pour remédier à la
                  violation et protéger vos données
                </li>
              </ul>
            </section>

            <section id="hebergement" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                7. Hébergement des données
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Vos données sont hébergées au sein de l'Union Européenne :
              </p>
              <ul className="space-y-2 text-gray-700 list-disc list-inside ml-4">
                <li>
                  <strong>Hébergeur :</strong> Scaleway SAS
                </li>
                <li>
                  <strong>Adresse :</strong> BP 438, 75366 Paris Cedex 08,
                  France
                </li>
                <li>
                  <strong>Localisation des serveurs :</strong> Allemagne (Union
                  Européenne)
                </li>
                <li>
                  <strong>Conformité :</strong> Infrastructure conforme aux
                  exigences RGPD
                </li>
              </ul>
              <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mt-4 rounded">
                <p className="text-sm text-blue-700 font-medium">
                  <strong>[À COMPLÉTER]</strong> : Certifications de l'hébergeur
                  (ISO 27001, etc.)
                </p>
              </div>
            </section>

            <section id="droits" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                8. Vos droits
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Conformément au RGPD et à la loi Informatique et Libertés, vous
                disposez des droits suivants concernant vos données personnelles
                :
              </p>

              <div className="space-y-4 mb-6">
                <div className="border-l-4 border-brand pl-4">
                  <h4 className="font-semibold text-gray-800 mb-1">
                    Droit d'accès (Art. 15 RGPD)
                  </h4>
                  <p className="text-gray-700 text-sm">
                    Obtenir une copie de vos données personnelles et des
                    informations sur leur traitement
                  </p>
                </div>

                <div className="border-l-4 border-brand pl-4">
                  <h4 className="font-semibold text-gray-800 mb-1">
                    Droit de rectification (Art. 16 RGPD)
                  </h4>
                  <p className="text-gray-700 text-sm">
                    Corriger vos données inexactes ou incomplètes
                  </p>
                </div>

                <div className="border-l-4 border-brand pl-4">
                  <h4 className="font-semibold text-gray-800 mb-1">
                    Droit à l'effacement (Art. 17 RGPD)
                  </h4>
                  <p className="text-gray-700 text-sm">
                    Demander la suppression de vos données personnelles (sous
                    réserve des obligations légales de conservation)
                  </p>
                </div>

                <div className="border-l-4 border-brand pl-4">
                  <h4 className="font-semibold text-gray-800 mb-1">
                    Droit à la portabilité (Art. 20 RGPD)
                  </h4>
                  <p className="text-gray-700 text-sm">
                    Récupérer vos données dans un format structuré et lisible
                    (JSON ou CSV) pour les transférer à un autre responsable de
                    traitement
                  </p>
                </div>

                <div className="border-l-4 border-brand pl-4">
                  <h4 className="font-semibold text-gray-800 mb-1">
                    Droit d'opposition (Art. 21 RGPD)
                  </h4>
                  <p className="text-gray-700 text-sm">
                    Vous opposer au traitement de vos données à des fins de
                    marketing direct
                  </p>
                </div>

                <div className="border-l-4 border-brand pl-4">
                  <h4 className="font-semibold text-gray-800 mb-1">
                    Droit à la limitation (Art. 18 RGPD)
                  </h4>
                  <p className="text-gray-700 text-sm">
                    Demander la limitation du traitement dans certaines
                    situations
                  </p>
                </div>
              </div>

              <h3 className="text-xl font-semibold mb-3 text-gray-800">
                Comment exercer vos droits ?
              </h3>
              <p className="text-gray-700 leading-relaxed mb-4">
                Pour exercer l'un de ces droits, vous pouvez nous contacter :
              </p>
              <ul className="space-y-2 text-gray-700 list-disc list-inside ml-4 mb-4">
                <li>
                  <strong>Par email :</strong>{' '}
                  <a
                    href="mailto:freelansign@gmail.com"
                    className="text-brand hover:underline"
                  >
                    freelansign@gmail.com
                  </a>
                </li>
                <li>
                  <strong>Objet du message :</strong> "Exercice de mes droits
                  RGPD"
                </li>
                <li>
                  <strong>Pièce d'identité :</strong> Pour des raisons de
                  sécurité, nous pourrons vous demander une copie de votre pièce
                  d'identité
                </li>
              </ul>
              <p className="text-gray-700 leading-relaxed">
                Nous nous engageons à répondre à votre demande dans un délai d'
                <strong>1 mois maximum</strong> à compter de sa réception. Ce
                délai peut être prolongé de 2 mois en cas de complexité ou de
                nombre important de demandes (vous en serez informé).
              </p>
            </section>

            <section id="cookies" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                9. Cookies et traceurs
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Freelansign utilise des cookies uniquement pour le
                fonctionnement technique du service. Aucun cookie publicitaire
                ou de tracking marketing n'est utilisé.
              </p>

              <h3 className="text-xl font-semibold mb-3 text-gray-800">
                Types de cookies utilisés
              </h3>
              <ul className="space-y-2 text-gray-700 list-disc list-inside ml-4 mb-4">
                <li>
                  <strong>Cookies de session :</strong> Nécessaires à
                  l'authentification et au maintien de votre session (supprimés
                  à la fermeture du navigateur)
                </li>
                <li>
                  <strong>Cookies de préférence :</strong> Mémorisation de vos
                  préférences (langue, thème) - durée : 1 an maximum
                </li>
              </ul>

              <p className="text-gray-700 leading-relaxed mb-4">
                <strong>Aucun cookie analytique ou publicitaire :</strong> Nous
                n'utilisons pas Google Analytics, Facebook Pixel ou tout autre
                outil de tracking tiers.
              </p>

              <h3 className="text-xl font-semibold mb-3 text-gray-800">
                Gestion des cookies
              </h3>
              <p className="text-gray-700 leading-relaxed">
                Vous pouvez à tout moment paramétrer votre navigateur pour
                refuser les cookies. Attention, le refus des cookies techniques
                peut empêcher le bon fonctionnement du service (impossibilité de
                se connecter).
              </p>
            </section>

            <section id="transferts" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                10. Transferts internationaux
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Vos données sont hébergées exclusivement au sein de l'Union
                Européenne (Allemagne via Scaleway).
              </p>
              <p className="text-gray-700 leading-relaxed">
                <strong>Stripe (traitement des paiements) :</strong> Stripe Inc.
                est une société américaine soumise aux clauses contractuelles
                types de la Commission Européenne et certifiée conforme au RGPD
                pour les transferts de données.
              </p>
            </section>

            <section id="mineurs" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                11. Mineurs
              </h2>
              <p className="text-gray-700 leading-relaxed">
                Le Service Freelansign est exclusivement destiné aux personnes
                majeures (18 ans révolus). Nous ne collectons pas sciemment de
                données personnelles concernant des mineurs. Si vous avez
                connaissance qu'un mineur a fourni des données, merci de nous
                contacter immédiatement.
              </p>
            </section>

            <section id="modifications" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                12. Modifications de la politique
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Nous nous réservons le droit de modifier la présente Politique
                de Confidentialité à tout moment afin de refléter les évolutions
                légales, réglementaires ou de nos pratiques.
              </p>
              <p className="text-gray-700 leading-relaxed">
                En cas de modification substantielle, vous serez informé par
                email au moins 30 jours avant l'entrée en vigueur des
                changements. La date de "Dernière mise à jour" en haut de cette
                page sera également mise à jour.
              </p>
            </section>

            <section id="reclamation" className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900">
                13. Réclamation auprès de la CNIL
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                Si vous estimez, après nous avoir contactés, que vos droits
                Informatique et Libertés ne sont pas respectés, vous pouvez
                adresser une réclamation à la CNIL (Commission Nationale de
                l'Informatique et des Libertés) :
              </p>
              <ul className="space-y-2 text-gray-700 list-disc list-inside ml-4">
                <li>
                  <strong>En ligne :</strong>{' '}
                  <a
                    href="https://www.cnil.fr/fr/plaintes"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-brand hover:underline"
                  >
                    https://www.cnil.fr/fr/plaintes
                  </a>
                </li>
                <li>
                  <strong>Par courrier :</strong> CNIL - 3 Place de Fontenoy -
                  TSA 80715 - 75334 Paris Cedex 07
                </li>
              </ul>
            </section>

            {/* Contact */}
            <div className="mt-12 pt-6 border-t border-gray-200 text-center">
              <p className="text-gray-600 text-sm mb-2">
                Pour toute question concernant cette politique de
                confidentialité ou l'exercice de vos droits :
              </p>
              <p className="text-gray-900 font-medium">
                <a
                  href="mailto:freelansign@gmail.com"
                  className="text-brand hover:underline"
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
