

    var app = angular.module("demoapp", ["leaflet-directive","elasticsearch"],
        ['$locationProvider', function($locationProvider){
    $locationProvider.html5Mode(true);
        }]
        );

app.factory('tweetService',
    ['$q', 'esFactory', '$location', function($q, elasticsearch, $location){
        var client = elasticsearch({
            host: "search-ccas2-wkp2mz4ca2wjtxn6kvlo6gw6vi.us-east-1.es.amazonaws.com:80"
        });

        /**
         * Given a term and an offset, load another round of 10 recipes.
         *
         * Returns a promise.
         */
        var search = function(term, offset){
            var deferred = $q.defer();
            var query = {
                "match": {
                    "_all": term
                }
            };
            // socket.on('connect', function() {
            socket.emit('first', term);
            console.log("hello");
            // });
            client.search({
                "index": 'test-index',
                "type": 'test-type',
                "body": {
                    "size": 100,
                    "from": (offset || 0) * 100,
                    "query": query
                }
            }).then(function(result) {
                var ii = 0, hits_in, hits_out = [];
                hits_in = (result.hits || {}).hits || [];
                for(;ii < hits_in.length; ii++){
                    hits_out.push(hits_in[ii]._source);
                }
                deferred.resolve(hits_out);
            }, deferred.reject);

            return deferred.promise;
        };


        return {
            "search": search
        };
    }]
);

 
app.controller('MarkersAddRemoveController', 
    ['tweetService', '$scope', '$location', "$http", 
    function(tweets, $scope, $location, $http) {
angular.extend($scope, {
                london: {
                    lat: 51.505,
                    lng: -0.09,
                    zoom: 2
                },  
                layers: {
                    baselayers: {
                        osm: {
                            name: 'OpenStreetMap',
                            type: 'xyz',
                            url: 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
                        }
                    },
                    overlays: {
                        realworld: {
                            name: "Real world data",
                            type: "markercluster",
                            visible: true
                        }
                    }
                },
                redIcon: {
                    iconUrl: 'static/img/red-mark.png',
                    iconSize:     [30, 30], // size of the icon
                    iconAnchor:   [15, 30] // point of the icon which will correspond to marker's location
                },
                blackIcon: {
                    iconUrl: 'static/img/black-mark.png',
                    iconSize:     [30, 30], // size of the icon
                    iconAnchor:   [15, 30] // point of the icon which will correspond to marker's location
                },
                greenIcon: {
                    iconUrl: 'static/img/green-mark.png',
                    iconSize:     [30, 30], // size of the icon
                    iconAnchor:   [15, 30] // point of the icon which will correspond to marker's location
                }
            });

                var initChoices = [
            "love",
            "dog",
            "trump",
            "world",
            "christmas"
        ];
        var idx = Math.floor(Math.random() * initChoices.length);

        // Initialize the scope defaults.
        $scope.tweets = [];   
        $scope.searchTerm = $location.search().q || initChoices[idx];
        $scope.search = function(){
            $scope.page = 0;
            $scope.tweets = [];
            $scope.allResults = false;
            $location.search({'q': $scope.searchTerm});
            $scope.loadMore();
        };

        $scope.loadMore = function(){
            tweets.search($scope.searchTerm, $scope.page++).then(function(results){
                if(results.length !== 100){
                    $scope.allResults = true;
                }

                var ii = 0;
                for(;ii < results.length; ii++){
                    $scope.tweets.push(results[ii]);
                }
            mrk = {};
            for(i = 0; i< $scope.tweets.length; i++) {
                console.log($scope.tweets[i])
                if (!("sentiment" in $scope.tweets[i])) {
                    $scope.tweets[i].sentiment = "neutral";
                }
                msg = "<dl><dt><b>Tweet: </b>" +$scope.tweets[i].message  +  "</dt><dt><b>Sentiment: </b>" + $scope.tweets[i].sentiment + "</dt></dl>";
                mrk[i] = {
                               //lat: 41.8335845,
                               //lng: -87.73201300000002,

                            lat: $scope.tweets[i].location.lat,
                            lng: $scope.tweets[i].location.lon,
                            message: msg,
//                            icon: "score" in $scope.tweets[i].sentiment ? ($scope.tweets[i].sentiment.type == "positive" ? $scope.greenIcon : $scope.redIcon) : $scope.blackIcon,
//                            layer: 'realworld'
                            icon:  $scope.tweets[i].sentiment == "positive" ?$scope.greenIcon : ($scope.tweets[i].sentiment == "neutral" ?$scope.blackIcon:$scope.redIcon),
                            //icon: $scope.blackIcon,
                            layer: 'realworld'
                        };
            }
            angular.extend($scope, {
                markers: mrk 
            });
            });
        };

        $scope.loadMore();
         

            
            $scope.addMarkers = function() {

            };
            $scope.removeMarkers = function() {
                $scope.markers = {};
            }
        } ]);
