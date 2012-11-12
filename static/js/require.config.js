var jam = {
    "packages": [
        {
            "name": "jquery",
            "location": "static/js/jquery",
            "main": "jquery.js"
        },
        {
            "name": "underscore",
            "location": "static/js/underscore",
            "main": "underscore.js"
        }
    ],
    "version": "0.2.3",
    "shim": {}
};

if (typeof require !== "undefined" && require.config) {
    require.config({packages: jam.packages, shim: jam.shim});
}
else {
    var require = {packages: jam.packages, shim: jam.shim};
}

if (typeof exports !== "undefined" && typeof module !== "undefined") {
    module.exports = jam;
}