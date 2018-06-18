module.exports.menu = function(req, res) {
    if (req.isAuthenticated()) {
        res.render('layout', { user : req.user })
    } else {
        res.render('layout')
    }
}
