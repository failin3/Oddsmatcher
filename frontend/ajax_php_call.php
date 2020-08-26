<?php
$servername = "localhost";
$username = "u80189p74860_oddsmatcher";
$password = "Kq90*r%XXlEXaUIvoxwo";

//Check if request comes from the oddsmatcher pages, else return nothing.
if ( $_SERVER["HTTP_REFERER"] != "https://www.rickproductions.nl/oddsmatcher-dev/" && $_SERVER["HTTP_REFERER"] != "https://www.rickproductions.nl/oddsmatcher/") {
  //http_response_code(403);
  //exit();
}

// Create connection
$mysqli = new mysqli($servername, $username, $password, $username);

// Check connection
if ($mysqli->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}
//Make sure to update this when adding new bookmakers
//Check this to prevent MYSQL injection
$bookmaker_array = ["Spinsports", "Neobet", "Casinowinner", "Betsson", "Betsafe", "Betrebels", "888sport", "Intertops", "Bet90", "Betathome", "Unibet", "LVBet", "Energybet"];
if($_POST['bookmaker'] && in_array($_POST['bookmaker'], $bookmaker_array)) {
  $bookmaker = $_POST['bookmaker'];
} else {
  $bookmaker = "Intertops";
}
if ($bookmaker == "Spinsports") {
  $order = "Loss";
} else {
  $order = "Closeness";
}
$exchange = "Betfair";
if ($_POST["exchange"] == "Matchbook") {
  $bookmaker = "{$bookmaker}_Matchbook";
  $exchange = "Matchbook";
}

$query_extra = "";
//Check if filter has been posted
if ($_POST) {
  //Add extra conditions to query
  //DONT FORGET TO ADD SPACE TO THE START OF NEW ADDITION!!
  if ($_POST['max_time']) {
    //Set the timerange slider to the posted value, with ugly javascript
    $timerange = $_POST['max_time'];
    $min_time = $_POST['min_time'];
    $timerange_original = $timerange;
    $current_date = date("d-m");
    if ($timerange != "∞") {
      $query_extra = "$query_extra WHERE Time <= '$timerange' AND Time >= '$min_time' AND Date = '$current_date'";
    } else {
      $query_extra = "$query_extra WHERE (Date > '$current_date' OR Time >= '$min_time')";
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
  $query = "SELECT MatchName, BookmakerOdds, ExchangeOdds, Closeness, Date, Time, Loss, Bet, Liquidity, Url, '$exchange' AS Exchange FROM $bookmaker $query_extra ORDER BY $order DESC";
} else {
  $query = "SELECT MatchName, BookmakerOdds, ExchangeOdds, Closeness, Date, Time, Loss, Bet, Liquidity, Url, '$exchange' AS Exchange FROM $bookmaker ORDER BY $order DESC";
}
if ($_POST["exchange"] == "Both") {
  $query = "SELECT MatchName, BookmakerOdds, ExchangeOdds, Closeness, Date, Time, Loss, Bet, Liquidity, Url, 'Matchbook' AS Exchange FROM {$bookmaker}_Matchbook $query_extra UNION $query";
}

//echo $query;
//$query = "SELECT MatchName, BookmakerOdds, ExchangeOdds, Closeness, Date, Time, Loss, Bet, Liquidity FROM $bookmaker ORDER BY $order DESC";
$results=mysqli_query($mysqli,$query);
$row_count=mysqli_num_rows($results);
while ($row = mysqli_fetch_array($results)) {
    $rows[] = array_map('utf8_encode', $row);
}
echo json_encode($rows);
?>