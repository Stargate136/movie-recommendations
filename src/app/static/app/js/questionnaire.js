function toggleDropdown() {
    var dropdown = document.getElementById("dropdown");
    if (dropdown.style.display === "none") {
        dropdown.style.display = "block";
    } else {
        dropdown.style.display = "none";
    }
}

    // Fonction pour afficher/masquer les éléments en fonction de la valeur sélectionnée
function updateVisibleElements() {
    const selectedFilter = $("#filter").val();
    $(".hidden-choice").hide();
    $("#" + selectedFilter).show();
}

// Écouter les changements dans la liste déroulante
$("#filter").on("change", updateVisibleElements);