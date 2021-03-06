function getUrlQuery() {
    var queries = {};
    $.each(document.location.search.substr(1).split('&'),function(c,q){
        var i = q.split('=');
        if (i[0].length > 0) {
            queries[i[0].toString()] = i[1].toString();
        }
    });
    return queries;
}

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

$(document).ready(function() {
    var query = getUrlQuery();
    $('#bid-history-analytics').hide()
    $.get('/bids/totals', function(totals) {
        $('#open-auctions').text(numberWithCommas(totals.open) + ' open');
        $('#closed-auctions').text(numberWithCommas(totals.closed) + ' closed');
    })

    if (query.search) {
        $('#search').val(decodeURIComponent(query.search).replace('+', ' '));
        $.each($(':checkbox[name="sites"]'), function(i, item) {
            if(query.sites && query.sites.indexOf(item.value) >= 0) {
                item.checked;
            }
        })
        $.each($(':checkbox[name="types"]'), function(i, item) {
            if(query.types && query.types.indexOf(item.value) >= 0) {
                item.checked;
            }
        })  
        $('#searchButton').click();
    }
})


$('#searchButton').click(function() {

    // JQuery's Serialize doesn't seem to want to return the data in a format
    // that I want, so I'm interpreting the data by hand now.
    var form = {
        search: $('#search').val(),
        types: [],
        sites: []
    };

    $('[name="types"]:checked').each(function() {
        form.types.push($(this).val());
    });

    $('[name="sites"]:checked').each(function() {
        form.sites.push($(this).val());
    });
    form.sites = form.sites.join(',')
    form.types = form.types.join(',')

    // Hide the help info and show the analytics
    $('#bid-history-help').hide()
    $('#bid-history-analytics').show()
    $('#bhl-content').text( 
        'https://herf.io/bids?search=' + encodeURIComponent(form.search) + 
        '&types=' + form.types + 
        '&sites=' + form.sites
    );

    // Clear out all of the current (if any) pricing information
    $('#avg-price').empty();
    $('#best-price').empty();
    $('#worst-price').empty();
    $('#std-dev').empty();
    $('#median').empty();
    $('#percentile-25').empty();
    $('#percentile-75').empty();
    $('#great-price-range').empty();
    $('#good-price-range').empty();
    $('#poor-price-range').empty();
    $('#bad-price-range').empty();
    $('#price-distribution').empty();
    $('price-trend').empty();
    $('#auction-history-table > tbody').empty();
    $('#open-auctions-table > tbody').empty();


    // Update the Totals to match the search
    $.post('/bids/search/totals', form, function(totals) {
        $('#open-auctions').text(numberWithCommas(totals.open) + ' open');
        $('#closed-auctions').text(numberWithCommas(totals.closed) + ' closed');
    });


    // Get the statistical data and populate the stats tiles
    $.post('/bids/search/stats', form, function(stats) {
        $('#avg-price').text(stats.mean.toFixed(2));
        $('#best-price').text(stats.best.toFixed(2));
        $('#worst-price').text(stats.worst.toFixed(2));
        $('#std-dev').text(stats.stddev.toFixed(2));
        $('#median').text(stats.median.toFixed(2));
        $('#percentile-25').text(stats.topQuarter.toFixed(2));
        $('#percentile-75').text(stats.bottomQuarter.toFixed(2));
        $('#great-price-range').text(stats.great.toFixed(2) + ' - ' + stats.good.toFixed(2));
        $('#good-price-range').text(stats.good.toFixed(2) + ' - ' + stats.mean.toFixed(2));
        $('#poor-price-range').text(stats.mean.toFixed(2) + ' - ' + stats.poor.toFixed(2));
        $('#bad-price-range').text(stats.poor.toFixed(2) + ' - ' + stats.bad.toFixed(2));


        // Get the price distribution and render the graph.  We are running this as a sub-call
        // to the statistical data as we need to use the stats information to generate the
        // histogram markings.
        $.post('/bids/search/distribution', form, function(distribution) {
            $('#price-distribution').height(200);

            // We need to break down the distribution into the various statistical buckets
            // so that we can apply the appropriate colors to them.
            var great = [], good = [], poor = [], bad = [], outside = [];
            $.each(distribution, function(i, item) {
                if (item[0] >= stats.great && item[0] < stats.good){ great.push(item); }
                else if (item[0] >= stats.good && item[0] < stats.mean){ good.push(item); }
                else if (item[0] >= stats.mean && item[0] < stats.poor){ poor.push(item); }
                else if (item[0] >= stats.poor && item[0] < stats.bad){ bad.push(item); }
                else { outside.push(item); }
            });

            // Now to populate the data with the information Flot needs to generate the
            // graph.
            var histogram = [
                {color: '#000', data: outside, bars: {show: true, barWidth: .25, fill: .8}},
                {color: '#357abd', data: great, bars: {show: true, barWidth: .25, fill: .8}},
                {color: '#4cae4c', data: good, bars: {show: true, barWidth: .25, fill: .8}},
                {color: '#fdc431', data: poor, bars: {show: true, barWidth: .25, fill: .8}},
                {color: '#ee9336', data: bad, bars: {show: true, barWidth: .25, fill: .8}},
            ]
            
            // and then to generate the graph :D
            $.plot($('#price-distribution'), histogram, {
                yaxis: {show: true},
                xaxis: {tickDecimals: 2},
                series: {
                    autoMarkings: {
                        enabled: false,
                    }
                },
            });
        })
    });


    // Get the price timeline and render the graph
    $.post('/bids/search/timeline', form, function(timeline) {
        $('#price-trend').height(200);
        var trendline = {
            color: 'rgb(21, 116, 157)',
            data: timeline,
        }
        $.plot($('#price-trend'), [trendline], {
            xaxis: { mode: 'time'},
            series: {
                autoMarkings: {
                    enabled: true,
                    showAvg: true,
                    avgcolor: 'rgb(255,0,0)'
                },
                lines: {
                    zero: false,
                    fill: true,
                    fillColor: 'rgba(21, 140, 186, 0.60)',
        }}});
    });


    // Populate the open auctions
    $.post('/bids/search/open', form, function(rows) {
        $.each(rows, function(k, item) {
            $('#open-auctions-table > tbody').append(
                '<tr>' +
                '<td><a href="' + item.link + '"><span aria-hidden="true" class="glyphicon glyphicon-link"></span></a>' +
                '<td>' + item.name + '</td>' +
                '<td><img src="/static/img/' + item.site + '.png"></td>' +
                '<td>' + item.type + '/<strong>' + item.quantity + '</strong></td>' +
                '<td>' + moment(item.closed).fromNow() + '</td>' +
                '</tr>'
            );
        });
    });


    // Populate the open auctions
    $.post('/bids/search/closed', form, function(rows) {
        $.each(rows, function(k, item) {
            var price = null;
            if (item.type != 'single' && item.price > 0) {
                price = '<strong>' + (item.price / item.quantity).toFixed(2) + '</strong>/<small>' + item.price.toFixed(2) + '</small>';
            } else if (!item.price || item.price == 0) {
                price = '<small>No Sale</small>';
            } else {
                price = '<strong>' + item.price.toFixed(2) + '</strong>';
            }
            $('#auction-history-table > tbody').append(
                '<tr>' +
                '<td><a href="' + item.link + '"><span aria-hidden="true" class="glyphicon glyphicon-link"></span></a>' +
                '<td>' + item.name + '</td>' +
                '<td><img src="/static/img/' + item.site + '.png"></td>' +
                '<td>' + item.type + '/<strong>' + item.quantity + '</strong></td>' +
                '<td>' + moment(item.closed).fromNow() + '</td>' +
                '<td>' + price + '</td>' +
                '</tr>'
            );
        });
    });
    return false;
})