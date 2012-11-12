
$(function() {
    function poll() {
        var data = {"param": 2};
        console.log("try");
        $.ajax({
            url: "/poll",
            dataType: 'json',
            type: 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json',
        }).then(function(result) {
            console.log("got it", result);
            $("<div>").text(result.res).appendTo($("#messages"));
            poll();
        });
    }
    poll();
    $("#send").click(function() {
        var mes = $("#typing").val();
        $.ajax({
            url: "/post",
            dataType: 'json',
            type: 'POST',
            data: JSON.stringify({message: mes}),
            contentType: 'application/json',
        }).then(function(result) {
            console.log("pushed message");
        });
    });
});