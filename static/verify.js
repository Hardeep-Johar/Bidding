function verify(minbids) {
    console.log(minbids);
    var points = document.getElementById("total");
    if (points.value < 0) {
        alert("Available points must be greater than or equal to zero!");
        return false;
    } else {
        var all_tags = document.getElementsByClassName("bid");
        var count = 0;
        for(var i=0;i<all_tags.length;i++) {
            if (parseInt(all_tags[i].value)>0)
                count = count + 1;
        }
        if (count < minbids) {
            msg = "You must make bids on at least " + minbids + " projects!"
            alert(msg);
            return false;
        }

    }
    return true;
}