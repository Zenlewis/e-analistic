"use strict";

var express = require('express');

var app = express();
var PORT = process.env.PORT || 3000;
app.get('/', function (req, res) {
  res.send('Le serveur fonctionne correctement !');
});
app.listen(PORT, function () {
  console.log("Le serveur fonctionne sur le port ".concat(PORT));
});
//# sourceMappingURL=server.dev.js.map
