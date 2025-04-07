"use strict";

function _slicedToArray(r, e) { return _arrayWithHoles(r) || _iterableToArrayLimit(r, e) || _unsupportedIterableToArray(r, e) || _nonIterableRest(); }
function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function _unsupportedIterableToArray(r, a) { if (r) { if ("string" == typeof r) return _arrayLikeToArray(r, a); var t = {}.toString.call(r).slice(8, -1); return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? _arrayLikeToArray(r, a) : void 0; } }
function _arrayLikeToArray(r, a) { (null == a || a > r.length) && (a = r.length); for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e]; return n; }
function _iterableToArrayLimit(r, l) { var t = null == r ? null : "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t["return"] && (u = t["return"](), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }
function _arrayWithHoles(r) { if (Array.isArray(r)) return r; }
var translations = {
  fr: {},
  en: {}
};

// Charger les traductions depuis les fichiers JSON
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
  } else {
    var _translations$selecte, _translations$selecte2;
    console.error("La langue sélectionnée n'est pas disponible dans les traductions.");
    console.log("signupRedirect:", (_translations$selecte = translations[selectedLanguage]) === null || _translations$selecte === void 0 ? void 0 : _translations$selecte.signupRedirect);
    console.log("signupLink:", (_translations$selecte2 = translations[selectedLanguage]) === null || _translations$selecte2 === void 0 ? void 0 : _translations$selecte2.signupLink);
  }
}

// Initialiser la langue par défaut
document.addEventListener("DOMContentLoaded", function () {
  var languageSelector = document.getElementById('language-select');
  if (languageSelector) {
    languageSelector.value = 'en'; // Langue par défaut
  }
  changeLanguage(); // Appliquer la langue au chargement
});