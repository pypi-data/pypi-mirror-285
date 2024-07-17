<lamp_color>

<div>
<label class="switch">
  <input type="checkbox" onchange={ chk } checked={checked}>
  <span class="slider round" id="{ switch_id }"></span>
</label>
  <button class="modal_btn" id="{ btn_id }" onclick={ open_model }>&nbsp;</button>
</div>

<dialog id="{dialog_id}" class="lamp_modal">
  <h3>Settings</h3>

  <div>
    <label class="label_modal">
      <span>Mode</span>
    </label>
    <select id="{ mode_input_id }" onchange={ mode_input } >
      <option value="white">White</option>
      <option value="color">Color</option>
    </select>
  </div>

  <div>
    <label class="label_modal">
      <span>Color</span>
    </label>
    <input type="color" id="{color_input_id}" onchange={ color_input }/>
  </div>


  <div>
    <label class="label_modal">
      <span>Brightness</span>
    </label>
    <input type="range" id="{brightness_input_id}" onchange={ brightness_input } min="0" max="100" value="{brightness}"/>
  </div>

  <div>
    <label class="label_modal">
      <span>White Temperature</span>
    </label>
    <input type="range" id="{white_balance_input_id}" onchange={ white_temperature_input } min="2000" max="6500" value="{white_temperature}"/>
  </div>


  <div class="modal_footer">
    <input type="button" value="Close" onclick={ close_modal }/>
  </div>

</dialog>

<script>
  this.addr = opts.xaal_addr
  // display ids
  this.dialog_id = objID()
  this.btn_id    = objID()
  this.mode_input_id = objID()
  this.color_input_id = objID()
  
  receive(data) {
    if (this.addr == '41998f5e-b1a6-11ec-b598-d6bd5fe18701') {
      //_("#"+this.dialog_id).show()
      dbg = _("#"+this.mode_input_id)
    }

    state = data['attributes']['light']
    hsv = data['attributes']['hsv']
    mode = data['attributes']['mode']

    this.white_temperature = data['attributes']['white_temperature']
    this.brightness = data['attributes']['brightness']


    if ((mode == 'color') && (hsv!=null)) {
      rgb=hsv2rgb(hsv[0], hsv[1], hsv[2])
      r = Math.round(rgb[0] * 255)
      g = Math.round(rgb[1] * 255)
      b = Math.round(rgb[2] * 255)

      color=rgbToHex(r,g,b)
      _("#"+this.btn_id).style.background = color
      _("#"+this.color_input_id).value = color
      _('#'+this.mode_input_id).value = 'color'
    } else {
      _("#"+this.btn_id).style.background = 'var(--color2)'
      _('#'+this.mode_input_id).value = 'white'
    }

    if (state == true) {
      this.checked = true

    }
    else {
      this.checked = false
    }
    this.update()
  }


  function objID(name) {
    l = 10000000000000
    b = Math.round(Math.random() * l)
    return name +'_'+ b.toString()
  }

  /* ============================================================ */
  /* Color functions                                              */
  /* ============================================================ */
  function hsv2rgb(h,s,v) {                              
    let f= (n,k=(n+h/60)%6) => v - v*s*Math.max( Math.min(k,4-k,1), 0);     
    return [f(5),f(3),f(1)];       
  }   

  function rgb2hsv(r,g,b) {
    let v=Math.max(r,g,b), c=v-Math.min(r,g,b);
    let h= c && ((v==r) ? (g-b)/c : ((v==g) ? 2+(b-r)/c : 4+(r-g)/c)); 
    return [60*(h<0?h+6:h), v&&c/v, v];
  }

  function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
  }
  
  function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
  }

  function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? [parseInt(result[1], 16), parseInt(result[2], 16), parseInt(result[3], 16)] : null;
  }

  /* ============================================================ */
  /* Buttons callbacks                                            */
  /* ============================================================ */
  chk(e) {
    if (e.target.checked == true)
      sio_send_request(this.addr,'turn_on',{})
    else
      sio_send_request(this.addr,'turn_off',{})
  }

  open_model(e) {
    _("#"+this.dialog_id).show()
  }

  close_modal(e) {
    _("#"+this.dialog_id).close()
  }

  color_input(e) {
    color = e.target.value
    _("#"+this.btn_id).style.background = color

    rgb = hexToRgb(color)
    r = rgb2hsv(rgb[0]/255,rgb[1]/255,rgb[2]/255)
    sio_send_request(this.addr,'set_hsv',{'hsv':r})
 }

  mode_input(e) {
    mode = e.target.value
    console.log(mode)
    sio_send_request(this.addr,'set_mode',{'mode':mode})
  }

  brightness_input(e) {
    value = e.target.value
    sio_send_request(this.addr,'set_brightness',{'brightness':value})
  }

  white_temperature_input(e) {
    value = e.target.value
    sio_send_request(this.addr,'set_white_temperature',{'white_temperature':value})
  }

</script>

<style>
.modal_btn {
  background-color: var(--color2);
  border : none;
  text-decoration: none;
  border-radius: 2px;
  display: inline-block;
  height: 20px;
}

.modal_btn:hover {
    background-color : var(--color3);
}

.lamp_modal {
  /*color: var(--color2); */
  background-color: var(--color4);
  width: 400px;
  border: 1px solid var(--color3);
  z-index: 100;
}


.label_modal {
  display: inline-block;
  width: 150px;
}​

.modal_footer {
  border: 1px solid red;
  padding: 10px;
}

</style>
</lamp_color>
