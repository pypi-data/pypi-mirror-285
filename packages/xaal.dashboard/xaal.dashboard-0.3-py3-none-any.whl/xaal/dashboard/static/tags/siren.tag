<siren>
  <div class="onoffswitch">
    <input type="checkbox" class="onoffswitch-checkbox" id={ tag_id } onchange={ chk } checked={checked}>
    <label class="onoffswitch-label" for={ tag_id }>
      <span class="onoffswitch-inner"></span>
      <span class="onoffswitch-switch"></span>
    </label>
  </div>


<script>
  this.addr = opts.xaal_addr
  this.tag_id = 'btn_'+Math.random();

  receive(data) {
    state = data['attributes']['light']
    if (state == true) {
      this.checked = true
    }
    else {
      this.checked = false
    }
    this.update()
  }

  chk(e) {
    if (e.target.checked == true)
      sio_send_request(this.addr,'play',{})
    else
      sio_send_request(this.addr,'stop',{})
  }
</script>

<style>
</style>
</siren>
