(function () {
  var url = pm.globals.get("POSTMAN_TOOLKIT_URL");
  pm.sendRequest(url + "/config", function (err, response) {
    var c = response.json().content;
    for (var i = 0; i < c.length; i++) {
      pm.environment.set(c[i].name, c[i].value);
    }
  });
})();
