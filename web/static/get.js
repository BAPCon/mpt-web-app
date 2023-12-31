/*

axios.get("/get_hikers/3").then(function(response) {

        for(var x = 0; x < 3; x++){
            var dhtml = response.data[x];
            var hikerCardsDiv = document.getElementById("hikerCardsDiv");
            hikerCardsDiv.innerHTML += dhtml;
        }
    })
    .catch(function(error) {
        console.log(error);
    });*/

var activeCard = document.getElementById('activeCard')

function previousCard() {
    var styl = activeCard.style;
    activeCard.setAttribute("style", "animation: shootLeft .5s linear 1;");
    setTimeout(function() { activeCard.setAttribute("style", styl); }, 711);
}

async function setMap(lat, lng){
    let map;
    lat = parseFloat(lat);
    lng = parseFloat(lng);
    async function initMap() {
        const { Map } = await google.maps.importLibrary("maps");

        map = new Map(document.getElementById("mapDisplay"), {
            center: { lat: lat, lng: lng },
            zoom: 8,
            mapTypeId: "terrain",
        });
        new google.maps.Marker({
            position: { lat: lat, lng: lng },
            map,
            title: "Status",
        });
    }

    initMap();
}