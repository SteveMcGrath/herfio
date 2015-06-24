<?php
setlocale(LC_MONETARY, 'en_US');

$dbtype = 'mysql';
	
function db_open() {
	global $dbtype;
	try {
		if ($dbtype == 'mysql') {
			$hostname = '127.0.0.1';
			$username = 'sloppyorg_cbid';
			$password = '******';
			return new PDO("mysql:host=$hostname;dbname=sloppyorg_cb", $username, $password);
		} else {
			return new PDO("sqlite:cigarbid.db");
		}
	} catch(PDOException $e) {
		die($e->getMessage());
	}
}
	
//if ($_GET['logout'] = 'true') {
//	$_SESSION['user'] = '';
//}

$con = mysql_connect("127.0.0.1","sloppyorg_cbid","wmK(********);
if (!$con)
  {
  die('Could not connect: ' . mysql_error());
  }

mysql_select_db("sloppyorg_cb", $con);


//try to locate user login
if (empty($_SESSION['user'])) {
	if (!empty($_POST['user'])) {
		$result = mysql_query("SELECT * from watcher_list where watcher_user='" . $_POST['user'] . "' and watcher_pass='" . $_POST['pass'] . "'");
		$check = mysql_num_rows($result);
		if ($check != 0) {
			$_SESSION['user'] = $_POST['user'];
			//echo "Login complete, redirecting...";
			header('Location: '.$_SERVER['REQUEST_URI']);
			//$_SERVER['REQUEST_URI'];
		} else {
			echo "Incorrect username or password.";
		}
	}

?>
<html>
<head>
<title>CBid Watcher</title>
<link rel=stylesheet href=style.css type=text/css>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>

<body>


		<form action="<?php echo htmlentities($_SERVER['PHP_SELF']); ?>" method="POST" id="searchfrm">
			<fieldset>
				<ol><table>
					<tr><td>Username:</td><td><input type="text" name="user"></input></td></tr>
					<tr><td>Password:</td><td><input type="text" name="pass"></input></td></tr>
					</table>
					<button type="submit">Submit</button>
				</ol>
			</fieldset>
		</form>
		User: <?php echo $_SESSION['user']; ?><br>
<?php
} else {
//Logged in at this point

//Update table with changes
if (!empty($_POST['searchstr'])) {
	$updateresult = mysql_query("UPDATE watcher_list set watcher_searches='" . $_POST['searchstr'] . "', watcher_recipient='" . $_POST['email'] . "' where watcher_user='" . $_POST['user'] . "'");
	if ($updateresult = 1) {
		echo 'Update complete';
	} else {
		echo 'Update error';
	};
}
//Show change form
$result = mysql_query("SELECT * from watcher_list where watcher_user='" . $_SESSION['user'] . "'");
while($row = mysql_fetch_array($result))
	{
		$user_recipient = $row['watcher_recipient'];
		$user_searches =  $row['watcher_searches'];
	}

?>
<html>
<head>
<title>CBid Watcher</title>
<link rel=stylesheet href=style.css type=text/css>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>

<body>


	<form action="<?php echo htmlentities($_SERVER['PHP_SELF']); ?>" method="POST" id="searchfrm">
		<fieldset>
			<ol><table>
				<tr><td>Email:</td><td><input type="text" name="email" value="<?php echo $user_recipient; ?>"></input></td></tr>
				<tr><td>Search Strings:</td><td><input type="text" name="searchstr" value="<?php echo $user_searches; ?>"></input></td></tr>
				<input type="hidden" name="user" value="<?php echo $_POST['user']; ?>"></input>
				<input type="hidden" name="pass" value="<?php echo $_POST['pass']; ?>"></input>
				</table>
				<button type="submit">Submit</button>
				<a href="<?php echo htmlentities($_SERVER['PHP_SELF']); ?>?logout=true"><button>Log out</button></a>
			</ol>
		</fieldset>
	</form>
	User: <?php echo $_SESSION['user']; ?><br>
<?php

}
//end of main if
mysql_close($con);
?>
</body>
</html>
