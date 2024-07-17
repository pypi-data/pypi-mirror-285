<shutter>


<div class="shutter padded">
  Open : <span class="position">{ value } %</span>
  <button class="button ripple full-width" name="btn_up" onclick={ btn }>UP</button>
  <button class="button ripple full-width" name="btn_stop" onclick={ btn }>STOP</button>
  <button class="button ripple full-width" name="btn_down" onclick={ btn }>DOWN</button>
</div>

<script>
  this.addr = opts.xaal_addr
  this.value = null
  receive(data) {
    this.value = data['attributes']['position']
    this.update()
  }

  btn(e) {
    if (e.target.name =='btn_up')
      sio_send_request(this.addr,'up',{})
    if (e.target.name =='btn_down')
      sio_send_request(this.addr,'down',{})
    if (e.target.name =='btn_stop')
      sio_send_request(this.addr,'stop',{})
  }
</script>

<style>
.full-width {
  width:100%;
  margin-top: 0.7em;
}

.padded {
  padding:0.7em;
}

.position {
    font-weight: bold;
    color : var(--color1);
}

</style>
</shutter>
