document.body.className = document.body.className
  ? document.body.className + " js-enabled"
  : "js-enabled";

if (window.GOVUKFrontend) {
  window.GOVUKFrontend.initAll();
}

window.addEventListener('load', function() {
  const print_button = document.getElementById("print_button")
  if (print_button) {
    print_button.onclick = () => window.print();
  }
}
)

