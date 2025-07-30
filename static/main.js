document.body.className += ' js-enabled' + ('noModule' in HTMLScriptElement.prototype ? ' govuk-frontend-supported' : '');

if (window.GOVUKFrontend) {
  window.GOVUKFrontend.initAll();
}