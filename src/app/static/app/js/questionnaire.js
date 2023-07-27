// LISTENERS
function addFilterListener() {
    $("#filter").on("change", function() {
        const selectedFilter = $("#filter").val();
        $(".hidden-choice").hide();
        $("#" + selectedFilter).show();
    });
}

// Call functions
$(document).ready(function () {
    addFilterListener();
});
