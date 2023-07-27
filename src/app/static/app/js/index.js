
// Fonction pour récupérer les titres de films depuis l'API sous forme de promesse
function getFilmTitles() {
    return new Promise((resolve, reject) => {
        $.get("get-titles/")
            .done((filmTitles) => resolve(filmTitles))
            .fail((error) => reject(error));
    });
};

// Fonction pour initialiser la liste déroulante avec Select2
function initializeAutoComplete(ageCategory) {

    // Remove old Select2 input if it exists
    $('#filmTitleInput').remove();

    // Create new Select2 input
    let selectInput = $('<input type="text" name="select2" id="filmTitleInput">');
    $('#filmInputContainer').append(selectInput);

    // Appeler la fonction getFilmTitles() pour obtenir les titres de films
    getFilmTitles()
        .then((filmTitles) => {

            const formattedFilmTitles = filmTitles[ageCategory].map(title => ({ id: title, text: title }));

            // Initialiser la liste déroulante avec Select2 en utilisant les titres de films récupérés
            $("#filmTitleInput").select2({
                 // Transformer les titres de films en objets appropriés pour Select2
                data: formattedFilmTitles
            });
        })
        .catch((error) => {
            // Gérer l'erreur en cas d'échec de la récupération des titres de films
            console.error("Error during load films titles :", error);
        });
};

function addTitleChangeListener() {
    // Ajoutez le symbole "#" devant les sélecteurs d'ID pour sélectionner les éléments correctement
    $("#filmTitleInput").on("change", function () {
        const selectedTitle = $(this).select2('data')[0];

        // Vérifiez si un élément a été sélectionné
        if (selectedTitle) {
            const value = selectedTitle.text;
            $("#filmTitleHidden").val(value);
        }
    });
};

// Function to delete filmTitles from localStorage when user leave website
function addBeforeUnloadListener() {
    window.addEventListener("beforeunload", function () {
    // Supprimez les données du localStorage
    localStorage.removeItem("filmTitles");
    });
};

function addSubmitListener() {
    $('#questionnaireForm').on('submit', function(e) {
        if ($("#filmTitleHidden").val() === '') {
            e.preventDefault();
            alert('Veuillez sélectionner un film');
        }
    });
};

// Ajouter un écouteur d'événements pour changer la tranche d'âge
function addAgeCategoryListener() {
    $("#ageCategories").change(function() {
        // Réinitialiser la liste déroulante avec les nouveaux titres de films
        const selectedAgeCategory = $(this).find(".radioAgeCategory:checked").val()

        initializeAutoComplete(selectedAgeCategory);
    });
}

function addListeners() {
    addBeforeUnloadListener();
    addTitleChangeListener();
    addSubmitListener();
    addAgeCategoryListener();
    // Trigger a change event on the currently selected radio button
    $("#ageCategories .radioAgeCategory:checked").trigger('change');
}

// Call functions
$(document).ready(function () {

    addListeners();
});
