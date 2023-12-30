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
    
    
function transitionCards() {
  document.getElementById('img').className = 'classname';
}

