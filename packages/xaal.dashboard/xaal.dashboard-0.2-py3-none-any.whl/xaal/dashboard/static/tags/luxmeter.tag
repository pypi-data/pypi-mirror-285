<luxmeter>

<span class="luxmeter">
  <span if={value} class="illuminance">{ value }&nbsp;lx</span>
</span>


<script>
  this.addr = opts.xaal_addr;
  this.value = null;
  receive(data) {
    this.value = data['attributes']['illuminance'];
    this.update();
  }
</script>


<style>
.illuminance {
    font-weight: bold;
    color : var(--color1);
    align: center;
}
</style>

</luxmeter>
