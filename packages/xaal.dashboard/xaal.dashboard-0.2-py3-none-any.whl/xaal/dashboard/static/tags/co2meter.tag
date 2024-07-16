<co2meter>

<span class="co2meter">
  <span if={value} class="co2">{ value }&nbsp;ppm</span>
</span>


<script>
  this.addr = opts.xaal_addr;
  this.value = '';
  receive(data) {
    this.value = data['attributes']['co2'];
    this.update();
  }
</script>

<style>
.co2 {
    font-weight: bold;
    color : var(--color1);
    align: center;
}
</style>

</co2meter>
