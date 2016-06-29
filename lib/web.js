var config = require('config');
var express = require('express');
var session = require('express-session');
var bodyParser = require('body-parser');
var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var async = require('async');
var passport = require('passport');
var email = require('emailjs').email;
var RedditStrategy = require('passport-reddit').Strategy;

// Lets connect to the database backend
const db = require('monk')(config.MongoDB.database)
const humidors = db.get('humidors')
const auctions = db.get('auctions')


app.set('view_engine', 'jade');
app.set(session({secret: config.AppServer.sessionSecret}))
app.use(bodyParser());
app.use('/static', express.static(config.AppServer.static))


// Simple route middleware to ensure user is authenticated.
//   Use this route middleware on any resource that needs to be protected.  If
//   the request is authenticated (typically via a persistent login session),
//   the request will proceed.  Otherwise, the user will be redirected to the
//   login page.
function ensureAuthenticated(req, res, next) {
  if (req.isAuthenticated()) { return next(); }
  res.redirect('/login');
}


// Passport session setup.
//   To support persistent login sessions, Passport needs to be able to
//   serialize users into and deserialize users out of the session.  Typically,
//   this will be as simple as storing the user ID when serializing, and finding
//   the user by ID when deserializing.  However, since this example does not
//   have a database of user records, the complete Reddit profile is
//   serialized and deserialized.
passport.serializeUser(function(user, done) {
  done(null, user);
});

passport.deserializeUser(function(obj, done) {
  done(null, obj);
});


// Use the RedditStrategy within Passport.
//   Strategies in Passport require a `verify` function, which accept
//   credentials (in this case, an accessToken, refreshToken, and Reddit
//   profile), and invoke a callback with a user object.
passport.use(new RedditStrategy({
    clientID: config.Reddit.clientID,
    clientSecret: config.Reddit.clientSecret,
    callbackURL: config.Reddit.callbackURL
  },
  function(accessToken, refreshToken, profile, done) {
    // asynchronous verification, for effect...
    process.nextTick(function () {

      // To keep the example simple, the user's Reddit profile is returned to
      // represent the logged-in user.  In a typical application, you would want
      // to associate the Reddit account with a user record in your database,
      // and return that user instead.
      return done(null, profile);
    });
  }
));


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
});


// GET /auth/reddit/callback
//   Use passport.authenticate() as route middleware to authenticate the
//   request.  If authentication fails, the user will be redirected back to the
//   login page.  Otherwise, the primary route function function will be called,
//   which, in this example, will redirect the user to the home page.
app.get('/auth/reddit/callback', function(req, res, next){
    // Check for origin via state token
    if (req.query.state == req.session.state){
        passport.authenticate('reddit', {
            successRedirect: '/',
            failureRedirect: '/login'
        })(req, res, next);
    } else {
        next( new Error(403) );
    }
});


app.get('/logout', function(req, res){
    req.logout();
    res.redirect('/');
});


app.get('/', function(req, res) {
    res.render('index')
})

app.get('/bids', function(req, res) {
    res.render('bidIndex')
})

app.get('/bids/search/:search', function(req, res){

})

app.get('/humidors', ensureAuthenticated, function(req, res) {
    humidors.find({user_id: req.user.id}).then(function(docs) {

    }).catch(function(err) {

    })
})

app.get('/humidors/:id', ensureAuthenticated, function(req, res) {
    humidors.findOne({id: id}).then(function (doc) {

    }).catch(function(err) {

    })
})

app.post('/humidors/:id', ensureAuthenticated, function(req, res) {
    humidors.findAndModify({
        query: {_id: id},
        update: {
            $setOnInsert: {user_id: req.user.id, last_alarm: 0},
            $set: {
                name: req.body.name,
                location: req.body.location,
                email: req.body.email,
                limits: {
                    temperature: {
                        high: req.body.high_temp,
                        low: req.body.low_temp
                    },
                    humidity: {
                        high: req.body.high_hum,
                        low: req.body.low_hum
                    }
                }
            }
        },
        new: true,
        upsert: true
    }).then(function() {

    }).catch(function(err) {

    })
})

app.post('/humidors/update', function(req, res) {
    var id = req.headers['X-HERF-HUM-ID'];
    var temp = req.body.temperature;
    var humidity = req.body.humidity;
    if (hum_id){
        humidors.findAndModify({
            query: {_id: id}, 
            update: {$addToSet: {'readings': {
                temperature: temp, 
                humidity: humidity, 
                timestamp: new Date.now()
            }}}
        }).then(function(doc) {
            // Here we want to check to see if any alarms have been triggered.  We also want to
            // make sure that we dont constantly spam the person, so we will alarm once, and then
            // silence the alarm for 24hrs.
            if ((doc.limits.temperature.high <= temp || doc.limits.temperature.low >= temp ||
                doc.limits.humidity.high <= humidity || doc.limits.humidity.low >= humidity) && 
                                                        doc.last_alarm >= new (Date.now() - 86400000)) {
                doc.last_alarm = new Date.now();

            }

            return {status: 'updated'}
        })
    } else {
        return {status: 'error'}
    }
})