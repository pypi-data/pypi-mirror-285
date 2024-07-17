<clock>

<link href='https://fonts.googleapis.com/css?family=Orbitron' rel='stylesheet' type='text/css'>

<div class="clock">
    { clock }
</div>


<script>
var self = this;

this.on('mount',function() {
    clock();
    setInterval(clock, 5000);
});



function clock() {
    var time = new Date(),
        hours = time.getHours(),
        minutes = time.getMinutes();

    self.clock = harold(hours) + ":" + harold(minutes);
    self.update();
}


function harold(standIn) {
    if (standIn < 10) {
        standIn = '0' + standIn
    }
    return standIn;
}

</script>

<style>
 .clock {
     font-weight: bold;
     font-size : 200%;
     color:  var(--color3);
     font-family: 'Orbitron', sans-serif;
 }
</style>

</clock>
