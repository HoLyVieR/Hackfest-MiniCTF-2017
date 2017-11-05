<?php
  $flag = "FLAG-297f30fc7d69b365821e5bb43ca089ec";

  function encrypt($data) {
    return base64_encode($data);
  }

  function decrypt($data) {
    return base64_decode($data);
  }

  if (!isset($_COOKIE['auth'])) {
    $struct = new stdClass();
    $struct->allowed = false;
    $data = encrypt(json_encode($struct));
    setcookie("auth", $data); 
  } else {
    $struct = json_decode(decrypt($_COOKIE['auth']));
  }
?>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <link href="css/bootstrap.min.css" rel="stylesheet">
  </head>

  <body>
    <div class="container">
      <br /><br />
      <?php
        if (isset($struct->allowed) && $struct->allowed === true) {
      ?>
      <div class="alert alert-success"><?php echo $flag; ?></div>
      <?php
        } else {
      ?>
      <div class="alert alert-danger">You are not allowed to view the flag.</div>
      <?php  
        }
      ?>
    </div>
  </body>
</html>
