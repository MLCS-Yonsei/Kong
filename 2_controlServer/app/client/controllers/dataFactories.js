

mlcs
.factory('labsInfo', function ($q, $http, $rootScope, $httpParamSerializerJQLike) {
    var data = {
        list : [
            {
                location: 'KongVR',
                ip: 'kong.hwanmoo.kr',
                status: 'offline',
                functions: {
                    "dataCollect": false,
                    "deepLearning": {
                        "ageGender": false
                    },
                    "pcarsData": false,
                    "recording": false,
                    "ruleBase": {
                        "chase": false,
                        "mapDistance": false,
                        "overtake": false
                    },
                    "serialActivate": true,
                    "hooker": false
                },
                active_devices: {},
                total_devices: [],
                videoList: {}
            },
            {
                location: 'Yonsei Lab.',
                ip: '165.132.46.101',
                status: 'offline',
                functions: {
                    "dataCollect": false,
                    "deepLearning": {
                        "ageGender": false
                    },
                    "pcarsData": false,
                    "recording": false,
                    "ruleBase": {
                        "chase": false,
                        "mapDistance": false,
                        "overtake": false
                    },
                    "serialActivate": true,
                    "hooker": false
                },
                active_devices: {},
                total_devices: [],
                videoList: {}
            },
            {
                location: 'Test',
                ip: 'localhost',
                status: 'offline',
                functions: {
                    "dataCollect": false,
                    "deepLearning": {
                        "ageGender": false
                    },
                    "pcarsData": false,
                    "recording": false,
                    "ruleBase": {
                        "chase": false,
                        "mapDistance": false,
                        "overtake": false
                    },
                    "serialActivate": true,
                    "hooker": false
                },
                active_devices: {},
                total_devices: [],
                videoList: {}
            }
        ],
        get: function() {
            return data.list
        },
        update_status: function(labs) {
            return $q( function ( resolve, reject ) {
                var l = labs.length;
                var c = 0;
                for(i=0;i<labs.length;i++) {
                    lab = labs[i];

                    if (lab.ip != '') {
                        var API = 'http://'+lab.ip+':3000/status';
                        $http.get(API).then(successCallback, errorCallback).catch(function(err){console.log(err)});
        
                        function successCallback(response){
                            var rip = response.config.url.split('/')[2].split(':')[0];
                            for (var j=0; j < labs.length; j++) {
                                if (labs[j].ip === rip) {
                                    labs[j].functions = response.data;
                                    labs[j].status = 'online'
                                }
                            }
                            c = c + 1;
                            
                            resolve(true);
                            //resolve(lab);
                        }
                        function errorCallback(error){
                            console.log(error)
                            c = c + 1;
                            if (c == l) {
                                resolve(true);
                            }
                            //resolve(opConfig.data);
                        }
                        
                    }
                        
                }
            });
        },
        update_lab: function(lab) {
            return $q( function ( resolve, reject ) {
                var API = 'http://'+lab.ip+':3000/api/common';
                // $http({
                //     url: API,
                //     method: 'POST',
                //     data: $httpParamSerializerJQLike(lab.functions),
                //     headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                // }).then(successCallback, errorCallback);

                // function successCallback(response){
                //     lab.functions = response.data;
                //     resolve(lab);
                // }
                // function errorCallback(error){
                //     resolve(lab);
                // }
                
                var form = new FormData();
                form.append("overtake", lab.functions.ruleBase.overtake);
                form.append("chase", lab.functions.ruleBase.chase);
                form.append("mapDistance", lab.functions.ruleBase.mapDistance);
                form.append("ageGender", lab.functions.deepLearning.ageGender);
                form.append("dataCollect", lab.functions.dataCollect);
                form.append("pcarsData", lab.functions.pcarsData);
                form.append("recording", lab.functions.recording);
                form.append("serialActivate", lab.functions.serialActivate);
                form.append("hooker", lab.functions.hooker);

                var settings = {
                    "async": true,
                    "crossDomain": true,
                    "url": API,
                    "method": "POST",
                    "processData": false,
                    "contentType": false,
                    "mimeType": "multipart/form-data",
                    "data": form
                }

                $.ajax(settings).done(function (response) {
                    lab.functions = JSON.parse(response);
                    resolve(lab);
                });
            });
        },
        get_video_devices: function(lab) {
            return $q( function ( resolve, reject ) {
                if (lab.ip != '') {
                    var API = 'http://'+lab.ip+':3000/api/video';
                    $http.get(API).then(successCallback, errorCallback);
    
                    function successCallback(response){
                        lab = parseVideoDeviceResponse(lab, response.data)
                        resolve(lab);
                    }
                    function errorCallback(error){
                        console.log(error)
                        //resolve(opConfig.data);
                    }
                    
                }
            });
        },
        update_video_devices: function(lab, devices) {
            return $q( function ( resolve, reject ) {
                var API = 'http://'+lab.ip+':3000/api/video';
                var form = new FormData();
                form.append("devices", devices);

                var settings = {
                    "async": true,
                    "crossDomain": true,
                    "url": API,
                    "method": "POST",
                    "processData": false,
                    "contentType": false,
                    "mimeType": "multipart/form-data",
                    "data": form
                }

                $.ajax(settings).done(function (response) {

                    lab = parseVideoDeviceResponse(lab, JSON.parse(response))
                    resolve(lab);
                });
            });
        },
        get_video_list: function(lab,dev) {
            return $q( function ( resolve, reject ) {
                
                if (lab.ip != '') {
                    var API = 'http://'+lab.ip+':3000/api/videoList';
                    $http.get(API).then(successCallback, errorCallback);
    
                    function successCallback(response){
                        lab.videoList = parseVideoListResponse(dev,response.data);
                        resolve(lab);
                    }
                    function errorCallback(error){
                        console.log(error)
                        //resolve(opConfig.data);
                    }
                    
                }
            });
        },
        turn_streaming: function(lab,dev) {
            return $q( function ( resolve, reject ) {
                
                if (lab.ip != '') {
                    var API = 'http://'+lab.ip+':3000/api/streamVideo';
                    var form = new FormData();
                    form.append("dev", dev);

                    var settings = {
                        "async": true,
                        "crossDomain": true,
                        "url": API,
                        "method": "POST",
                        "processData": false,
                        "contentType": false,
                        "mimeType": "multipart/form-data",
                        "data": form
                    }

                    $.ajax(settings).done(function (response) {

                        r = JSON.parse(response);
                        resolve(r.status);
                    });
                    
                }
            });
        }
    }
    
    return data;
})

function parseVideoDeviceResponse(lab, r) {
    lab.total_devices = r["total_devices"];
    _a = r["active_devices"];

    lab.active_devices = {}
    for (i=0;i<(lab.total_devices.length);i++) {
        _dev = lab.total_devices[i];
        if (_a.indexOf(_dev) === -1) {
            lab.active_devices[_dev] = false
        } else {
            lab.active_devices[_dev] = true
        }
    }

    return lab
}

function parseVideoListResponse(dev,r) {
    videoList = {}

    for (i=0;i<r.length;i++) {
        _v = r[i].split('/')[3].split('.mp4')[0];

        _time = _v.split('_')[0];
        _dev = parseInt(_v.split('_')[1]);

        if (_dev in videoList) {
            videoList[_dev].push(_time);
        } else {
            videoList[_dev] = [_time];
        }
    }

    return videoList
}