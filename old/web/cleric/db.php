<?
	$dbtype = 'mysql';
		
	function db_open() {
		global $dbtype;
		try {
			if ($dbtype == 'mysql') {
				$hostname = '127.0.0.1';
				$username = 'sloppyorg_cbid';
				$password = '*******';
				return new PDO("mysql:host=$hostname;dbname=sloppyorg_cb", $username, $password);
			} else {
				return new PDO("sqlite:cigarbid.db");
			}
		} catch(PDOException $e) {
		    die($e->getMessage());
	    }
	}
?>