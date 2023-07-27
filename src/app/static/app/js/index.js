// Function to retrieve movie titles from the API as a Promise
function getFilmTitles() {
    return new Promise((resolve, reject) => {
        $.get("get-titles/")
            .done((filmTitles) => resolve(filmTitles))
            .fail((error) => reject(error));
    });
};

// Function to initialize the drop-down list with Select2
function initializeAutoComplete(ageCategory) {

    // Remove old Select2 input if it exists
    $('#filmTitleInput').remove();

    // Create new Select2 input
    let selectInput = $('<input type="text" name="select2" id="filmTitleInput">');
    $('#filmInputContainer').append(selectInput);

    // Call the getFilmTitles() function to get film titles
    getFilmTitles()
        .then((filmTitles) => {

            const formattedFilmTitles = filmTitles[ageCategory].map(title => ({ id: title, text: title }));

            // Initialize the drop-down list with Select2 using the retrieved film titles
            $("#filmTitleInput").select2({
                 // Transformer les titres de films en objets appropriés pour Select2
                data: formattedFilmTitles
            });
        })
        .catch((error) => {
            // Error handling in case of failed movie title retrieval
            console.error("Error during load films titles :", error);
        });
};


// LISTENERS
function addTitleChangeListener() {
    $(document).on("change", "#filmTitleInput", function () {
        const selectedTitle = $(this).select2('data')[0];

        if (selectedTitle) {
            const value = selectedTitle.text;
            $("#filmTitleHidden").val(value);
            
            console.log(`Selected title: ${value}`);
        }
    });
};

function addBeforeUnloadListener() {
    window.addEventListener("beforeunload", function () {
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

function addAgeCategoryListener() {
    $("#ageCategories").change(function() {
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
