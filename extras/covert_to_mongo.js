#!/usr/bin/env node
const db = require('monk')('localhost/herfio');
const auctions = db.get('auctions');
var mysql = require('mysql')
var async = require('async')

var pool = mysql.createPool({
	connectionLimit: 100,
	host: 'localhost',
	user: 'bidhistory',
	password: 'bidhistory',
	database: 'bidhistory'
})

var done = false
var count = 0 

var queue = async.queue(function (auction, callback) {
	count++;
	var state = auction.finished ? 'closed': 'open'
	var pps = null;
	if (state == 'closed' && auction.price) {
		pps = auction.price / auction.quantity;
	}
	auctions.insert({
		name: auction.name,
		type: auction.type,
		price: auction.price,
		quantity: auction.quantity,
		auctionId: auction.aid,
		site: auction.site,
		link: auction.link,
		state: state,
		pricePerStick: pps,
		created: auction.timestamp.getTime(),
		closed: auction.close.getTime()
	}).then(function (doc) {
		console.log(doc._id + ':' + doc.name)
	}).catch(function (err) {
		console.log('[!] ERROR: ' + err)
	}).then(callback)
}, 1000)

queue.drain = function() {
	if (!done) {return}
	pool.end(function(err) {
		console.log('Completed ' + count);
		process.exit();
	})
}

pool.getConnection(function(err, connection) {
	connection.query('SELECT * FROM auctions')
		.on('error', function(err) {
			console('[!] CRITICAL: ' + err)
		})
		.on('result', function(row) {
			queue.push(row)
		})
		.on('end', function() {
			done = true;
			console.log('[*] No more rows to add to queue.')
		})
})