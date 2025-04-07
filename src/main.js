document.addEventListener("DOMContentLoaded", () => {
    const translations = {
        fr: {
            heroTitle: "Transformez Vos Données E-commerce en Opportunités Concrètes",
            heroDescription: "Avec E-Analistic, exploitez vos données...",
            heroButton: "Démarrer l'Essai Gratuit",
            aboutTitle: "À Propos de Nous",
            aboutDescription: "E-Analistic est la plateforme ultime...",
            featuresTitle: "Découvrez Nos Fonctionnalités",
            featureSales: "Analyse des Ventes",
            featureReports: "Rapports Personnalisés",
            featureForecasts: "Prévisions Intelligentes",
            contactTitle: "Contactez Notre Équipe",
            contactDescription: "Écrivez-nous à support@e-analistic.com.",
            footerText: "© 2025 E-Analistic. Tous droits réservés.",
            footerPrivacy: "Politique de confidentialité",
            footerTerms: "Conditions d'utilisation"
        },
        en: {
            heroTitle: "Transform Your E-commerce Data Into Opportunities",
            heroDescription: "With E-Analistic, harness your data...",
            heroButton: "Start Free Trial",
            aboutTitle: "About Us",
            aboutDescription: "E-Analistic is the ultimate platform...",
            featuresTitle: "Discover Our Features",
            featureSales: "Sales Analysis",
            featureReports: "Customized Reports",
            featureForecasts: "Intelligent Forecasting",
            contactTitle: "Contact Our Team",
            contactDescription: "Write to us at support@e-analistic.com.",
            footerText: "© 2025 E-Analistic. All rights reserved.",
            footerPrivacy: "Privacy Policy",
            footerTerms: "Terms of Use"
        }
    };

    function changeLanguage() {
        const selectedLanguage = document.getElementById("language-select").value;
        if (translations[selectedLanguage]) {
            document.getElementById("hero-title").innerText = translations[selectedLanguage].heroTitle;
            document.getElementById("hero-description").innerText = translations[selectedLanguage].heroDescription;
            document.getElementById("hero-button").innerText = translations[selectedLanguage].heroButton;
            document.getElementById("about-title").innerText = translations[selectedLanguage].aboutTitle;
            document.getElementById("about-description").innerText = translations[selectedLanguage].aboutDescription;
            document.getElementById("features-title").innerText = translations[selectedLanguage].featuresTitle;
            document.getElementById("feature-sales").innerText = translations[selectedLanguage].featureSales;
            document.getElementById("feature-reports").innerText = translations[selectedLanguage].featureReports;
            document.getElementById("feature-forecasts").innerText = translations[selectedLanguage].featureForecasts;
            document.getElementById("contact-title").innerText = translations[selectedLanguage].contactTitle;
            document.getElementById("contact-description").innerText = translations[selectedLanguage].contactDescription;
            document.getElementById("footer-text").innerText = translations[selectedLanguage].footerText;
            document.getElementById("footer-privacy").innerText = translations[selectedLanguage].footerPrivacy;
            document.getElementById("footer-terms").innerText = translations[selectedLanguage].footerTerms;
        }
    }

    document.getElementById("language-select").addEventListener("change", changeLanguage);

    // Initialisation
    const defaultLanguage = "fr";
    document.getElementById("language-select").value = defaultLanguage;
    changeLanguage();
});
