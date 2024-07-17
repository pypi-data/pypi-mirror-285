<%inherit file="base.mako"/>
    
<script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.13.0/moment.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@2.8.0"></script>
<script src="https://cdn.jsdelivr.net/npm/hammerjs@2.0.8"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@0.7.0"></script>





<br/>
<div class="content">
    <div id="data">Warp10 datas for ${addr} daily</div>
    <canvas id="chart"></canvas>
</div>



<script>

//================ JS tools ====================================================
// dumbs functions to mimic jQuery selectors
var _ = function ( elem ) {
  return document.querySelector( elem );
}

var __ = function ( elem ) {
  return document.querySelectorAll( elem );
}


function update(data) {
    //console.log(data);
    //_('#data').innerHTML = "<pre>" + data +"</pre>";
    clearData(chart);
    addData(chart,data);
}

function clearData(chart) {
  if (chart.hasOwnProperty('datasets')) {
    chart.datasets.forEach((dataset) => {
      dataset.data = [];
    })
  }
  chart.data.labels=[];  
  chart.update();
}

function load(addr) {
  var getUrl = window.location;
  var url = getUrl.protocol + "//" + getUrl.host + "/warp10/daily/"+addr;
  console.log(url);
  fetch(url)
    .then(response => response.json())
    .then(data => update(data))
    .catch(err => console.log(err))
}



function addData(chart, data) {
  data.forEach((kv) => {
    chart.data.labels.push(kv[0]);
    chart.data.datasets[0].data.push(kv[1]);
    }
  );
  //chart.data.labels.push(label);
  //chart.data.datasets.forEach((dataset) => {
  //    dataset.data.push(data);
  //});
  chart.update();
  chart.render();
}



var config = {
  type: 'line',
  data: {
    datasets: [{
      label: "Warp10 data",
      borderColor: "#00bbd7",
      pointRadius: 1,
      borderWidth: 2,
      lineTension: 0.2,
    }]
  },

  options: {
    responsive: true, 
    //maintainAspectRatio: false,
    scales: {
      xAxes: [{
        type: 'time',
        time: {
          parser: 'X',
          displayFormats: { hour: 'H:mm'}
        }
      }],
    },
  }
};


var ctx = document.getElementById("chart").getContext("2d");
chart=new Chart(ctx, config);

function refresh() {
  console.log('Loading datas');
  load('${addr}');
}


refresh();
/*
setInterval(() => { 
  refresh();
  },1000 * 60);
*/

</script>
