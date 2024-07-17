<hygrometer>

<span class="hygrometer">
  <span if={value} class="humidity">{ value }&nbsp;%</span>
</span>


<script>
  this.addr = opts.xaal_addr;
  this.value = null;
  receive(data) {
    this.value = data['attributes']['humidity'];
    this.update();
  }
</script>


<style>
.humidity {
    font-weight: bold;
    color : var(--color1);
    align: center;
}
</style>

</hygrometer>
