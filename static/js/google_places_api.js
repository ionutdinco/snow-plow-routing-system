var EPSILON = 0.000001;

function fp_less_than(A, B) {
		Epsilon = EPSILON;
		return (A - B < Epsilon) && (Math.abs(A - B) > Epsilon);
	};

function fp_greater_than(A, B) {
    Epsilon = EPSILON;
    return (A - B > Epsilon) && (Math.abs(A - B) > Epsilon);
};

$.getScript( "https://maps.googleapis.com/maps/api/js?key=" + google_api_key + "&libraries=places&callback=initMap")
.done(function( script, textStatus ) {
    google.maps.event.addDomListener(window, "load", initAutoComplete);
})

let autocomplete;
let infoWindow;
let open_marker = false;

function initAutoComplete(){

   autocomplete = new google.maps.places.Autocomplete(
       document.getElementById('id-google-address'),
       {
           types: ['address'],
       })

   autocomplete.addListener('place_changed', onPlaceChanged);
}


function onPlaceChanged (){

    var place = autocomplete.getPlace();

    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id-google-address').value

    geocoder.geocode( { 'address': address}, function(results, status) {

        if (status == google.maps.GeocoderStatus.OK) {
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();
            console.log(latitude);
            console.log(longitude);

            $('#id-lat-veh-addres').val(latitude)
            $('#id-long-veh-addres').val(longitude)
        }
    });

    if (!place.geometry){
        document.getElementById('id-google-address').placeholder = "*Begin typing address";
    }
}


