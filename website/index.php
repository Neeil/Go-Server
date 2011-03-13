<?php
$sql_db = "ai_go";
$sql_user = "ai_go";
$sql_pw = "password";

$db = mysql_connect("localhost", $sql_user, $sql_pw);
mysql_select_db($sql_db, $db);

$bots = array();

$res = mysql_query("SELECT * FROM bots order by name, version DESC;");
while ($row = mysql_fetch_array($res)) {
	$row['wins'] = 0;
	$row['matchs'] = 0;
	$bots[$row['id']] = $row;
}

if (isset($_GET['page']))
{
	$limit = " limit ".($_GET['page'] * 10).",".(($_GET['page']+1)*10);
} else {
	$limit = " limit 0,10";
}


$matchs = array();
if (isset($_GET['name'])) {
	$sql = "SELECT * FROM matchs, bots where (matchs.white_id = bots.id or matchs.black_id=bots.id) and bots.name=\"".$_GET['name']."\" order by date desc ".$limit.";";
//	$statsql = "SELECT black_id, white_id, round(avg(score),1) as 'avg', sum(score) as 'sum', count(*) as 'games' FROM matchs, bots where (matchs.white_id = bots.id or matchs.black_id=bots.id) and bots.name=\"".$_GET['name']."\" group by black_id, white_id;";
	$botname = $_GET['name'];

} else if (isset($_GET['version'])) {
	$sql = "SELECT * FROM matchs where white_id=".$_GET['version']." or black_id=".$_GET['version']." order by date desc ".$limit.";";
//	$statsql = "SELECT black_id, white_id, round(avg(score),1) as 'avg', sum(score) as 'sum', count(*) as 'games' FROM matchs where white_id=".$_GET['version']." or black_id=".$_GET['version']." group by black_id, white_id;";
	$botname = $bots[$_GET['version']]['name'];
	$botversion = $bots[$_GET['version']]['version'];
} else {
	$sql = "SELECT * FROM matchs order by date desc".$limit.";";
//	$statsql = "SELECT black_id, white_id, round(avg(score),1) as 'avg', sum(score) as 'sum', count(*) as 'games' FROM matchs group by black_id, white_id;";
}

$res = mysql_query($sql);
$stats = array();
while ($row = mysql_fetch_array($res)) {
	$matchs[] = $row;
//	$stats[ $bots[ $row['black_id'] ][ 'name' ] ][ 'matchs' ]++;
//	$stats[ $bots[ $row['white_id'] ][ 'name' ] ][ 'matchs' ]++;
//	if ($row['score'] > 0)
//		$stats[ $bots[ $row['black_id'] ][ 'name' ] ][ 'wins' ]++;
//	else if ($row['score'] < 0)
//		$stats[ $bots[ $row['white_id'] ][ 'name' ] ][ 'wins' ]++;

}


$statsql = "SELECT black_id, white_id, round(avg(score),1) as 'avg', sum(score) as 'sum', count(*) as 'games' FROM matchs group by black_id, white_id;";
$res = mysql_query($statsql);
while ($row = mysql_fetch_array($res)) {
	$stats[] = $row;
	$avg[$row['black_id']][$row['white_id']]['total'] += $row['sum'];
	$avg[$row['black_id']][$row['white_id']]['games'] += $row['games'];
	$avg[$row['black_id']][$row['white_id']]['avg'] = round($avg[$row['black_id']][$row['white_id']]['total']/$avg[$row['black_id']][$row['white_id']]['games'],2);
	if ($row['black_id'] != $row['white_id']) {
		$avg[$row['white_id']][$row['black_id']]['total'] += -$row['sum'];
		$avg[$row['white_id']][$row['black_id']]['games'] += $row['games'];
		$avg[$row['white_id']][$row['black_id']]['avg'] = round($avg[$row['white_id']][$row['black_id']]['total']/$avg[$row['white_id']][$row['black_id']]['games'],2);
	}
}

