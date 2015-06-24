<html>
<head>
<title>CBid Watcher Verification</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>

<body>
<?php 
	if (isset($_POST['user'])) {
	//verify new user
			$con = mysql_connect("127.0.0.1","sloppyorg_cbid","wmK(*******);
			if (!$con)
			  {
			  die('Could not connect: ' . mysql_error());
			  }
			
			mysql_select_db("sloppyorg_cb", $con);
			$user = mysql_real_escape_string($_POST['user']);
			$pass = md5(mysql_real_escape_string($_POST['pass']));
			$code = mysql_real_escape_string($_POST['code']);
			$result = mysql_query("SELECT * from watcher_list where watcher_user='" . $user . "' and watcher_pass='" . $pass . "' and watcher_code='" . $code . "'");
			//echo "SELECT * from watcher_list where watcher_user='" . $user . "' and watcher_pass='" . $pass . "' and watcher_code='" . $code . "' <br>";
			$check = mysql_num_rows($result);
			if ($check != 0) {
				//good login
				$_SESSION['user'] = $_POST['user'];
				$updateresult = mysql_query("UPDATE watcher_list set watcher_verified='1' where watcher_user='" . $_POST['user'] . "' and watcher_code='" . $code . "'");
				if ($updateresult = 1) {
					echo 'User verified.<br><a href="http://sloppymcnubble.com/cbid/cbid_watcher.php">Go here</a> to set up searches.';
				} else {
					echo 'Update error. User not verified.';
				};				
			} else {
				//bad login
				echo "Incorrect username, password, or verification code.";
			}

	} else {

?>
		<h4>User Verification</h4>
		<form action="<?php echo htmlentities($_SERVER['PHP_SELF']); ?>" method="POST" id="userfrm">
			<fieldset>
				<ol><table>
					<tr><td>Username:</td><td><input type="text" name="user"></input></td></tr>				
					<tr><td>Password:</td><td><input type="password" name="pass"></input></td></tr>					
					<input type="hidden" name="code" value="<?php echo $_GET['code']; ?>"></input>
					</table>
					<button type="submit">Verify</button>
				</ol>
			</fieldset>
		</form>

<?php
}
?>
</body>
</html>
