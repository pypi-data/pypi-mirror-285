<%inherit file="base.mako"/>
<%namespace name="widgets" file="widgets.mako" />

<link href="./static/css/btns.css" rel="stylesheet">

<div class="grid-background">
<div class="grid">

  <div class="grid-box">
  	Please edit grid.mako
  </div>

  <div class="grid-box two">
  	${widgets.list_all_devices()}
  </div>
  
</div> <!-- end of grid -->
</div><!-- end of grib background -->

<script type="riot/tag" src="./static/tags/powerrelay.tag"></script>
<script type="riot/tag" src="./static/tags/hygrometer.tag"></script>
<script type="riot/tag" src="./static/tags/thermometer.tag"></script>
<script type="riot/tag" src="./static/tags/powermeter.tag"></script>
<script type="riot/tag" src="./static/tags/lamp.tag"></script>
<script type="riot/tag" src="./static/tags/lamp_color.tag"></script>
<script type="riot/tag" src="./static/tags/shutter.tag"></script>
<script type="riot/tag" src="./static/tags/barometer.tag"></script>
<script type="riot/tag" src="./static/tags/co2meter.tag"></script>
<script type="riot/tag" src="./static/tags/motion.tag"></script>
<script type="riot/tag" src="./static/tags/door.tag"></script>
<script type="riot/tag" src="./static/tags/contact.tag"></script>


<script type="riot/tag" src="./static/tags/generic_attrs.tag"></script>
<script type="riot/tag" src="./static/tags/clock.tag"></script>
