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

