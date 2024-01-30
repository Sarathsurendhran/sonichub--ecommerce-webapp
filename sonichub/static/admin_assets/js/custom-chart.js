(function ($) {
    "use strict";

    // Initialize the chart data with empty arrays
    let initialData = {
        labels: [],
        datasets: [
            {
                label: 'Sales',
                tension: 0.2,
                fill: true,
                backgroundColor: 'rgba(44,220,185,0.2)',
                borderColor: 'rgb(44,217,220)',
                data: []
            }
        ]
    };
    let ctx = document.getElementById('myChart').getContext('2d');
    let chart = new Chart(ctx, {
        type: 'line',
        data: initialData,
        options: {
            plugins: {
                legend: {
                    labels: {
                        usePointStyle: true,
                    },
                }
            },
            scales: {
                y: {
                    suggestedMin: 0,
                    suggestedMax: 10,
                    beginAtZero: true,
                }
            }
        }
    });

    function updateChart(newData) {
        chart.data.labels = Object.keys(newData);
        chart.data.datasets[0].data = Object.values(newData);
        chart.update();
    }

    function fetchData(url, successCallback) {
        
        $.ajax({
            
            type: 'GET',
            url: url,
            // crossDomain : true,
            success: successCallback,
            error: function (error) {
                console.log('Error:', error);
            }
        });
    }

    
    // Make an initial AJAX request to get the default data (monthly data)
               
    fetchData('fetchData/month', function (monthlyData) { updateChart(monthlyData.response)  });
    

    $('#dailyButton').on('click', function () {
        fetchData('fetchData/week' , function (dailyData) { updateChart(dailyData.response) });
    });

    $('#MonthlyButton').on('click', function () {
        
        fetchData('fetchData/month', function (monthlyData) { updateChart(monthlyData.response) });
    });

    $('#YearlyButton').on('click', function () {
        fetchData('fetchData/year', function (yearlyData) { updateChart(yearlyData.response) });
    });
})(jQuery);