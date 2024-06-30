$(document).ready(function() {
    $('.nav-link').click(function(event) {
        event.preventDefault(); // Prevent the default link behavior
        var pageUrl = $(this).attr('href'); // Get the href attribute of the clicked link
        
        // Use AJAX to load the content of the target page
        $.ajax({
            url: pageUrl,
            success: function(data) {
                $('#content').fadeOut(200, function() {
                    $('#content').html(data); // Insert the new content
                    $('#content').fadeIn(200); // Fade in the new content
                });
            },
            error: function() {
                alert('Error loading page. Please try again.');
            }
        });
    });
});