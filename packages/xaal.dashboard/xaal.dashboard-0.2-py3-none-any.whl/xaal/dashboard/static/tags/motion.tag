<motion>

<span class="motion">
  <span class="{class}">⚛</span>
</span>


<script>
  this.addr = opts.xaal_addr;
  this.presence = false;
  this.class = 'no_motion';
    
  receive(data) {
    state = data['attributes']['presence'];
    if (state == true) {
       this.presence = true
       this.class = 'motion'
    }
    else {
       this.presence = false
        this.class = 'no_motion'
    }
    this.update();
  }
</script>

<style>
.motion {
    font-weight: bold;
    color : var(--color3);
    align: center;
}

.no_motion {
    font-weight: bold;
    color : var(--color2);
    align: center;
}
    
</style>

</motion>
