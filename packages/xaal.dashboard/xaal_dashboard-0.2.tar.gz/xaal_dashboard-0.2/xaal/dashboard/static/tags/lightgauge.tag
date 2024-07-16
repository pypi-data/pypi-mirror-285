<lightgauge>

<span class="lightgauge">
  <span class="brightness">{ brightness }&nbsp;%</span>
</span>


<script>
  this.addr = opts.xaal_addr;
  this.brightness = '__';
  receive(data) {
    this.brightness = data['attributes']['brightness'];
    this.update();
  }
</script>


<style>
.brightness {
    font-weight: bold;
    color : var(--color1);
    align: center;
}
</style>

</lightgauge>
