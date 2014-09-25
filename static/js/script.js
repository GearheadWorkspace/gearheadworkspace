$(function() {
    // POST to api to track user signup
    $( "form" ).submit(function() {
        var email = $('#mce-EMAIL').val();
        $.ajax({
            type: "POST",
            url: "/subscriber/",
            data: { email: email }
        });
        return;
    });
});
