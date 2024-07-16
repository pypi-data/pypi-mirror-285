<debug-btn>

<div class="debug-btn">
<input type="button" class="button" value="debug"  name="debug" onclick={ btn } />
</div>

<script>
btn(e) {
   sio.emit('debug')     
}
</script>


</debug-btn>

