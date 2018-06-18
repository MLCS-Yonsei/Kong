mlcs.service('API', function ($q, $http, $state, $cacheFactory, $rootScope) {
    var API = '/api/';

    // 로그인 정보 조회
    this.get_user = function(user_id) {
        var PATH = API + 'user?user_id=' + user_id

        return $http.get(PATH).then(successCallback, errorCallback);

        function successCallback(response){
            //$rootScope.user = response.data.user
            return response.data
        }
        function errorCallback(error){
            // 조회된 사용자 없음
        }

    }

});