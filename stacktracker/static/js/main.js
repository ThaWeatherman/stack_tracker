function submit_coin() {
    alert('called submit coin');
}


function submit_item() {
    alert('called submit item');
}


function sold_selected(cb) {
    if (cb.checked) {
        d3.selectAll('div.hide').transition()
                                .duration(1000)
                                .delay(function(d, i) { return i*100 })
                                .style('display', 'inline');
    }
    else {
        d3.selectAll('div.hide').transition()
                                .duration(600)
                                .delay(function(d, i) { return i*100 })
                                .style('display', 'none');
    }
}

