<?php
session_start();
	
if (isset($_GET['logout'])) {
//log current session out
	unset($_SESSION['user']);
	echo "Session logged out<br>";
}

$con = mysql_connect("127.0.0.1","sloppyorg_cbid","wmK(*******);
if (!$con)
  {
  die('Could not connect: ' . mysql_error());
  }

mysql_select_db("sloppyorg_cb", $con);


function show_login() {
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
						<tr><td>Password:</td><td><input type="password" name="pass"></input></td></tr>
						</table>
						<button type="submit">Submit</button>
					</ol>
				</fieldset>
			</form>
			<a href="watcher_reset.php">I forgot my password</a>
	</body>
	</html>

	<?php
}

function show_search() {
//Logged in at this point

	if (isset($_POST['newuser'])) {
	//create new user
			$newemail = mysql_real_escape_string($_POST['newemail']);
			$newpass = md5(mysql_real_escape_string($_POST['newpass']));
			$newusername = mysql_real_escape_string($_POST['newusername']);
			$updateresult = mysql_query("INSERT INTO watcher_list(watcher_recipient, watcher_user, watcher_pass) VALUES('" . $newemail . "','" . $newusername . "','" . $newpass . "')");
			if ($updateresult = 1) {
				echo $_POST['newusername'] . ' user added';
			} else {
				echo 'Update error';
			};
	
	}
	
	if (isset($_POST['deluser'])) {
	//delete user
			$delusername = mysql_real_escape_string($_POST['delusername']);
			$updateresult = mysql_query("DELETE FROM watcher_list where watcher_user='" . $delusername . "'");
			if ($updateresult = 1) {
				echo $_POST['delusername'] . 'user deleted';
			} else {
				echo 'Update error';
			};
	
	}
	
	//Update user table with changes if there are any
	if (!empty($_POST['email'])) {
		$searchstr = mysql_real_escape_string($_POST['searchstr']);
		$email = mysql_real_escape_string($_POST['email']);
		$cm = mysql_real_escape_string($_POST['cm']);
		$updateresult = mysql_query("UPDATE watcher_list set watcher_searches='" .$searchstr . "', watcher_recipient='" . $email . "', watcher_cm='" . $cm . "' where watcher_user='" . $_SESSION['user'] . "'");

		if ($updateresult = 1) {
			echo 'Update complete';
		} else {
			echo 'Update error';
		};
	}
	//get data for change form
	$result = mysql_query("SELECT * from watcher_list where watcher_user='" . $_SESSION['user'] . "'");
	while($row = mysql_fetch_array($result))
		{
			$user_recipient = $row['watcher_recipient'];
			$user_searches =  $row['watcher_searches'];
			$user_admin = $row['watcher_admin'];
			$user_cm = $row['watcher_cm'];
			if ($user_cm == 1) {
				$checkstr = 'checked';
			} else {
				$checkstr = '';
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
					<tr><td>Email:</td><td width="80%"><input type="text" name="email" value="<?php echo $user_recipient; ?>"></input></td></tr>
					<tr><td>Search Strings:</td><td width="80%"><input type="text" name="searchstr" value="<?php echo $user_searches; ?>"></input></td></tr>
					<tr><td>Include CigarMonster</td><td width="80%"><input type="checkbox" name="cm" value="1" <?php echo $checkstr; ?>></input>
					<input type="hidden" name="user" value="<?php echo $_SESSION['user']; ?>"></input>
					</table>
					<button type="submit">Submit</button>
				</ol>
			</fieldset>
		</form>
		User: <?php echo $_SESSION['user']; ?><br>
		<font color=white>
		<table>
		<tr><td width=50%>
		<table border=1>
		<th><font color=white><b>Your Searches</b></font></th>		
		<?php
		$slist = preg_split('/,/',$user_searches) ;
		foreach ($slist as $search) {
		?>
		<tr><td><font color=white><?php echo $search ; ?></font></td></tr>
		<?php 
		}
		?>
		</table></td><td>
		<font color=white>
		<i>Instructions:</i><br>
		-Emails are sent at Noon ET and 10PM ET daily. <br>
		-In the search criteria, enter a list of comma delimited strings you want to find. <br>
		-Only lot names are searched (not description, etc). <br>
		-The search is not case sensitive.<br>
		-For instance "tatuaje,vsg" will return all auctions with Tatuaje OR VSG in their lot name.<br>
		</font>
		</td></tr></table>
		<a href="<?php echo htmlentities($_SERVER['PHP_SELF']); ?>?logout=now">Log out</a>
		
	<?php 
	//check for admin
	if ($user_admin == '1') {
		//show new user,delete user forms
		?>

		<h2>User Administration</h2>
		<h4>Create new user</h4>
		<form action="<?php echo htmlentities($_SERVER['PHP_SELF']); ?>" method="POST" id="userfrm">
			<fieldset>
				<ol><table>
					<tr><td><font color=white>Username:</font></td><td><input type="text" name="newusername"></input></td></tr>				
					<tr><td><font color=white>Email:</font></td><td><input type="text" name="newemail"></input></td></tr>
					<tr><td><font color=white>Password:</font></td><td><input type="password" name="newpass"></input></td></tr>					
					<input type="hidden" name="user" value="<?php echo $_SESSION['user']; ?>"></input>
					<input type="hidden" name="newuser" value="1"></input>
					</table>
					<button type="submit">Create User</button>
				</ol>
			</fieldset>
		</form>
		<h4>Delete user</h4>
		<form action="<?php echo htmlentities($_SERVER['PHP_SELF']); ?>" method="POST" id="delfrm">
			<fieldset>
				<ol><table>
					<tr><td><font color=white>Username:</font></td><td><input type="text" name="delusername"></input></td></tr>				
					<input type="hidden" name="user" value="<?php echo $_SESSION['user']; ?>"></input>
					<input type="hidden" name="deluser" value="1"></input>
					</table>
					<button type="submit">Delete User</button>
				</ol>
			</fieldset>
		</form>
		<h4>Current Users</h4>
		<table border=1>
		<tr><th><font color=white>Username</font></th><th><font color=white>Email</font></th><th><font color=white>Searches</font></th><th><font color=white>Admin</font></th></tr>
		<?php
		//list current users
		$result = mysql_query("SELECT * from watcher_list");
		while($row = mysql_fetch_array($result))
			{
			?>
			<tr><td><font color=white><?php echo $row['watcher_user'] ; ?></font></td><td><font color=white><?php echo $row['watcher_recipient'] ; ?></font></td><td><font color=white><?php echo $row['watcher_searches'] ; ?></font></td><td><font color=white><?php echo $row['watcher_admin'] ; ?></font></td></tr>
			<?php
			}
		
		?>
		</table>
		<?php
	}
	?>

	</body>
	</html>
	<?php
}

//try to locate user login
if (!isset($_SESSION['user'])) {
//if (!isset($_SESSION['user']) || $_SESSION['user'] == '') {
	//echo "User session not set<br>";
	if (!empty($_POST['user'])) {
		//echo "User post set<br>";
		//login attempt
		$user = mysql_real_escape_string($_POST['user']);
		$pass = md5(mysql_real_escape_string($_POST['pass']));
		$result = mysql_query("SELECT * from watcher_list where watcher_user='" . $user . "' and watcher_pass='" . $pass . "' and watcher_verified='1'");
		$check = mysql_num_rows($result);
		if ($check != 0) {
			//good login
			$_SESSION['user'] = $_POST['user'];
			show_search();
			//exit();
		} else {
			//bad login
			echo "<a font=white>Incorrect username or password.</font>";
			show_login();
		}
	} else {
		//not logged in
		show_login();
	}
} else {
	//already logged in
	show_search();
}

?>
