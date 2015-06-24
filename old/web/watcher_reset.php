<html>
<head>
<title>Password reset</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>

<body>

<?php

$con = mysql_connect("127.0.0.1","sloppyorg_cbid","wmK(********);
if (!$con)
  {
  die('Could not connect: ' . mysql_error());
  }

mysql_select_db("sloppyorg_cb", $con);

if (!empty($_POST['reset'])) {
	reset_pw();
} else {
	if (!empty($_GET['return'])) {
		//show_reset();
		prompt_reset();
	} else {
		if (!empty($_POST['newpassreset'])) {
			final_reset();
		} else {
			show_reset();
			//prompt_reset();
		}
	}
}

function rand_string( $length ) {
	$chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";	

	$size = strlen( $chars );
	for( $i = 0; $i < $length; $i++ ) {
		$str .= $chars[ rand( 0, $size - 1 ) ];
	}

	return $str;
}

function final_reset(){
	$updateresult = mysql_query("UPDATE watcher_list set watcher_pass='" . md5($_POST['newpass']) . "' where watcher_recipient='" . $_POST['user'] . "'");
	if ($updateresult = 1) {
		echo 'Password reset successful. <a href="http://sloppymcnubble.com/cbid/cbid_watcher.php">Click here</a> to log in.';
	} else {
		echo "Password reset not successful.";
	}
}

function prompt_reset() {
	$result = mysql_query("SELECT * from watcher_list where watcher_code='" . $_GET['code'] . "' and watcher_verified='1'");
	$check = mysql_num_rows($result);
	if ($check != 0) {
		//good acct
		while($row = mysql_fetch_array($result))
			{
				$user_recipient = $row['watcher_recipient'];
		}		
?>
		<h4>CBid watcher password reset</h4>

		<form action="<?php echo htmlentities($_SERVER['PHP_SELF']); ?>" method="POST" id="userfrm">
			<fieldset>
				<ol><table>
					<tr><td>New Password:</td><td><input type="password" name="newpass"></input></td></tr>					
					<input type="hidden" name="newpassreset" value="1"></input>
					<input type="hidden" name="user" value="<?php echo $user_recipient ?>"></input>
					</table>
					<button type="submit">Submit</button>
				</ol>
			</fieldset>
		</form>
<?php
	} else { 
		echo "Something is wrong, cannot locate that verification code";
	}
}

function reset_pw() {
	$email = mysql_real_escape_string($_POST['email']);
	$result = mysql_query("SELECT * from watcher_list where watcher_recipient='" . $email . "' and watcher_verified='1'");
	$check = mysql_num_rows($result);
	if ($check != 0) {
		//good email
		$newverif = rand_string(20);
		$updateresult = mysql_query("UPDATE watcher_list set watcher_code='" .$newverif . "' where watcher_recipient='" . $email . "'");
		if ($updateresult = 1) {
			$to = $email;
			$subject = "CBid Watcher Password Reset";
			$message = "Do not reply to this email. Click this link to reset your password: http://sloppymcnubble.com/cbid/watcher_reset.php?return=1&code=" . $newverif;
			$from = "cbid_watcher@sloppymcnubble.com";
			$headers = "From:" . $from;
			mail($to,$subject,$message,$headers);
			echo "Email sent to " . $email . ". Please check your email for the password reset link.";
		} else {
			echo 'Update error';
		};

	} else {
		echo "Cannot locate that email address.";
	}	
	
}

function show_reset() {
?>
		<h4>CBid watcher password reset</h4>
		<form action="<?php echo htmlentities($_SERVER['PHP_SELF']); ?>" method="POST" id="userfrm">
			<fieldset>
				<ol><table>
					<tr><td>Email Address:</td><td><input type="text" name="email"></input></td></tr>					
					<input type="hidden" name="reset" value="1"></input>
					</table>
					<button type="submit">Submit</button>
				</ol>
			</fieldset>
		</form>

<?php
}
?>
</body>
</html>
