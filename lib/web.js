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
    , RedditStrategy = require('passport-reddit').Strategy;
//    , async = require('async')
var app = express();
var http = require('http').Server(app);
//var io = require('socket.io')(http);

// Lets connect to the database backend
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


passport.serializeUser(function(user, done) {
  done(null, user);
})


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


app.get('/login', function(req, res) {
    if (!req.session.returnTo) { req.session.returnTo = '/' }
    res.redirect('/auth/reddit')
})


app.get('/logout', function(req, res){
    req.logout();
    res.redirect('/');
})


app.get('/', function(req, res) {
    res.render('index', {user: req.user})
})


app.get('/bids', function(req, res) {
    res.render('bidIndex', {user: req.user})
})


app.get('/bids/exact/:search', function(req, res){
    var query = {name: req.params.search}
    if (req.query.site) {
        query.site = req.query.site
    }
    if (req.query.category) {
        query.category = req.query.category
    }
})

app.get('/bids/search/:search', function(req, res){
    var query = {};
    if (req.query.exact) {
        query = {$text: {$search: '"' + striptags(req.params.search) + '"', $options: 'i'}};
    } else {
        query = {$text: {$search: striptags(req.params.search), $options: 'i'}};
    }
    if (req.query.site) {
        query.site = req.query.site
    }
    if (req.query.category) {
        query.category = req.query.category
    }
})


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