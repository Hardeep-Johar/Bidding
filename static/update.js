function update(tag,maxbid) {
    var value = tag.value;
    console.log(value)
    if (value < 0) {
        tag.value=0;
        value=0;
        alert("Bids cannot be negative!");
    }
    if (value > maxbid) {
        tag.value = maxbid;
        var msg = "The maximum bid allowed on a project is " + maxbid;
        alert(msg)
    }
    if (value > 0) {
        tag.style.color = "red";
    }
    if (value == 0) {
        tag.style.color = "lightgray";
    }
    var all_tags = document.getElementsByClassName("bid")
    var tot = 0
    for(var i=0;i<all_tags.length;i++){
        if(parseInt(all_tags[i].value))
            tot += parseInt(all_tags[i].value);
    }
    console.log(tot,value)
    document.getElementById("total").value = 2000 - tot}
