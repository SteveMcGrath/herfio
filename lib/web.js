var config = require('config');
var express = require('express')
    , session = require('express-session')
    , logger = require('express-logger')
    , bodyParser = require('body-parser')
    , cookieParser = require('cookie-parser')
    , striptags = require('striptags')
    , passport = require('passport')
    , email = require('emailjs').email
    , crypto = require('crypto')
    , Stats = require('fast-stats').Stats
    , RedditStrategy = require('passport-reddit').Strategy;
var app = express();
var http = require('http').Server(app);


// MongoDB Connection and setup
const db = require('monk')(config.MongoDB.database)
const humidors = db.get('humidors')
const auctions = db.get('auctions')


// Use the RedditStrategy within Passport.
//   Strategies in Passport require a `verify` function, which accept
//   credentials (in this case, an accessToken, refreshToken, and Reddit
//   profile), and invoke a callback with a user object.
passport.use(new RedditStrategy({
    clientID: config.Reddit.clientID,
    clientSecret: config.Reddit.clientSecret,
    callbackURL: config.Reddit.callback
  },
  function(accessToken, refreshToken, profile, done) {
    process.nextTick(function () {
      return done(null, profile);
    });
  }
))


// Passport Serializer
passport.serializeUser(function(user, done) {
  done(null, user);
})


// Passport Deserializer
passport.deserializeUser(function(obj, done) {
  done(null, obj);
})


// Express setup
app.set('view engine', 'jade');
app.use(logger({path: config.AppServer.logfile}));
app.use(session({secret: config.AppServer.sessionSecret}))
app.use(cookieParser());
app.use(bodyParser());
app.use('/static', express.static(config.AppServer.static))
app.use(passport.initialize());
app.use(passport.session());


// Simple route middleware to ensure user is authenticated.
//   Use this route middleware on any resource that needs to be protected.  If
//   the request is authenticated (typically via a persistent login session),
//   the request will proceed.  Otherwise, the user will be redirected to the
//   login page.
function ensureAuthenticated(req, res, next) {
  if (req.isAuthenticated()) { return next(); }
  req.session.returnTo = req.path;
  res.redirect('/login');
}

// Rounding to Two Decimals
//   This function (listed from Stack Overvlow) attempts to round down to
//   two places and also attemps to compensate for potential mathmatical
//   variances.
function roundToTwo(num) {    
    return +(Math.round(num + "e+2")  + "e-2");
}


// BidHistory Query Builder
//   
function buildBidQuery(req) {
    var search = ''
    if (req.body.exact) {

        // If the exact parameter is set, then we will use the search string
        // verbatim and will not parse any further.
        search = '"' + striptags(req.body.search) + '"'
    } else {

        // The default behavior is to interpret the results of the search parameter
        // and to construct a text search string that Mongo will then handle each
        // word as a logical AND.
        var words = striptags(req.body.search).trim().split(/ +/)
        for (var i in words) {

            // If the word starts with a "-" symbol, then we will pass the word
            // without quotes, as this is a negative expression.
            if (words[i][0] != '-' ) {
                search = search + ' "' + words[i] + '"'
            } else {
                search = search + ' ' + words[i]
            }
        }
    }

    // Lets trim out any remaining extra whitespace and construct the base query
    var query = {$text: {$search: search.trim()}};

    // If the site parameter is present, then lets use it.
    if (req.body.site) {
        query.site = {$in: striptags(req.body.site).split(',')};
    }

    // Same thing with the auction type.  If it's present, then lets use it, however
    // if we don't have a category set, then we will (by default) want to exclude 
    // sampler packs.  Sampler packs have a tendency to skew the result-set and the
    // metrics, and we generally dont want them.  We will NOT however set the negative
    // sampler filter if the exact flag is set, as it's possible that we then actually
    // want the sampler data.
    if (req.body.type) {
        query.type = {$in: striptags(req.body.type).split(',')};
    } else {
        if (!req.body.exact) {
            query.type = {$ne: 'sampler'}
        }
    }
    return query;
}


