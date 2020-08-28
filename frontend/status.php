<?php
$servername = "localhost";
$username = "u80189p74860_oddsmatcher";
$password = "Kq90*r%XXlEXaUIvoxwo";

$green_time = 7*60;
$orange_time = 15*60;
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
</style>
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
        $status = "🟢";
        $diff = gmdate("i:s", $diff);
    } elseif ($diff <= $orange_time) {
        $status = "🟠";
        $diff = gmdate("i:s", $diff);
    } elseif ($diff > $timeout_time) {
        $diff = "∞";
        $status = "❓";
    } else {
        $status = "🔴";
        $diff = "∞";
    }
    if ($table_name == "Spinsports_Matchbook") {
        $status = "🔴";
    }
    if (strpos($table_name, "Matchbook")) {
        echo "<th>$status</th></tr>";
    } else {
        echo "<tr><th>$table_name</th><th>$diff</th><th>$status</th>";
    }
}
?>
</table>
