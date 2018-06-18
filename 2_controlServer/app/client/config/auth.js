mlcs.service('Auth', function ($q, $http, $state, $cacheFactory, $rootScope) {
    var API = '/api/auth',
        cache = $cacheFactory('mlcs');

    // 로그인 정보 조회
    this.get = function(options) {
        var deferred = $q.defer();

        if (cache.get('auth')) {

            // 캐쉬에 인증정보가 있으면 인증정보 반환
            deferred.resolve(cache.get('auth'));
        } else {
            // 캐쉬에 인증정보가 없으면 백엔드에 호출함
            $http.get(API).then(successCallback, errorCallback);

            function successCallback(response){
                console.log('Login Success from Backend - not cached')

                $rootScope.user = response.data.user
                cache.put('auth', true); // 캐쉬에 인증정보 저장
                deferred.resolve(cache.get('auth')); // 인증정보 반환
            }
            function errorCallback(error){
                console.log('Login Failed')    
                // 인증되지 않을경우 reject
                deferred.reject('Rejected');

                // options.redirect 파라메터 값이 설정된 경우 /login 페이지로 리다이랙트
                if (options && options.redirect) {
                    $state.go('login');
                }
            }
            
        }
    }

    this.logout = function() {
        var deferred = $q.defer();
        $http.get('/api/auth/logout');

        function successCallback(response){
            console.log('Logout Success')     
            
        }

        function errorCallback(error){
            console.log('Logout Failed')    
            
        }

        $rootScope.user = null;
        cache.put('auth', null);
        deferred.reject('Rejected');

        $state.go('login');
    }
});