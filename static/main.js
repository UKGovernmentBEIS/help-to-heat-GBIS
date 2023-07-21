document.body.className = document.body.className
  ? document.body.className + " js-enabled"
  : "js-enabled";

window.GOVUKFrontend.initAll();

window.onload = () => {
  const hideButton = document.getElementById("hideButton");
  const cookieBanner = document.getElementById("cookie-banner");

  const cookiesAccepted = document.cookie
    .split(";")
    .some((item) => item.trim().startsWith("cookiesAccepted="));

  if (!cookiesAccepted) {
    cookieBanner.classList.remove("hidden");
    cookieBanner.classList.add("visible");
  }

  hideButton.addEventListener("click", () => {
    const date = new Date();
    date.setFullYear(date.getFullYear() + 1);

    document.cookie =
      "cookiesAccepted=True; expires=" + date.toUTCString() + "; path=/";

    cookieBanner.classList.remove("visible");
    cookieBanner.classList.add("hidden");
  });
};
