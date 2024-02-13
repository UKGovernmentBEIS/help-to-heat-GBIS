const downloadReferralsFromDateRangeForm = document.getElementById("download-referrals-from-date-range");

function clearDateErrors() {
  const errorElements = document.querySelectorAll(".govuk-error-summary,.govuk-error-message");
  for (const errorElement of [...errorElements]) {
    errorElement.remove();
  }
  removeClassFromAllElements("govuk-form-group--error");
  removeClassFromAllElements("govuk-input--error");
}

function removeClassFromAllElements(className) {
  const elements = document.getElementsByClassName(className);
  for (const element of [...elements]) {
    element.classList.remove(className);
  }
}

downloadReferralsFromDateRangeForm.addEventListener("submit", clearDateErrors);
