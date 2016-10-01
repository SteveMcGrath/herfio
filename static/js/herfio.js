var clipboard = new Clipboard('[data-clipboard-demo]');

function showTooltip(elem,msg){
	elem.setAttribute('class', 'btn tooltipped tooltipped-s');
	elem.setAttribute('aria-label', msg);
}

clipboard.on('success',function(e){
	e.clearSelection();
	console.info('Action:',e.action);
	console.info('Text:',e.text);
	console.info('Trigger:',e.trigger);
	showTooltip(e.trigger,'Copied!');
});

clipboard.on('error',function(e){
	console.error('Action:',e.action);
	console.error('Trigger:',e.trigger);
	showTooltip(e.trigger,fallbackMessage(e.action));
});

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

$(document).ready(function() {
	var query = getUrlQuery();
	$('#bid-history-analytics').hide()
	$.get('/bids/totals', function(totals) {
		$('#open-auctions').text(' ' + totals.open);
		$('#closed-auctions').text(' ' + totals.closed);
	})

	if (query.search) {
		$('#search').val(decodeURIComponent(query.search));
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
	var form = $('#searchForm').serializeObject();
	form.types = [];
	form.sites = [];

	$('[name="types"]:checked').each(function() {
    	form.types.push($(this).val());
	});

	$('[name="sites"]:checked').each(function() {
    	form.sites.push($(this).val());
	});

	// Hide the help info and show the analytics
	$('#bid-history-help').hide()
	$('#bid-history-analytics').show()
	$('#get-search-link').attr('data-clipboard-text', function() {
		var directLink = 'https://herf.io/bids?search=' + encodeURIComponent(form.search);
		if (form.types) {
			directLink = directLink + '&types=' + form.types.join(',');
		}
		if (form.sites) {
			directLink = directLink + '&sites=' + form.sites.join(',');
		}
		return directLink;
	})

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
		$('#open-auctions').text(' ' + totals.open);
		$('#closed-auctions').text(' ' + totals.closed);
	}, 'json');


	// Get the statistical data and populate the stats tiles
	$.post('/bids/search/stats', form, function(stats) {
		console.log(stats)
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
			$('#price-distribution').height(100);
			var histogram = {
				color: 'rgba(21, 116, 157, 1)',
				data: distribution,
				bars: {
					show: true,
					barWidth: .25
				}
			}
			
			$.plot($('#price-distribution'), [histogram], {
				yaxis: {show: false},
				xaxis: {tickDecimals: 2},
				grid: {
					markings: [
						{xaxis: {from: stats.great, to: stats.good}, color: '#357abd'},
						{xaxis: {from: stats.good, to: stats.mean}, color: '#4cae4c'},
						{xaxis: {from: stats.mean, to: stats.poor}, color: '#fdc431'},
						{xaxis: {from: stats.poor, to: stats.bad}, color: '#ee9336'}
			]}});
		}, 'json')
	}, 'json');


	// Get the price timeline and render the graph
	$.post('/bids/search/timeline', form, function(timeline) {
		$('#price-trend').height(100);
		var trendline = {
			color: 'rgba(21, 116, 157, 1)',
			data: timeline,
		}
        $.plot($('#price-trend'), [trendline], {
            xaxis: { mode: 'time'},
            series: {lines: {
                fill: true,
                fillColor: 'rgba(21, 140, 186, 0.60)',
        }}});
	}, 'json');


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
	}, 'json');


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
	}, 'json');
	return false;
})