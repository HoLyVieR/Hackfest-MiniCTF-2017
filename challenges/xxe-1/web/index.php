<?php
// FLAG-4854126eef48a4c1ec2999b6a00b6a6b
if (isset($_GET['search'])) {
  libxml_disable_entity_loader(false);
  $xml = file_get_contents('php://input');
  $data = simplexml_load_string($xml, 'SimpleXMLElement', LIBXML_NOENT);
  if ($data->user == "admin") {
    echo 'Username exists !';
  } else {
    echo 'Username ' . $data->user . ' doesn\'t exists.';
  }
  exit();
}
?>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <link href="css/bootstrap.min.css" rel="stylesheet" />
    <script type="text/javascript">
      function search() {
        var username = document.getElementById("username").value;
        var message = document.getElementById("message");
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
          if (xhr.readyState == 4) {
            message.style.display = "block";
            message.innerHTML = xhr.responseText;
          }
        };
        xhr.open("POST", "?search=", true);
        xhr.setRequestHeader("Content-Type", "text/xml");
        xhr.send("<\?xml version='1.0' \?><lookup><user>" + username + "</user></lookup>");
        return false;
      }
    </script>
  </head>
  <body>
    <div class="container">
      <br /><br />
      <div class="alert alert-success" style="display: none" id="message"></div>
      <br />
      
      <h3>Username lookup</h3>

      <form class="form" onsubmit="return search();">
        <div class="form-group">
          <label for="username">Username</label>
          <input type="text" name="username" class="form-control" id="username" />
        </div>

        <button type="button" onclick="search()" class="btn btn-primary">Search</button>
      </form>
    </div>
  </body>
</html>