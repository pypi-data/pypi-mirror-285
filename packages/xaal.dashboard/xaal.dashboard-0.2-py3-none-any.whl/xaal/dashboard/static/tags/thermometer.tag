<thermometer>

<span class="thermometer">
    <span if={value} class="temperature">{ value }&nbsp;°</span>
</span>

<script>
  this.addr = opts.xaal_addr
  this.value = null
  receive(data) {
    this.value = data['attributes']['temperature']
    this.update()
  }
</script>

<style>

.temperature {
    font-weight: bold;
    color : var(--color1);
}

.thermometer {
    padding: 10px 0px;
}

</style>


</thermometer>
