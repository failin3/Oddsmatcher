<?php
$servername = "localhost";
$username = "u80189p74860_oddsmatcher";
$password = "Kq90*r%XXlEXaUIvoxwo";

$green_time = 5;
$orange_time = 10;


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

<table>
    <tr>
        <th>Table Name</th>
        <th>Time Last Update</th>
        <th>Status</th>
    </tr>

<?php
while ($row = mysqli_fetch_array($results)) {
    $table_name = $row['TABLE_NAME'];
    //Ignore Spinsports_Matchbook, it has not been implemented yet, and might never
    if ($table_name == "Spinsports_Matchbook") {
        continue;
    }
    $update_time = strtotime($row['UPDATE_TIME']);
    $now = time();
    $diff = round(($now - $update_time)/60); //Difference in time in minutes
    if ($diff <= $green_time) {
        $status = "🟢";
    } elseif ($diff <= $orange_time) {
        $status = "🟠";
    } else {
        $diff = "∞";
        $status = "🔴";
    }
    echo "<tr><th>$table_name</th><th>$diff:00</th><th>$status</th></tr>";
}
?>
</table>