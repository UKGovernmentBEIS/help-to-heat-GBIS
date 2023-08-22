window.addEventListener('load', function() {
    const print_elements_to_show = Array.from(document.querySelectorAll('[data-show-if-can-print]'));
    const print_buttons = Array.from(document.querySelectorAll('[data-print'));
    print_elements_to_show.forEach((el) => {
      el.hidden = false;
    })

    print_buttons.forEach((el) => {
      el.addEventListener('click', function() {
        window.print();
      })
    })
  }
)