function format_time($time_str)
{
	if ($time_str == "0" or $time_str == null)
		return "?";
	else 
		return round($time_str, 2)."s";
}


?>


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

	<title>ai.mindstab.net: Go competition</title>

	<link rel="stylesheet" href="http://www.mindstab.net/wordpress/wp-content/themes/mindstab3.1/style.css" type="text/css" /> 
	<style type="text/css">
		
		table { 
			padding: 0px;
			border-width: 0px;
			border-collapse: collapse; 

		}

		td, th {
			border: 1px solid black;
			padding: 2px;
			margin: 0px;
			text-align: center;
		}

		.black {
			background: #a0a0a0;
			/*color: #ffffff; */
		}

		td.selected, th.selected {
			background: #cebaee;
		}

		td.unselected {
			background: #e0e0e0;
		}

		#content {
			margin-left: 10px;
		}


	</style>


</head>

<body>
<div id="header">
<img src="http://www.mindstab.net/power.png" align="left" />
<div id="title">
<h1>Mindstab AI: Go Competition</h1>
</div>
</div>
<div id="content">
<p align="right"><a href="/wiki/">Return to Wiki</a></p>
<?php
if (isset($_GET['name']) or isset($_GET['version'])) {
print "<a href=\"?\">All Matchs</a><br>";
print "<h2>$botname $botversion</h2>";
print "<a href=\"/wiki/index.php/$botname\">Wiki entry for $botname</a><br/><br/>";
}/*
$bot = $stats[$botname];
print "<table><tr><th>Wins</th><th>Percent</th></tr>";
print "<tr>";
print "<td>".(isset($bot['wins']) ? $bot['wins'] : '0')."/".$bot['matchs'] . "</td><td>".round($bot['wins']/$bot['matchs']*100)."%</td></tr>";

print "</table>";


} else {
print "<h2>Bot Stats</h2>";
print "<table><tr><th>Bot</th><th>Wins</th><th>Percent</th></tr>";
foreach ($stats as $name => $bot) {
print "<tr><td><a href=\"?name=".$name."\">".$name."</a></td>";
print "<td>".(isset($bot['wins']) ? $bot['wins'] : '0')."/".$bot['matchs'] . "</td><td>".round($bot['wins']/$bot['matchs']*100)."%</td></tr>";
$botname="";
}
print "</table>";
}*/

//print "<pre>";
//print_r($avg);
//print "</pre><br>";

print "<h2>Agerage Scores</h2>"; //These stats wont make sense if handicapping is added
print "<table><tr><th>Black \ White</th>";
foreach ($bots as $bot) {
	if ($bot['version'] == $botversion || (!isset($botversion) && $bot['name'] == $botname))
	{
		print "<th class=\"selected white\">";
	} else if (!isset($botname)) {
		print "<th class=\"white\">";
	} else {
		print "<th class=\"unselected white\">";
	}
		
	print "<a href=\"?name=".$bot['name']."\">".$bot['name']."</a>";
	print " - <a href=\"?version=".$bot['id']."\">".$bot['version']."</a></th>";
}
foreach ($bots as $black) {
	print "<tr>";
	if ($black['version'] == $botversion || (!isset($botversion) && $black['name'] == $botname))
	{
		print "<th class=\"selected black\">";
	} else if (!isset($botname)) {
		print "<th class=\"black\">";
	} else {
		print "<th class=\"unselected black\">";
	}
	print "<a href=\"?name=".$black['name']."\">".$black['name']."</a>";
	print " - <a href=\"?version=".$black['id']."\">".$black['version']."</a></th>";
	foreach ($bots as $white) {
		if ($white['version'] == $botversion || $black['version'] == $botversion || (!isset($botversion) && ($white['name'] == $botname || $black['name'] == $botname)))
		{
			print "<td class=\"selected ";
		} else if (!isset($botname)) {
			print "<td class=\" ";
		} else {
			print "<td class=\"unselected ";
		}
		if (isset($avg[$black['id']][$white['id']]['avg']))
		{
			$score =  $avg[$black['id']][$white['id']]['avg'];
			if ($score >= 0) {
				$score = "B+$score";
				if ($black['name'] == $botname)
					$score = "<b>".$score."</b>";
			} else {
				$score="W+".abs($score);
				if ($white['name'] == $botname)
					$score = "<b>".$score."</b>";
			}
			if (substr($score, 0, 1) == "W")
				print " white\">".$score;
			else
				print " black\">".$score;
		} else {
			print " empty\">";
		}
		print "</td>\n";
	}
	print "</tr>\n";
}

