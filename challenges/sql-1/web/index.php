<?php
  $db = new PDO('sqlite:db/a86f88dcfcd2d020296f2bbd7283dd23.db');

  // Setup
  $db->query('CREATE TABLE IF NOT EXISTS items (name TEXT, description TEXT); ');
  $result = $db->query('SELECT COUNT(*) FROM items;');
  $count = $result->fetch(PDO::FETCH_NUM)[0];

  if ($count == 0) {
    $db->query("INSERT INTO items VALUES ('Banana', 'Yellow Thing')");
    $db->query("INSERT INTO items VALUES ('Orange', 'Orange Thing')");
    $db->query("INSERT INTO items VALUES ('Tomato', 'Red Thing')");
  }

  $db->query('CREATE TABLE IF NOT EXISTS flag (flag TEXT); ');
  $result = $db->query('SELECT COUNT(*) FROM flag;');
  $count = $result->fetch(PDO::FETCH_NUM)[0];

  if ($count == 0) {
    $db->query("INSERT INTO flag VALUES ('FLAG-8c0f78bd9f65fb6b2d553ae30db6e612');");
  }

  $sql = '';
  $items = array();

  if (isset($_POST['search'])) {
    $query = str_replace(";", "", $_POST['search']);
    $sql = 'SELECT * FROM items WHERE name LIKE "%' . $query . '%"';
    $result = $db->query($sql);
    
    while (($res = $result->fetch(PDO::FETCH_ASSOC)) !== false) {
      $items[] = $res;
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
      <form method="POST">
        <div class="form-group">
          <label for="username">Search</label>
          <input type="text" name="search" class="form-control" id="search" />
        </div>

        <button type="submit" class="btn btn-primary">Search</button>
        <br /><br />
        <?php if ($sql) { ?><div class="alert alert-info"><?php echo htmlentities($sql); ?></div> <?php } ?>
        <br /><br />
        <table class="table table-striped">
          <tr>
            <th>Name</th><th>Description</th>
          </tr>
          <?php 
            foreach ($items as $val) {
          ?>
            <tr>
              <td><?php echo $val['name'] ?></td>
              <td><?php echo $val['description'] ?></td>
            </tr>
          <?php 
            }
          ?>
        </table>
      </form>
    </div>
  </body>
</html>
