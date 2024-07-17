<barometer>

<span class="barometer">
  <span class="pressure">{ pressure }&nbsp;hPa</span><br/>
</span>


<script>
  this.addr = opts.xaal_addr;
  this.pressure = null;
  receive(data) {
    this.pressure = Math.round(data['attributes']['pressure']);
    this.update();
  }
</script>

<style>
.barometer {
    font-weight: bold;
    color : var(--color1);
    align: center;
}
</style>

</barometer>
