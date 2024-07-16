<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <title>${title}</title>
  <meta name="keywords" content="" />
  <meta name="description" content="" />
  <meta name="mobile-web-app-capable" content="yes">
  <link rel="manifest" href="/static/manifest.json">
  <link rel="icon" href="/static/imgs/favicon.ico">
  <meta name="theme-color" content="#333" />

  <!-- CSS & Fonts -->
  <link href="/static/css/site.css" rel="stylesheet">


</head>
<body>

  <!-- Menu -->
  <div>
      <%include file="./menu.mako" />
  </div>



<!-- <div id="messages"></div> -->

<div id="main">
    ${self.body()}
</div> <!-- EOF Main -->



<!-- loading JS-->
<script src="/static/js/riot+compiler.min.js"></script>
<script src="/static/js/socket.io.min.js"></script>

<script src="/static/js/site.js"></script>

</body>
</html>
