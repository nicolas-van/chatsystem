
$(function() {
    var last = null;
    function poll() {
        var data = {"last": last};
        console.log("try");
        $.ajax({
            url: "/poll",
            dataType: 'json',
            type: 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json',
        }).then(function(result) {
            console.log("got it", result);
            last = result.last;
            _.each(result.res, function(mes) {
                $("<div>").text(mes).appendTo($("#messages"));
            });
            poll();
        }, function() {
            poll();
        });
    }
    poll();
    $("#typing").keypress(function(e) {
        if(e.which != 13) {
            return;
        }
        var mes = $("#typing").val();
        $("#typing").val("");
        $.ajax({
            url: "/post",
            dataType: 'json',
            type: 'POST',
            data: JSON.stringify({message: mes}),
            contentType: 'application/json',
        }).then(function(result) {
            console.log("pushed message");
        });
    }).focus();
});