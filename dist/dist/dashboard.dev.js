"use strict";

document.addEventListener("DOMContentLoaded", function () {
  var quotidiennes = JSON.parse('{{ quotidiennes|tojson|safe }}'); // Configuration du graphique de ventes quotidiennes

  var ctx = document.getElementById('dailyChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Jour 1', 'Jour 2', 'Jour 3', 'Jour 4', 'Jour 5', 'Jour 6', 'Jour 7'],
      datasets: [{
        label: 'Ventes prévues',
        data: quotidiennes,
        borderColor: '#4A90E2',
        backgroundColor: 'rgba(74, 144, 226, 0.2)',
        fill: true
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
});