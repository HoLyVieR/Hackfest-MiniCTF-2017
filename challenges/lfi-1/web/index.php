<?php
  // FLAG-61be296dafa12f88ac36a9d968fe92bf
  if (isset($_GET['path'])) {
    $content = file_get_contents('uploads/' . $_GET['path']);
  }
?>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <link href="css/bootstrap.min.css" rel="stylesheet">
  </head>

  <body>
    <div class="container">
      <h3>ASCII Art Viewer</h3>
      <form method="GET">
        <div class="form-group">
          <label for="path">ASCII Art</label>
          <select name="path" class="form-control" id="path">
            <option value="cats.txt">Cat</option>
            <option value="dog.txt">Dog</option>
            <option value="zebra.txt">Zebra</option>
          </select>
        </div>

        <button type="submit" class="btn btn-primary">View</button>
      </form>

      <?php if (isset($content)) { ?>
      <br />
      <pre><?php echo $content; ?></pre>
      <?php } ?>
    </div>
  </body>
</html>