function initMap(){
    lat = parseFloat(latitude);
    lng = parseFloat(longitude);
    const myLatLng = { lat: lat, lng: lng };
    const map = new google.maps.Map(document.getElementById("map-route"), {
        zoom: 6,
        center: myLatLng,
        styles: [
          { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
          { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
          { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
          {
            featureType: "administrative.locality",
            elementType: "labels.text.fill",
            stylers: [{ color: "#d59563" }],
          },
          {
            featureType: "poi",
            elementType: "labels.text.fill",
            stylers: [{ color: "#d59563" }],
          },
          {
            featureType: "poi.park",
            elementType: "geometry",
            stylers: [{ color: "#263c3f" }],
          },
          {
            featureType: "poi.park",
            elementType: "labels.text.fill",
            stylers: [{ color: "#6b9a76" }],
          },
          {
            featureType: "road",
            elementType: "geometry",
            stylers: [{ color: "#38414e" }],
          },
          {
            featureType: "road",
            elementType: "geometry.stroke",
            stylers: [{ color: "#212a37" }],
          },
          {
            featureType: "road",
            elementType: "labels.text.fill",
            stylers: [{ color: "#9ca5b3" }],
          },
          {
            featureType: "road.highway",
            elementType: "geometry",
            stylers: [{ color: "#746855" }],
          },
          {
            featureType: "road.highway",
            elementType: "geometry.stroke",
            stylers: [{ color: "#1f2835" }],
          },
          {
            featureType: "road.highway",
            elementType: "labels.text.fill",
            stylers: [{ color: "#f3d19c" }],
          },
          {
            featureType: "transit",
            elementType: "geometry",
            stylers: [{ color: "#2f3948" }],
          },
          {
            featureType: "transit.station",
            elementType: "labels.text.fill",
            stylers: [{ color: "#d59563" }],
          },
          {
            featureType: "water",
            elementType: "geometry",
            stylers: [{ color: "#17263c" }],
          },
          {
            featureType: "water",
            elementType: "labels.text.fill",
            stylers: [{ color: "#515c6d" }],
          },
          {
            featureType: "water",
            elementType: "labels.text.stroke",
            stylers: [{ color: "#17263c" }],
          },
        ],
    });
    let marker = new google.maps.Marker({
       map,
       title: "Vehicles address",
    });

    lat_bool = fp_less_than(parseFloat(latitude), 0.0) || fp_greater_than(parseFloat(latitude), 0.0);
    lng_bool = fp_less_than(parseFloat(longitude), 0.0) || fp_greater_than(parseFloat(longitude), 0.0);
    model_value = lat_bool && lng_bool;

    if (model_value){
        marker.setPosition(myLatLng);
        map.setZoom(14);
    }else{
        infoWindow = new google.maps.InfoWindow({
            content: "Use the input box to type addres or/and click the map to set Depot!",
            position: { lat: 45.80186488976563, lng: 24.802484850565268 },
        });
        infoWindow.open(map);
        open_marker = true;
    }
    mapInfo(map, myLatLng, marker);

}

function updateMap() {
  var lat_a = document.getElementById('id-lat-veh-addres').value;
  var long_a= document.getElementById('id-long-veh-addres').value;

  if (lat_a != "" && long_a != ""){
  // 45.80186488976563 long 24.802484850565268
      const myLatLng = { lat: parseFloat(lat_a), lng: parseFloat(long_a) };
      const map = new google.maps.Map(document.getElementById("map-route"), {
        zoom: 13,
        center: myLatLng,
        styles: [
          { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
          { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
          { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
          {
            featureType: "administrative.locality",
            elementType: "labels.text.fill",
            stylers: [{ color: "#d59563" }],
          },
          {
            featureType: "poi",
            elementType: "labels.text.fill",
            stylers: [{ color: "#d59563" }],
          },
          {
            featureType: "poi.park",
            elementType: "geometry",
            stylers: [{ color: "#263c3f" }],
          },
          {
            featureType: "poi.park",
            elementType: "labels.text.fill",
            stylers: [{ color: "#6b9a76" }],
          },
          {
            featureType: "road",
            elementType: "geometry",
            stylers: [{ color: "#38414e" }],
          },
          {
            featureType: "road",
            elementType: "geometry.stroke",
            stylers: [{ color: "#212a37" }],
          },
          {
            featureType: "road",
            elementType: "labels.text.fill",
            stylers: [{ color: "#9ca5b3" }],
          },
          {
            featureType: "road.highway",
            elementType: "geometry",
            stylers: [{ color: "#746855" }],
          },
          {
            featureType: "road.highway",
            elementType: "geometry.stroke",
            stylers: [{ color: "#1f2835" }],
          },
          {
            featureType: "road.highway",
            elementType: "labels.text.fill",
            stylers: [{ color: "#f3d19c" }],
          },
          {
            featureType: "transit",
            elementType: "geometry",
            stylers: [{ color: "#2f3948" }],
          },
          {
            featureType: "transit.station",
            elementType: "labels.text.fill",
            stylers: [{ color: "#d59563" }],
          },
          {
            featureType: "water",
            elementType: "geometry",
            stylers: [{ color: "#17263c" }],
          },
          {
            featureType: "water",
            elementType: "labels.text.fill",
            stylers: [{ color: "#515c6d" }],
          },
          {
            featureType: "water",
            elementType: "labels.text.stroke",
            stylers: [{ color: "#17263c" }],
          },
        ],
      });
      let marker = new google.maps.Marker({
        map,
        title: "Vehicles address",
      });
      updateMapInfo(map, myLatLng, marker);
  }
}

function mapInfo(map, myLatLng, marker){

    map.addListener("click", (mapsMouseEvent) => {
        // Close the current InfoWindow.
        if (open_marker){
            infoWindow.close();
        }
        marker.setPosition(mapsMouseEvent.latLng);
        updateGeolocation(mapsMouseEvent.latLng.toJSON());
    });
}

function updateMapInfo(map, myLatLng, marker){

    marker.setPosition(myLatLng);
    updateGeolocation(myLatLng);
    map.addListener("click", (mapsMouseEvent) => {
        marker.setPosition(mapsMouseEvent.latLng);
        updateGeolocation(mapsMouseEvent.latLng.toJSON());
        console.log("coords",mapsMouseEvent.latLng.toJSON());
    });
}

function updateGeolocation(myLatLng){
    $.ajax({
      url: "http://127.0.0.1:8000/accounts/profile-admin/",
      type: "POST",
      dataType: "json",
      data: JSON.stringify({lat: myLatLng["lat"], lng: myLatLng["lng"]}),
      headers: {
        "X-Requested-For": "GeocodingControl",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: (data) => {
      result = data['payload'];
      },
      error: (error) => {
        console.log(error);
      }
    });
}