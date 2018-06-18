var express = require('express');
var router = express.Router();
var apiCtrl = require('../controllers/api');

var passport = require('passport'),
    LocalStrategy = require('passport-local').Strategy;

/* GET home page. */
router.get('/', apiCtrl.get);

router.post('/auth/login', passport.authenticate('local'), // 인증 실패 시 401 리턴, {} -> 인증 스트레티지
    function (req, res) {
        res.send({auth: true, user: req.user})
    });

router.get('/auth/logout', function (req, res) {
    console.log('로그아웃 성공')
    req.logout();
    req.session.destroy(function (err) {
        if (err) { return next(err); }
        // The response should indicate that the user is no longer authenticated.
        return res.send({ authenticated: req.isAuthenticated() });
    });

});

module.exports = router;
