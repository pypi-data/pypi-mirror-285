<contact>

<span class="detected">
  <span class="{class}">⚛</span>
</span>


<script>
  this.addr = opts.xaal_addr;
  this.detected = false;
  this.class = 'not_detected';
    
  receive(data) {
    state = data['attributes']['detected'];
    if (state == true) {
       this.detected = true
       this.class = 'detected'
    }
    else {
       this.detected = false
        this.class = 'not_detected'
    }
    this.update();
  }
</script>

<style>
.detected {
    font-weight: bold;
    color : var(--color3);
    align: center;
}

.not_detected {
    font-weight: bold;
    color : var(--color2);
    align: center;
}
    
</style>

</contact>
