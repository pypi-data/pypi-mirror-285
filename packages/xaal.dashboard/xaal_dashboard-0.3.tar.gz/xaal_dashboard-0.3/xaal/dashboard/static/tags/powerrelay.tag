<powerrelay>

<label class="switch">
  <input type="checkbox" id="{ tag_id }" onchange={ chk } checked={checked}>
  <span class="slider round" ></span>
</label>

<script>
  this.addr = opts.xaal_addr
  this.tag_id = 'btn_'+Math.random();
    
  receive(data) {
    state = data['attributes']['power']
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
      sio_send_request(this.addr,'turn_on',{})
    else
      sio_send_request(this.addr,'turn_off',{})
  }
    
</script>

<style>
 .powerrelay {
 }

</style>
</powerrelay>
