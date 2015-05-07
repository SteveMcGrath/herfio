<html>
<head>
<title>CBid Watcher Signup</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>

<body>
<?php 
function rand_string( $length ) {
	$chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";	

	$size = strlen( $chars );
	for( $i = 0; $i < $length; $i++ ) {
		$str .= $chars[ rand( 0, $size - 1 ) ];
	}

	return $str;
}
	if (isset($_POST['newuser'])) {
	//create new user
			$con = mysql_connect("127.0.0.1","sloppyorg_cbid","wmK(*******);
			if (!$con)
			  {
			  die('Could not connect: ' . mysql_error());
			  }
			
			mysql_select_db("sloppyorg_cb", $con);
			
			$newemail = mysql_real_escape_string($_POST['newemail']);
			$newpass = md5(mysql_real_escape_string($_POST['newpass']));
			$newusername = mysql_real_escape_string($_POST['newusername']);
			$newverif = rand_string(20);
			$result = mysql_query("SELECT * from watcher_list where watcher_user='" . $newusername . "'");
			$check = mysql_num_rows($result);
			if ($check != 0) {
				//username taken
				echo "Sorry, that username is taken";
			} else {
				//new username
				$updateresult = mysql_query("INSERT INTO watcher_list(watcher_recipient, watcher_user, watcher_pass, watcher_verified, watcher_code) VALUES('" . $newemail . "','" . $newusername . "','" . $newpass . "','0','" . $newverif . "')");
				if ($updateresult = 1) {
					$to = $newemail;
					$subject = "CBid Watcher Verification";
					$message = "Do not reply to this email. Click this link to continue verification: http://sloppymcnubble.com/cbid/watcher_verif.php?code=" . $newverif;
					$from = "cbid_watcher@sloppymcnubble.com";
					$headers = "From:" . $from;
					mail($to,$subject,$message,$headers);
					echo "Email sent to " . $_POST['newemail'] . ". Please check your email for the verification link.";
	
				} else {
					echo 'Update error';
				};
			}

	} else {

?>
		<h4>CBid Watcher User Sign Up</h4>
		<form action="<?php echo htmlentities($_SERVER['PHP_SELF']); ?>" method="POST" id="userfrm">
			<fieldset>
				<ol><table>
					<tr><td>Username:</td><td><input type="text" name="newusername"></input></td></tr>				
					<tr><td>Email:</td><td><input type="text" name="newemail"></input></td></tr>
					<tr><td>Password:</td><td><input type="password" name="newpass"></input></td></tr>					
					<input type="hidden" name="user" value="<?php echo $_SESSION['user']; ?>"></input>
					<input type="hidden" name="newuser" value="1"></input>
					</table>
					<button type="submit">Sign Up</button>
				</ol>
			</fieldset>
		</form>

<?php
}
?>
</body>
</html>