// GET /auth/reddit
//   Use passport.authenticate() as route middleware to authenticate the
//   request.  The first step in Reddit authentication will involve
//   redirecting the user to reddit.com.  After authorization, Reddit
//   will redirect the user back to this application at /auth/reddit/callback
//
//   Note that the 'state' option is a Reddit-specific requirement.
app.get('/auth/reddit', function(req, res, next){
    req.session.state = crypto.randomBytes(32).toString('hex');
    passport.authenticate('reddit', {
        state: req.session.state,
    })(req, res, next);
})


// GET /auth/reddit/callback
//   Use passport.authenticate() as route middleware to authenticate the
//   request.  If authentication fails, the user will be redirected back to the
//   login page.  Otherwise, the primary route function function will be called,
//   which, in this example, will redirect the user to the home page.
app.get('/auth/reddit/callback', function(req, res, next){
    // Check for origin via state token
    if (req.query.state == req.session.state){
        var returnTo = req.session.returnTo;
        delete req.session.returnTo;
        passport.authenticate('reddit', {
            successRedirect: returnTo,
            failureRedirect: '/login'
        })(req, res, next);
    } else {
        next( new Error(403) );
    }
})


// GET /login
//   As reddit is our authentication machanism, lets go ahead and set the returnTo
//   path and just redirect to /auth/reddit
app.get('/login', function(req, res) {
    if (!req.session.returnTo) { req.session.returnTo = '/' }
    res.redirect('/auth/reddit')
})


// GET /logout
//   Clears out whatever authentication cookies and session sookies that we may be
//   storing and logout.
app.get('/logout', function(req, res){
    req.logout();
    res.redirect('/');
})


// GET /
//   The application homepage! \o/
app.get('/', function(req, res) {
    res.render('index', {user: req.user})
})


// ------------------------------------------------------------------------------------ \\
//                                      BIDHISTORY                                      \\
// ------------------------------------------------------------------------------------ \\


// GET /bids
//   The BidHistory front-end page.  This page front-ends all of the calls to the API.
app.get('/bids', function(req, res) {
    res.render('bidIndex', {user: req.user})
})


// GET /bids/totals
//   Get the current cound of open and closed auctions and returns the resulting JSON.
app.get('/bids/totals', function(req, res) {
    auctions.count({state: 'open'}).then(function(openCount) {
        auctions.count({state: 'closed'}).then(function(closedCount) {
            return res.send({
                open: openCount,
                closed: closedCount
            })
        })
    })
})


// POST /bids/search/closed
//   Returns the list of closed auctions.
app.post('/bids/search/closed', function(req, res) {
    var query = buildBidQuery(req);
    query.state = 'closed'
    auctions.find(query, {fields: {_id: -1}}).then(function(docs) {
        res.send(docs)
    })
})


// POST /bids/search/open
//   Returns the list of currently open auctions that the BidHistory parser
//   is tracking.
app.post('/bids/search/open', function(req, res) {
    var query = buildBidQuery(req);
    query.state = 'open'
    auctions.find(query, {fields: {_id: -1}}).then(function(docs) {
        res.send(docs)
    })
})


// POST /bids/search/timeline
//   Returns an array of prices over time from oldest to newest.
app.post('/bids/search/timeline', function(req, res) {
    var query = buildBidQuery(req);
    var timeline = []
    query.pricePerStick = {$ne: null}
    query.state = 'closed'
    auctions.find(query, {fields: {pricePerStick: 1, closed: 1, _id: -1}}).each(function(doc) {
        timeline.push([doc.closed, roundToTwo(doc.pricePerStick)])
    }).then(function() {
        timeline.sort(function(a, b) {return b[0]-a[0];})
        return res.send(timeline)
    })
})


// POST /bids/search/stats
//   Returns the metrics used to drive the pricing data for
//   BidHistory.
app.post('/bids/search/stats', function(req, res){
    var stats = new Stats()
    var query = buildBidQuery(req);
    query.pricePerStick = {$ne: null}
    query.state = 'closed'
    auctions.find(query, {fields: {pricePerStick: 1}}).each(function (doc) {
        stats.push(doc.pricePerStick)
    }).then(function() {
        return res.send({
            bottomQuarter: roundToTwo(stats.percentile(75)),
            topQuarter: roundToTwo(stats.percentile(25)),
            median: roundToTwo(stats.percentile(50)),
            mean: roundToTwo(stats.amean()),
            stddev: roundToTwo(stats.stddev()),
            moe: roundToTwo(stats.moe()),
            good: roundToTwo(stats.amean() - stats.stddev()),
            great: roundToTwo(stats.amean() - (stats.stddev() * 2)),
            poor: roundToTwo(stats.amean() + stats.stddev()),
            bad: roundToTwo(stats.amean() + (stats.stddev() * 2)),
            best: roundToTwo(stats.min),
            worst: roundToTwo(stats.max),
            count: stats.length
        })
    })
})


