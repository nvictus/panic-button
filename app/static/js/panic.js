var PanicButton = (function ($) {

    var data = [];

    var plot = $.plot(".panic-plot", [{data: []}], {
        series: {
            lines: {fill: true}                    
        },
        
        grid: {
            //backgroundColor: { colors: ["#75A7E0", "#1F77DB"]  }
            backgroundColor: "#EFF2FB",
            borderWidth: 2,
        },
        
        xaxis: {
            mode: "time",
            timeformat: "%H:%M",
            timezone: "browser"
        }
    });

    $('.panic-button').on("click", function () {
        $.ajax({
            url: "panic", 
            method: "post",
            success: function( resp ) {
                //$("#timestamps").html(resp["timestamp"].toString());
                console.log(resp);
                addPoint(resp.timestamp, resp.count);
            }
        });
    });

    function addZero() {
        var now = new Date().getTime();
        data.push([now, 0]);
        plot.setData([data]);
        plot.setupGrid();
        plot.draw();
        setTimeout(addZero, 6000);
    }

    function addPoint(timestamp, count) {
        data.push([timestamp, count]);
    }

    function init() {
        console.log('starting loop');
        // $.ajax({
        //     url: 'panic',
        //     method: 'get',
        //     success: function(resp) {
        //         $.merge(data, resp.series);
        //         console.log(data);
        //         plot.setData([data]);
        //         plot.setupGrid();
        //         plot.draw();
        //     }       
        // });
        addZero();     
    }

    return {
        data: data,
        plot: plot,
        init: init
    };
}(jQuery));
