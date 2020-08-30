<?php
$servername = "localhost";
$username = "u80189p74860_oddsmatcher";
$password = "Kq90*r%XXlEXaUIvoxwo";

$green_time = 15*60;
$orange_time = 30*60;
$timeout_time = 10000*60;


// Create connection
$mysqli = new mysqli($servername, $username, $password, $username);

// Check connection
if ($mysqli->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}
$query = "SELECT TABLE_NAME, UPDATE_TIME FROM information_schema.tables WHERE TABLE_SCHEMA = 'u80189p74860_oddsmatcher' ORDER BY TABLE_NAME ASC";
$results=mysqli_query($mysqli,$query);
$row_count=mysqli_num_rows($results);
?>
<head>
  <title>Oddsmatcher Status</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<h1 style="text-align: center; font-family: arial, sans-serif;">Status</h1>
<style>
table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
}

td, th {
  border: 1px solid #dddddd;
  text-align: center;
  padding: 8px;
}

tr:nth-child(even) {
  background-color: #dddddd;
}
.green-dot {
    height: 20px;
    width: 20px;
    background-color: #16c60c;
    border-radius: 50%;
    display: inline-block;
}
.orange-dot {
    height: 20px;
    width: 20px;
    background-color: orange;
    border-radius: 50%;
    display: inline-block;
}
.red-dot {
    height: 20px;
    width: 20px;
    background-color: red;
    border-radius: 50%;
    display: inline-block;
}
@media all and (max-width: 800px) {
    .legenda {
        display: none;
    }
}
</style>
<div style="
    display: flex;
    width: 100%;
    padding: 0;
    margin: 0;
    display: -webkit-box;
    display: -moz-box;
    display: -ms-flexbox;
    display: -webkit-flex;
    display: flex;
    justify-content: center;
">
<div>
<table style="margin-left: auto; margin-right: auto;">
    <tr>
        <th>Table Name</th>
        <th>Time Last Update</th>
        <th>Betfair</th>
        <th>Matchbook</th>
    </tr>

<?php
while ($row = mysqli_fetch_array($results)) {
    $table_name = $row['TABLE_NAME'];
    //Ignore Spinsports_Matchbook, it has not been implemented yet, and might never
    $update_time = strtotime($row['UPDATE_TIME']);
    $now = time();
    $diff = $now - $update_time; //Difference in time in seconds
    if ($diff <= $green_time) {
        $status = "<span class='green-dot'></span>";
        $diff = gmdate("i:s", $diff);
    } elseif ($diff <= $orange_time) {
        $status = "<span class='orange-dot'></span>";
        $diff = gmdate("i:s", $diff);
    } elseif ($diff > $timeout_time) {
        $diff = "∞";
        $status = "❓";
    } else {
        $status = "<span class='red-dot'></span>";
        $diff = gmdate("H:i:s", $diff);
    }
    if ($table_name == "Spinsports_Matchbook") {
        $status = "<span class='red-dot'></span>";
    }
    if (strpos($table_name, "Matchbook")) {
        echo "<th>$status</th></tr>";
    } else {
        echo "<tr><th>$table_name</th><th>$diff</th><th>$status</th>";
    }
}
?>
</table>
</div>
<div class="legenda" style="
float: left; 
padding-left: 20px;
padding-top: 35px;">
    <table>
        <tr style="background-color: #ffffff;">
            <th style="border: 0px solid #dddddd;"><span class='green-dot'></span></th>
            <th style="border: 0px solid #dddddd;"> < <?php echo $green_time/60; ?> minutes</th>
        </tr>
        <tr style="background-color: #ffffff;">
            <th style="border: 0px solid #dddddd;"><span class='orange-dot'></span></th>
            <th style="border: 0px solid #dddddd;"> < <?php echo $orange_time/60; ?> minutes</th>
        </tr>
        <tr style="background-color: #ffffff;">
            <th style="border: 0px solid #dddddd;"><span class='red-dot'></span></th>
            <th style="border: 0px solid #dddddd;"> > <?php echo $orange_time/60; ?> minutes</th>
        </tr>
        <tr style="background-color: #ffffff;">
            <th style="border: 0px solid #dddddd;">❓</th>
            <th style="border: 0px solid #dddddd;">MySQL Bug</th>
        </tr>
    </table>
</div>
</div>
