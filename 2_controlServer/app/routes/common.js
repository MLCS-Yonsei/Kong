var express = require('express');
var router = express.Router();
var commonCtrl = require('../controllers/common');

/* GET home page. */
router.get('/', commonCtrl.menu);

module.exports = router;

