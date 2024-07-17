<powermeter>

<span class="powermeter">
  <span class="power">{ power }&nbsp;W</span><br/>
  <span if={energy} class="energy">{ energy }&nbsp;kW</span>
</span>


<script>
  this.addr = opts.xaal_addr;
  this.power = null;
  this.energy = null;
  receive(data) {
    this.power = data['attributes']['power'];
    this.energy = data['attributes']['energy'];
    this.update();
  }
</script>

<style>
.power {
    font-weight: bold;
    color : var(--color1);
    align: center;
}
</style>

</powermeter>