print "</tr>";

print "</table>";

/*
print "<table><tr><th>Black</th><th>White</th><th>Games Played</th><th>Average Score</th></tr>";
foreach ($stats as $stat) {
	print "<tr>";
	print "<td><a href=\"?name=".$bots[$stat['black_id']]['name']."\">".$bots[$stat['black_id']]['name'] . "</a>";
	print " - <a href=\"?version=" .$stat['black_id']. "\">" .$bots[$stat['black_id']]['version'] ."</a></td>";
	print "<td><a href=\"?name=".$bots[$stat['white_id']]['name']."\">".$bots[$stat['white_id']]['name'] . "</a>";
	print " - <a href=\"?version=" .$stat['white_id']. "\">" .$bots[$stat['white_id']]['version'] ."</a></td>";
	print "<td>".$stat['games']."</td>";
	$score = $stat['avg'];
	if ($score >= 0) {
		$score = "B+$score";

		print "<td>".$score."</td>";
	} else {
		$score="W+".abs($score);
		print "<td>".$score."</td>";
	}
	print "</tr>";
}
print "</table>";
*/

?>

<h2>Matchs</h2>
<table>
<tr><th>Black</th><th>White</th><th>Score</th><th>Date</th><th>Black Time</th><th>White Time</th><th>Handicap</th><th>SGF file</th></tr>
<?php
foreach ($matchs as $match) {
	print "<tr>";
	print "<td><a href=\"?name=".$bots[$match['black_id']]['name']."\">".$bots[$match['black_id']]['name'] . "</a>";
	print " - <a href=\"?version=" .$match['black_id']. "\">" .$bots[$match['black_id']]['version'] ."</a></td>";
	print "<td><a href=\"?name=".$bots[$match['white_id']]['name']."\">".$bots[$match['white_id']]['name'] . "</a>";
	print " - <a href=\"?version=" .$match['white_id']. "\">" .$bots[$match['white_id']]['version'] ."</a></td>";
	$score = $match['score'];
	if ($score >= 0) {
		$score = "B+$score";
		if ($bots[$match['black_id']]['name'] == $botname)
			$score = "<b>$score</b>";
	} else {
		$score="W+".abs($score);
		if ($bots[$match['white_id']]['name'] == $botname)
			$score = "<b>$score</b>";
	}

	
	print "<td>".$score."</td>";
	print "<td>" . $match['date']."</td>";
	print "<td>". format_time($match['black_time'], 2)."</td>";
	print "<td>". format_time($match['white_time'], 2)."</td>";
	print "<td>".$match['handicap']."</td>";
	print "<td><a href=\"/go/sgf/".$match['sgffile']."\"><img src=\"/go/sgf/".str_replace("sgf","png",$match['sgffile'])."\" alt=\"SGF File\"></a></td>";
	print "</tr>";
}
print "</table>";
if (isset($_GET['name']))
{
	$args = "name=".$_GET['name']."&";
} else if (isset($_GET['version'])) {
	$args = "version=".$_Get['version']."&";
}
if (isset($_GET['page']))
{
	print "<br><a href=\"?".$args."page=".($_GET['page']-1)."\">Prev</a>";
	print " - <a href=\"?".$args."page=1\">Next</a>";
} else {
	print "<a href=\"?".$args."page=1\">Next</a>";
}
?>
</div>
</body>
</html>
