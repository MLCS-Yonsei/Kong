module.exports.get = function(req, res) {
    res.json({status: true});
}

module.exports.auth = function(req, res) {
    console.log('Auth Requested')
    //res.json({status: true});
    console.log(req.session.user)
    if (req.isAuthenticated()) {
        res.status(200).json({user: req.session.user})
    } else {
        res.status(401).send('Failed')
    }
    
}

var models = require('../models');
