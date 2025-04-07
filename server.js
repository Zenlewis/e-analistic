const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
    res.send('Le serveur fonctionne correctement !');
});

app.listen(PORT, () => {
    console.log(`Le serveur fonctionne sur le port ${PORT}`);
});
