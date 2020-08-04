<?php
$servername = "localhost";
$username = "u80189p74860_oddsmatcher";
$password = "Kq90*r%XXlEXaUIvoxwo";

//Check if request comes from the oddsmatcher pages, else return nothing.
if ($_SERVER["HTTP_REFERER"] != "https://www.rickproductions.nl/oddsmatcher-dev/" && $_SERVER["HTTP_REFERER"] != "https://www.rickproductions.nl/oddsmatcher/") {
  http_response_code(403);
  exit();
}

// Create connection
$mysqli = new mysqli($servername, $username, $password, $username);

// Check connection
if ($mysqli->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}
if($_POST['bookmaker']) {
  $bookmaker = $_POST['bookmaker'];
} else {
  $bookmaker = "Spinsports";
}
if ($bookmaker == "Spinsports") {
  $order = "Loss";
} else {
  $order = "Closeness";
}

//Check if filter has been posted
if ($_POST) {
  //Add extra conditions to query
  //DONT FORGET TO ADD SPACE TO THE START OF NEW ADDITION!!
  $query_extra = "";
  if ($_POST['time_range']) {
    //Set the timerange slider to the posted value, with ugly javascript
    $timerange = $_POST['time_range'];
    $timerange_original = $timerange;
    $timerange = "$timerange:00";
    $current_date = date("d-m");
    $query_extra = "$query_extra WHERE Time < '$timerange'";
    if ($timerange_original < 25) {
      $query_extra = "$query_extra AND Date = '$current_date'";
    }
  } 
  if ($_POST['min_odds']) {
      $min_odds = $_POST['min_odds'];
      $query_extra = "$query_extra AND BookmakerOdds > $min_odds";
  }
  if ($_POST['max_odds']) {
      $max_odds = $_POST['max_odds'];
      $query_extra = "$query_extra AND BookmakerOdds < $max_odds";
  }
  if ($_POST['min_liquidity']) {
    $min_liquidity = $_POST['min_liquidity'];
    $query_extra = "$query_extra AND Liquidity > $min_liquidity";
  }
  $query = "SELECT MatchName, BookmakerOdds, ExchangeOdds, Closeness, Date, Time, Loss, Bet, Liquidity FROM $bookmaker $query_extra ORDER BY $order DESC";
} else {
  $query = "SELECT MatchName, BookmakerOdds, ExchangeOdds, Closeness, Date, Time, Loss, Bet, Liquidity FROM $bookmaker ORDER BY $order DESC";
}
//$query = "SELECT MatchName, BookmakerOdds, ExchangeOdds, Closeness, Date, Time, Loss, Bet, Liquidity FROM $bookmaker ORDER BY $order DESC";
$results=mysqli_query($mysqli,$query);
$row_count=mysqli_num_rows($results);

while ($row = mysqli_fetch_array($results)) {
    $rows[] = $row;
}
echo json_encode($rows);
?>