// ------------------------------------------------------------------------------------ \\
//                                      HUMITRACK                                       \\
// ------------------------------------------------------------------------------------ \\


app.get('/humidors/list', ensureAuthenticated, function(req, res) {
    humidors.find({user_id: req.user.id}).then(function(docs) {
        res.render('humidors', {humidors: docs, user: req.user})
    }).catch(function(err) {

    })
})


app.get('/humidors/info/:id', ensureAuthenticated, function(req, res) {
    var id = req.params.id;
    if (id == 'new') {id = '000000000000'}
    humidors.findOne({_id: id}).then(function(doc) {
        res.render('humidor_info', {humidor: doc, user: req.user})
    }).catch(function(err) {
        console.log(err)
    })
})


app.post('/humidors/info/new', ensureAuthenticated, function(req, res) {
    humidors.insert({
        user_id: req.user.id, 
        last_alarm: 0,
        name: req.body.name,
        location: req.body.location,
        email: req.body.email,
        limits: {
            temperature: {
                high: req.body.temp_high,
                low: req.body.temp_low
            },
            humidity: {
                high: req.body.hum_high,
                low: req.body.hum_low
            }
        },
        readings: []
    }).then(function(doc) {
        res.redirect('/humidors/info/' + doc._id)
    }).catch(function(err) {
        console.log(err)
    })
})


app.post('/humidors/info/:id', ensureAuthenticated, function(req, res){
    if (req.body.delete) {
        humidors.remove({_id: req.params.id}).then(function() {
            res.redirect('/humidors/list')
        })
    } else {
        humidors.findAndModify({
            query: {_id: req.params.id},
            update: {$set: {
                name: req.body.name,
                location: req.body.location,
                email: req.body.email,
                limits: {
                    temperature: {
                        high: req.body.temp_high,
                        low: req.body.temp_low
                    },
                    humidity: {
                        high: req.body.hum_high,
                        low: req.body.hum_low
                    }
                }
            }}
        }).then(function(doc) {
            res.redirect('/humidors/info/' + doc._id)
        }).catch(function(err) {
            console.log(err)
        })
    }
})


app.post('/humidors/update', function(req, res) {
    if (req.body.humidor && req.body.temperature && req.body.humidity){
        timestamp = Date.now();
        console.log('Humidor: ' + req.body.humidor + ' Temp: ' + req.body.temperature + ' Humidity: ' + req.body.humidity)
        humidors.findAndModify({
            query: {_id: req.body.humidor}, 
            update: {$addToSet: {'readings': {
                temperature: req.body.temperature, 
                humidity: req.body.humidity, 
                timestamp: timestamp
            }}}
        }).then(function(doc) {
            // Here we want to check to see if any alarms have been triggered.  We also want to
            // make sure that we dont constantly spam the person, so we will alarm once, and then
            // silence the alarm for 24hrs.
            if ((  req.body.temperature >= doc.limits.temperature.high
                || req.body.temperature <= doc.limits.temperature.low
                || req.body.humidity >= doc.limits.humidity.high
                || req.body.humidity <= doc.limits.humidity.low)
                && (timestamp - 86400000) <= doc.last_alarm)
            {
                console.log('Humidor Alarm on ' + doc._id + 'Temp: ' + doc.limits.temperature.high + '{' + req.body.temperature + '}' + doc.limits.temperature.high + ' Humidity: ' + doc.limits.humidity.high + '{' + req.body.humidity + '}' + doc.limits.humidity.low)
                doc.last_alarm = timestamp;
            }

            res.send('{"status": "updated"}')
        }).catch(function(err) {
            console.log(err)
        })
    } else {
        res.send('{"status": "error"}')
    }
})


http.listen(config.AppServer.port, function() {
    console.log('Application Web Server is listening on *:' + config.AppServer.port);
})