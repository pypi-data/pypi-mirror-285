<%inherit file="base.mako"/>
<%namespace name="widgets" file="widgets.mako" />

<link href="/static/css/btns.css" rel="stylesheet">

<div class="grid-background">
<div class="grid">

 <div class="grid-box">
 <b>Eclairage</b><br/>
 	${widgets.list_devices(['yl_tv_salon','lamp_salle','spot_dressing','yl_bureau','meross1','light_hub_aqara_salon'])}
 </div>

 <div class="grid-box">
 <b>Eclairage</b><br/>
 	${widgets.list_devices(['lamp_owen','radio','chevet1','chevet2','lamp_tv_ch','light_hub_aqara_chambre'])}
 </div>


 <div class="grid-box">
 <b>Température</b><br/>
 	${widgets.list_devices(['temp_owm','temp_bureau','temp_salon','temp_chambre','temp_owen','temp_sdb','temp_garage'])}
 </div>


 <div class="grid-box">
 <b>Humidité</b><br/>
 	${widgets.list_devices(['rh_owm','rh_bureau','rh_salon','rh_chambre','rh_owen','rh_sdb','rh_garage'])}
 </div>


 <div class="grid-box">
 <b>Autre</b><br/>
 	${widgets.list_devices(['power_tv','power_bureau','power_hp_ecran','co2_esp32','temp_cpu_j4105','ecran_bureau','hp_bureau'])}
 </div>


 <div class="grid-box">
 <b>Soleil</b><br/>
 	${widgets.list_devices(['lux_dressing','lux_garage','lux_owen','lux_salon','lux_chambre'])}
 </div>



 <div class="grid-box">
 <b>Contacts</b><br/>
   ${widgets.list_devices(['door_garage','door_maison','door_bureau','door_placard'])}
 </div>

<!--
 <div class="grid-box">
   ${widgets.list_devices(['window_cuisine','window_salle1','window_salle2','window_baie1','window_baie2'])}
 </div>

 
 <div class="grid-box">
   ${widgets.list_devices(['window_salon','window_bureau','window_sdb','window_dress'])}
 </div>
-->

 <div class="grid-box">
 <b>Mouvements</b><br/>
   ${widgets.list_devices(['pir_dressing','pir_sdb','pir_bureau','pir_garage','pir_owen','pir_autre'])}
 </div>

 <div class="grid-box" style="text-align:center;">
  <br/><br/><br/><br/>
      <span data-is="clock"/>
 </div>


 <!--
 <div class="grid-box two">
   <generic-attrs xaal_addr="2bab0c66-cfc7-11e9-a554-7085c2a4a601"></generic-attrs>      
 </div>
-->


</div>
</div>


<script type="riot/tag" src="../static/tags/powerrelay.tag"></script>
<script type="riot/tag" src="../static/tags/hygrometer.tag"></script>
<script type="riot/tag" src="../static/tags/thermometer.tag"></script>
<script type="riot/tag" src="../static/tags/powermeter.tag"></script>
<script type="riot/tag" src="../static/tags/lamp_color.tag"></script>
<script type="riot/tag" src="../static/tags/lamp.tag"></script>
<script type="riot/tag" src="../static/tags/shutter.tag"></script>
<script type="riot/tag" src="../static/tags/barometer.tag"></script>
<script type="riot/tag" src="../static/tags/co2meter.tag"></script>
<script type="riot/tag" src="../static/tags/luxmeter.tag"></script>
<script type="riot/tag" src="../static/tags/motion.tag"></script>
<script type="riot/tag" src="../static/tags/contact.tag"></script>



<script type="riot/tag" src="../static/tags/generic_attrs.tag"></script>
<script type="riot/tag" src="../static/tags/clock.tag"></script>
