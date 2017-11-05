<?php
  // FLAG-90831a06961d71bfeca38257aad7aa5c
  if (isset($_FILES['file'])) {
    $folderid = bin2hex(random_bytes(16));
    $uploaddir = '/var/www/html/uploads/' . $folderid . '/';
    mkdir($uploaddir);
    $uploadfile = $uploaddir . basename($_FILES['file']['name']);
    if (move_uploaded_file($_FILES['file']['tmp_name'], $uploadfile)) {
      $text = 'Image uploaded to "/upload-1/uploads/' . $folderid . '/' . basename($_FILES['file']['name']). '".';
    } else {
      $error = 'Error while uploading file.';
    }
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
      <h3>File upload</h3>
      <br />
      <?php if (isset($text)) { ?><div class="alert alert-success"><?php echo $text; ?></div><?php } ?>
      <?php if (isset($error)) { ?><div class="alert alert-danger"><?php echo $error; ?></div><?php } ?>
      <br />
      <form method="POST" enctype="multipart/form-data">
        <div class="form-group">
          <label for="file">Your file</label>
          <input type="file" name="file" id="file" class="form-control"  /> 
        </div>

        <button type="submit" class="btn btn-primary">Upload</button>
      </form>
    </div>
  </body>
</html>