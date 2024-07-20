function setDropDown(el) {
    if (el.getAttribute('data-dropdown-id')) {
        el = document.getElementById(el.getAttribute('data-dropdown-id'));

    }
    const dropdownMenu = el.querySelector('.dropdown-menu');
    document.querySelectorAll('.dropdown').forEach(dropdown => {
        if (dropdown !== el) {
            dropdown.classList.remove('is-active');
            if (dropdown.getAttribute('data-dropdown-trigger-id')) {
                document.getElementById(
                    dropdown.getAttribute('data-dropdown-trigger-id')
                ).classList.remove('is-active');
            }
        }
        else if (dropdownMenu.contains(el)) {}
        else if (dropdown === el) {
            dropdown.classList.toggle('is-active');
            if (dropdown.getAttribute('data-dropdown-trigger-id')) {
                document.getElementById(
                    dropdown.getAttribute('data-dropdown-trigger-id')
                ).classList.toggle('is-active');
            }
        }
    })
}

function removeModal(modalId) {
    document.getElementById(modalId).remove()
}
