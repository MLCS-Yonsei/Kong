var passport = require('passport'),
    LocalStrategy = require('passport-local').Strategy;

// var mysql_dbc = require('./db_con')();
// var connection = mysql_dbc.init();
// connection._protocol._delegateError = function(err, sequence){
//   if (err.fatal) {
//     console.trace('fatal error: ' + err.message);
//   }
//   return del.call(this, err, sequence);
// };

// var schedule = require('node-schedule');
// var j = schedule.scheduleJob('26 * * * *', function(){
//   console.log('Reset DB 2');
//   connection = mysql_dbc.init();
// });

var models = require('../app/models');
const User = models.user;

passport.use(new LocalStrategy({
    usernameField: 'username',
    passwordField: 'password',
    passReqToCallback: true //인증을 수행하는 인증 함수로 HTTP request를 그대로  전달할지 여부를 결정한다
  }, function (req, username, password, done) {
    User.findAll({
        where: {
          username: username
        }
    })
    .then(function(results){
      if (results.length === 0) {
        console.log('해당 유저가 없습니다');
        return done(false, null);
      } else {
        if (password != results[0].password) {// (!bcrypt.compareSync(password, result[0].passwd)) {
          console.log('패스워드가 일치하지 않습니다');
          return done(false, null);
        } else {
          console.log('로그인 성공');
          var user = {
            user_id: results[0].id,
            username: results[0].username,
            level: results[0].level,
            name: results[0].name,
          }
          sess = req.session;
          sess.user = user;
          
          return done(null, user);
        }
      }
    
    })
    
  }));

passport.serializeUser(function (user, done) {
    done(null, user)
});

passport.deserializeUser(function (user, done) {
    done(null, user);
});

var isAuthenticated = function (req, res, next) {
    if (req.isAuthenticated())
        return next();
    res.redirect('/login');
};