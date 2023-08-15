const cookiesAccepted = document.cookie
      .split(";")
      .some((item) => item.trim().startsWith("cookiesAccepted="));

if (cookiesAccepted) {
  window.dataLayer = window.dataLayer || [];
  function gtag() {
    dataLayer.push(arguments);
  }
  gtag("js", new Date());
  gtag("config", "{{gtag_id}}");
  console.log("gtagged");
}
