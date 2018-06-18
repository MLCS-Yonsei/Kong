mlcs
.controller('MainCtrl', ['$scope', '$rootScope', '$state', 'labsInfo', '$http', '$window', function ($scope, $rootScope, $state, labsInfo, $http, $window) {
    $scope.labs = labsInfo.get();

    $scope.config = {
        streamingOn : false,
        currentStreamingPath : ""
    }

    $scope.isLoading = true;
    $scope.isChrome = !!window.chrome && !!window.chrome.webstore;

    $scope.currentStreamingPath = ""
    angular.element(document).ready(function () {
        $(':button').prop('disabled', true);
        $(':input').prop('disabled', true);
        labsInfo.update_status($scope.labs).then(
            function(_) {
                var t = '';
                for(i=0;i<$scope.labs.length;i++) {
                    var l = $scope.labs[i];
                    if (l.status != "offline") {
                        t = l;
                    }
                }

                if (t != '') {
                    labsInfo.get_video_devices(t).then(
                        function(_lab) {
                            $scope.currentLab = _lab;
                            $scope.currentDev = $scope.currentLab.total_devices[0]
                            labsInfo.get_video_list($scope.currentLab,$scope.currentDev)
            
                            $scope.isLoading = false;
                            $(':button').prop('disabled', false);
                            $(':input').prop('disabled', false);
                        }
                    )
                }
                
            }
        )

        
    });
    $scope.turnStreamingOn = function(lab,dev) {
        labsInfo.turn_streaming(lab,dev).then(
            function(status) {
                $scope.config.streamingOn = status;

                if (status) {
                    $scope.currentStreamingPath = "http://" + lab.ip + ":5800/stream.webm"

                    setTimeout(function (){

                        var myVideo = angular.element( document.querySelector( '#s_vid' ) )[0];

                        myVideo.src = $scope.currentStreamingPath;
                        myVideo.load();
                        myVideo.play();
                      
                    }, 600); 
                    
                } else {
                    $scope.currentStreamingPath = ""

                    var myVideo = angular.element( document.querySelector( '#s_vid' ) )[0];

                    myVideo.src = "";
                    myVideo.load();
                }
            }
        )
        $scope.config.streamingOn = true
        

    }
    $scope.refreshLabs = function() {
        labsInfo.update_status($scope.labs)
    }

    $scope.updateVideo = function(lab) {
        if (lab.status != 'offline') {
            var target_devices = [];

            for (i=0;i<lab.total_devices.length;i++) {
                var _dev = lab.total_devices[i]
                if (lab.active_devices[_dev]) {
                    target_devices.push(_dev)
                }
            }
            
            labsInfo.update_video_devices(lab, target_devices).then(
                function(_lab) {
                    lab = _lab
                }
            )
        }
    }

    $scope.refreshVideoDevices = function(lab) {
        labsInfo.get_video_devices(lab).then(
            function(_) {
                labsInfo.get_video_list($scope.currentLab,$scope.currentDev)
            }
        )
    }

    $scope.getVideoList = function(lab, dev) {
        $scope.currentDev = dev;
        labsInfo.get_video_list(lab,dev)
    }

    $scope.downloadVideo = function(lab,time,dev) {
        var file_name = time + '_' + dev + '.mp4'
        $http({
            method: 'GET',
            url: 'http://'+lab.ip+':3000/'+file_name,
            // params: { name: name },
            responseType: 'arraybuffer'
        }).success(function (data, status, headers) {
            headers = headers();
     
            var filename = headers['x-filename'];
            var contentType = headers['content-type'];
     
            var linkElement = document.createElement('a');
            try {
                var blob = new Blob([data], { type: contentType });
                var url = window.URL.createObjectURL(blob);
     
                linkElement.setAttribute('href', url);
                linkElement.setAttribute("download", filename);
     
                var clickEvent = new MouseEvent("click", {
                    "view": window,
                    "bubbles": true,
                    "cancelable": false
                });
                linkElement.dispatchEvent(clickEvent);
            } catch (ex) {
                console.log(ex);
            }
        }).error(function (data) {
            console.log(data);
        });
    }

    $scope.videoManage = function(lab){
        if (lab.status != 'offline') {
            labsInfo.get_video_devices(lab).then(
                function(_lab) {
                    $scope.currentLab = _lab;
                }
            )
        } else {
            $scope.currentLab = lab;
        }
    }
    $scope.update_lab = function(lab) {
        
        if (lab.status != 'offline') {
            labsInfo.update_lab(lab).then(
                function(_lab) {
                    lab = _lab
                }
            )
        }
            
    }

    $scope.turnRb = function(lab) {
        var rb = lab.functions.ruleBase;

        if ((rb.chase && rb.mapDistance && rb.overtake) == true) {
            rb.chase = false;
            rb.mapDistance = false;
            rb.overtake = false;
        } else if ((rb.chase && rb.mapDistance && rb.overtake) == false) {
            rb.chase = true;
            rb.mapDistance = true;
            rb.overtake = true;
        } else if ((rb.chase || rb.mapDistance || rb.overtake) == true) {
            rb.chase = false;
            rb.mapDistance = false;
            rb.overtake = false;
        }

    }

    

    
}]);

