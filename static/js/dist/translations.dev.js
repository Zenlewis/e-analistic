"use strict";

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance"); }

function _iterableToArrayLimit(arr, i) { if (!(Symbol.iterator in Object(arr) || Object.prototype.toString.call(arr) === "[object Arguments]")) { return; } var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

var translations = {
  fr: {},
  en: {}
}; // Charger les traductions depuis les fichiers JSON

Promise.all([fetch('/static/translations/fr.json').then(function (response) {
  return response.json();
}), fetch('/static/translations/en.json').then(function (response) {
  return response.json();
})]).then(function (_ref) {
  var _ref2 = _slicedToArray(_ref, 2),
      frTranslations = _ref2[0],
      enTranslations = _ref2[1];

  translations.fr = frTranslations;
  translations.en = enTranslations;
  changeLanguage(); // Appeler la fonction après le chargement des traductions
});
var signupUrl = "/login_and_config"; // URL statique ou dynamique de l'inscription

function changeLanguage() {
  var selectedLanguage = document.getElementById('language-select').value; // Récupérer la langue sélectionnée

  if (translations[selectedLanguage]) {
    // Mettre à jour dynamiquement le contenu des éléments avec les traductions
    document.getElementById('signup-redirect').innerHTML = translations[selectedLanguage].signupRedirect + '<a href="' + signupUrl + '" class="btn-link" id="signup-link">' + translations[selectedLanguage].signupLink + '</a>';
    document.getElementById('hero-title').innerText = translations[selectedLanguage].welcome;
    document.getElementById('hero-description').innerText = translations[selectedLanguage].description;
    document.getElementById('start-now-btn').innerText = translations[selectedLanguage].startNow;
    document.getElementById('about-title').innerText = translations[selectedLanguage].aboutUs;
    document.getElementById('about-description').innerText = translations[selectedLanguage].aboutDescription;
    document.getElementById('features-title').innerText = translations[selectedLanguage].features;
    document.getElementById('feature-sales').innerText = translations[selectedLanguage].featureSales;
    document.getElementById('feature-reports').innerText = translations[selectedLanguage].featureReports;
    document.getElementById('feature-forecasts').innerText = translations[selectedLanguage].featureForecasts;
    document.getElementById('feature-insights').innerText = translations[selectedLanguage].featureInsights;
    document.getElementById('feature-shopify').innerText = translations[selectedLanguage].featureShopify;
    document.getElementById('contact-title').innerText = translations[selectedLanguage].contactUs;
    document.getElementById('contact-description').innerHTML = translations[selectedLanguage].contactDescription;
    document.getElementById('config-title').innerText = translations[selectedLanguage].configTitle;
    document.getElementById('config-description').innerText = translations[selectedLanguage].configDescription;
    document.getElementById('email-label').innerText = translations[selectedLanguage].emailLabel;
    document.getElementById('password-label').innerText = translations[selectedLanguage].passwordLabel;
    document.getElementById('confirm-password-label').innerText = translations[selectedLanguage].confirmPasswordLabel;
    document.getElementById('shop-url-label').innerText = translations[selectedLanguage].shopUrlLabel;
    document.getElementById('api-key-label').innerText = translations[selectedLanguage].apiKeyLabel;
    document.getElementById('api-secret-label').innerText = translations[selectedLanguage].apiSecretLabel;
    document.getElementById('signup-button').innerText = translations[selectedLanguage].signupButton;
    document.getElementById('login-redirect').innerHTML = translations[selectedLanguage].loginRedirect + '<a href="/login" class="btn-link" id="login-link">' + translations[selectedLanguage].loginLink + '</a>';
    document.getElementById('login-title').innerText = translations[selectedLanguage].loginTitle;
    document.getElementById('login-description').innerText = translations[selectedLanguage].loginDescription;
    document.getElementById('login-button').innerText = translations[selectedLanguage].loginButton;
    document.querySelector('.hero-content h1').innerText = translations.heroTitle;
    document.querySelector('.hero-content p').innerText = translations.heroDescription;
    document.querySelector('.btn-primary').innerText = translations.heroButton;
    document.querySelector('#about .about-content h2').innerText = translations.aboutTitle;
    document.querySelector('#about .about-content p').innerText = translations.aboutDescription;
    document.querySelector('#features h2').innerText = translations.featuresTitle;
    document.querySelector('#contact .contact-section h2').innerText = translations.contactTitle;
    document.querySelector('#contact .contact-section p').innerHTML = `${translations.contactDescription} <a href="mailto:support@e-analistic.com" class="contact-link">support@e-analistic.com</a>.`;
  } else {
    console.error("La langue sélectionnée n'est pas disponible dans les traductions.");
  }
} // Initialiser la langue par défaut


document.addEventListener("DOMContentLoaded", function () {
  var languageSelector = document.getElementById('language-select');

  if (languageSelector) {
    languageSelector.value = 'en'; // Langue par défaut
  }

  changeLanguage(); // Appliquer la langue au chargement
});
//# sourceMappingURL=translations.dev.js.map
