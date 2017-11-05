<?php
  class LogFileStrategy {
    private $file;

    public function __construct($file) {
      $this->file = $file;
    }

    // Hint : Find a way to invoke this.
    public function log($data) {
      file_put_contents($this->file, $data . "\n", FILE_APPEND);
    }

    // Hint : Or find a way to invoke this.
    public function content() {
      return file_get_contents($this->file);
    }

    public function __toString() {
      return $this->content();
    }
  }

  class LogOutputStrategy {
    private $allData = '';

    public function log($data) {
      $this->allData .= $data . "\n";
      echo "<!--" . $data . "-->\n";
    }

    public function content() {
      return $this->allData;
    }

    public function __toString() {
      return $this->content();
    }
  }

  class ContentManagement {
    private $title;
    private $logger;

    public function __construct($title, $logger) {
      $this->title = $title;
      $this->logger = $logger;
    }

    public function __destruct() {
      $this->logger->log("Content Management of " . $this->title . " finished.");
    }

    public function printTitle() {
      echo $this->title;
    }
  }

  if (isset($_GET['source'])) {
    highlight_file(__FILE__);
    exit();
  }

  $cm = new ContentManagement("PHP Data Inspector", new LogOutputStrategy());
?>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <link href="css/bootstrap.min.css" rel="stylesheet">
  </head>

  <body>
    <div class="container">
      <br />
      <h1><?php $cm->printTitle(); ?></h1>

      <form method="POST">
        <label>PHP Object (ex.: "a:2:{i:0;s:1:"1";i:1;a:1:{i:2;i:3;}}")</label><br />
        <textarea name="php-object" style="width: 400px; height: 100px"></textarea><br />
        <button type="submit">Go !</button>
      </form>

      <?php if (isset($_POST['php-object'])) { ?>
      <br />
      <h2>Output</h2>
      <pre><?php var_dump(unserialize($_POST['php-object'])); ?></pre>
      <?php } ?>

      <br /> 
      <br />
      <a href="index.php?source=">View the source</a> 
    </div>

   
  </body>
</html>
