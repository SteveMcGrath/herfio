<?php
	setlocale(LC_MONETARY, 'en_US');

	$dbtype = 'mysql';
	
	function db_open() {
		global $dbtype;
		try {
			if ($dbtype == 'mysql') {
				$hostname = '127.0.0.1';
				$username = 'sloppyorg_cbid';
				$password = 'wmK(*******';
				return new PDO("mysql:host=$hostname;dbname=sloppyorg_cb", $username, $password);
			} else {
				return new PDO("sqlite:cigarbid.db");
			}
		} catch(PDOException $e) {
		    die($e->getMessage());
	    }
	}

	function getBrowser() 
	{ 
		$u_agent = $_SERVER['HTTP_USER_AGENT']; 
		$bname = 'Unknown';
		$platform = 'Unknown';
		$version= "";
	
		//First get the platform?
		if (preg_match('/linux/i', $u_agent)) {
			$platform = 'linux';
		}
		elseif (preg_match('/macintosh|mac os x/i', $u_agent)) {
			$platform = 'mac';
		}
		elseif (preg_match('/windows|win32/i', $u_agent)) {
			$platform = 'windows';
		}
		
		// Next get the name of the useragent yes seperately and for good reason
		if(preg_match('/MSIE/i',$u_agent) && !preg_match('/Opera/i',$u_agent)) 
		{ 
			$bname = 'Internet Explorer'; 
			$ub = "MSIE"; 
		} 
		elseif(preg_match('/Firefox/i',$u_agent)) 
		{ 
			$bname = 'Mozilla Firefox'; 
			$ub = "Firefox"; 
		} 
		elseif(preg_match('/Chrome/i',$u_agent)) 
		{ 
			$bname = 'Google Chrome'; 
			$ub = "Chrome"; 
		} 
		elseif(preg_match('/Safari/i',$u_agent)) 
		{ 
			$bname = 'Apple Safari'; 
			$ub = "Safari"; 
		} 
		elseif(preg_match('/Opera/i',$u_agent)) 
		{ 
			$bname = 'Opera'; 
			$ub = "Opera"; 
		} 
		elseif(preg_match('/Netscape/i',$u_agent)) 
		{ 
			$bname = 'Netscape'; 
			$ub = "Netscape"; 
		} 
		
		// finally get the correct version number
		$known = array('Version', $ub, 'other');
		$pattern = '#(?<browser>' . join('|', $known) .
		')[/ ]+(?<version>[0-9.|a-zA-Z.]*)#';
		if (!preg_match_all($pattern, $u_agent, $matches)) {
			// we have no matching number just continue
		}
		
		// see how many we have
		$i = count($matches['browser']);
		if ($i != 1) {
			//we will have two since we are not using 'other' argument yet
			//see if version is before or after the name
			if (strripos($u_agent,"Version") < strripos($u_agent,$ub)){
				$version= $matches['version'][0];
			}
			else {
				$version= $matches['version'][1];
			}
		}
		else {
			$version= $matches['version'][0];
		}
		
		// check if we have a number
		if ($version==null || $version=="") {$version="?";}
		
		return array(
			'userAgent' => $u_agent,
			'name'      => $bname,
			'version'   => $version,
			'platform'  => $platform,
			'pattern'    => $pattern
		);
	}

	if(!empty($_GET['issearch'])){
		if (!empty($_GET['sortstr'])){
			$sortstr = $_GET['sortstr'];
		}else{
			$sortstr = 'auclosedate';
		}
		if (!empty($_GET['sortdir'])){
			$sortdir = $_GET['sortdir'];
		}else{
			$sortdir = 'DESC';
		}
		if ($sortdir=='ASC'){
			$newsortdir = 'DESC';
		}else{
			$newsortdir = 'ASC';
		}
		if (!empty($_GET['searchtxt'])){
			$searchtxt = $_GET['searchtxt'];
		}else{
			$searchtxt = '';
		}
		if (!empty($_GET['txttype'])){
			$txttype = $_GET['txttype'];
		}else{
			$txttype = '';
		}
		if (!empty($_GET['item'])){
			$item = $_GET['item'];
		}else{
			$item = '';
		}
		if (!empty($_GET['issearch'])){
			$issearch = $_GET['issearch'];
		}else{
			$issearch = '';
		}
		if (!empty($_GET['specific'])){
			$specific = $_GET['specific'];
		}else{
			$specific = '';
		}
		if (!empty($_GET['type'])){
			$type = $_GET['type'];
		}else{
			$type = '';
		}

	}
	$statquery = "";
	$tablequery = "";
	$query = "";
	if(!empty($_GET['searchtxt'])){
		$searchstr = '';
		$searchstr = $_GET['searchtxt'];
		$searchstr = str_replace("'","",$searchstr);
		$searchstr = str_replace('"','',$searchstr);
		$searchstr = trim($searchstr);
		if (strlen($searchstr) == 0){
			$query = "SELECT *
				FROM compauction
				WHERE 0=1";
			$statquery = "SELECT *
				FROM compauction
				WHERE 0=1";
			$tablequery = "SELECT *
				FROM compauction
				WHERE 0=1";
		}else{
			if($_GET['type'] != ''){
				if($_GET['specific'] != ''){
					$wherestr = "WHERE auitem='" . $searchstr . "' AND autype='" . $_GET['type'] . "'";
				} else {
					$wherestr = "WHERE INSTR(auitem,'" . $searchstr . "')>0 AND autype='" . $_GET['type'] . "'";
				}
			}else{
				if($_GET['specific'] != ''){
					$wherestr = "WHERE auitem='" . $searchstr . "'";
				} else {
					$wherestr = "WHERE INSTR(auitem,'" . $searchstr . "')>0";
				}
			}
			$statquery = "SELECT CAST(avg(aubid) AS DECIMAL(5,2)) AS statprice, auclosedate AS statdate
							FROM compauction " . $wherestr . " GROUP BY auclosedate ORDER BY auclosedate ASC";
			$tablequery = "SELECT auitem, autype, CAST(auquant AS DECIMAL(5)) AS cauquant, aubuytype, CAST(aubid AS DECIMAL(5,2)) AS caubid, auclosedate, aulotid
							FROM compauction " . $wherestr . " ORDER BY " . $sortstr . " " . $sortdir;
		}
	}
	if($_GET['item'] != ''){
		if($_GET['type'] != ''){
			$wherestr = "WHERE auitem='" . $_GET['item'] . "' AND autype='" . $_GET['type'] . "'";
		}else{
			$wherestr = "WHERE auitem='" . $_GET['item'] . "'";
		}
		$statquery = "SELECT CAST(avg(aubid) AS DECIMAL(5,2)) AS statprice, auclosedate AS statdate
						FROM compauction " . $wherestr . " GROUP BY auclosedate ORDER BY auclosedate ASC";
		$tablequery = "SELECT auitem, autype, CAST(auquant AS DECIMAL(5)) AS cauquant, aubuytype, CAST(aubid AS DECIMAL(5,2)) AS caubid, auclosedate, aulotid
						FROM compauction " . $wherestr . " ORDER BY " . $sortstr . " " . $sortdir;
	}
	$rowcount = 0;
	$db = db_open();
	if ($tablequery != '') {
		$query = $tablequery;
	}else{
		$query = $statquery;
	}
	/*echo '$query=' . $query . '<br \>';
	echo '$statquery=' . $statquery . '<br \>';
	echo '$tablequery=' . $tablequery . '<br \>';*/
	if ($query != ""){
		foreach ($db->query($query) as $line) {
			$rowcount = $rowcount + 1;
		}
	}
	$db= null;
	if ($rowcount > 30){
		
	}
?>

<html>
	<head>
		<title>Cbid Completed Auctions</title>
		<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
		<link rel=stylesheet href=style.css type=text/css>
		<script src="jquery-1.7.min.js" type="text/javascript"></script>
		<script src="raphael.js" type="text/javascript"></script>
		<script src="elycharts.min.js" type="text/javascript"></script>
		<script src="jquery.tablesorter.js" type="text/javascript"></script>
		<script type="text/javascript">
			$(document).ready(function() 
				{ 
					$("#itemlist").tablesorter(); 
				} 
			);
			
			function average(vals) {
				if (vals.length == 0) return null;
				if (vals.length == 1) return vals[0];
				var total = 0;
				for (var i = 0; i < vals.length; i++) total += vals[i];
				return total/vals.length;
			}
			
			function stdDev(vals) {
				if (vals.length == 0) return null;
				if (vals.length == 1) return 0;
				avg = average(vals);
				squares = [];
				
				for (var i = 0; i < vals.length; i++) squares[i] = Math.pow(vals[i] - avg, 2);
				
				return Math.sqrt(average(squares));
			}
		<?php
		if ($statquery != ''){
		?>
			var dates = [
				<?php
					$db = db_open();
					foreach ($db->query($statquery) as $line) {
							echo '"' . $line["statdate"] . '",';
					}
					$db = null;
				?>
			];
			
			var prices = [
				<?php
					$db = db_open();
					foreach ($db->query($statquery) as $line) {
							echo $line["statprice"] . ',';
					}
					$db = null;
				?>
			];
			
			
			tooltips = [];
			
			for (var i = 0; i < prices.length; i++) tooltips[i] = dates[i] + '<br />' + formatMoney(prices[i]);
			
			MAX_CHART_SIZE = 30;
			
			if (prices.length > MAX_CHART_SIZE) {
				var topXprices = prices.slice(prices.length-50, prices.length);
				var topXtooltips = tooltips.slice(prices.length-50, prices.length);
				var topXdates = dates.slice(prices.length-50, prices.length);
			} else {
				var topXprices = prices;
				var topXtooltips = tooltips;
				var topXdates = dates;
			}
			
			$.elycharts.templates['line_basic_3'] = {
				type: "line",
				style: {
					"background-color": "black"
				},
				margins: [10, 10, 100, 30],
				defaultSeries: {
					rounded: false,
					plotProps: {
						"stroke-width": 2
						},
    				dot: true,
    				dotProps: {
      					stroke: "black",
      					"stroke-width": 2
    				},
    				tooltip: {
      					frameProps: {
        					opacity: 0.75
      					}
    				}
  				},
			  	series: {
			    	serie1: {
			      		color: "red"
			    	},
			    	serie2: {
			      		color: "blue"
			    	}
			  	},
			  	defaultAxis: {
			    	labels: true,
			    	labelsProps: {
			      		fill: "white"
			    	},
			    	labelsAnchor: "start",
			    	labelsMargin: 5
			  	},
			  	axis: {
			    	l: {
			      		titleProps: {
			        		fill: "white"
			      		},
			      		labels: false
			    	},
			    	x : {
				   		labelsRotate : 45,
				   		labelsProps : {
					    	font : "12px Verdana"
					   }
				  	}
			  	},
			  	features: {
			    	grid: {
			      		draw: [false, true],
			      		forceBorder: true,
			      		props: {
			        		stroke: "#A0A080"
			      		},
			      		extra: [0, 0, 10, 0]
			    	}
			  	}
			};

		<?php
		}
		?>
			
			function drawChart() {
				if (prices.length < 1) return;
				$("#chart").chart({
					template : "line_basic_3",
					tooltips : {
						serie1 : topXtooltips
					},
					values : {
						serie1 : topXprices,
					},
					labels : topXdates,
					defaultSeries : {
				 		fill : true,
				 		stacked : true
					},
					axis : {
						l : {
				<?php
					$ua=getBrowser();
					if (($ua['name'] == 'Google Chrome') or ($ua['name'] == 'Apple Safari')) {
						echo 'title : "Average Price"';
					} else {
						echo 'title : ""';
					}
				?>
						}
					}
				});
				$('#chart').removeClass('hidden');
			}
			
			function formatMoney(val) {
				return '$' + val.toFixed(2);
			}
			function sortNumber(a,b)
			{
				return a - b;
			}
			function populatePriceData()
			{
				if (prices.length < 1) return;
				var sorted = prices.slice(0).sort(sortNumber);
				//var avg = average(prices);
				var mid_price = sorted[Math.floor(prices.length/2)];
				var sd = stdDev(prices);
				var max_price = sorted[sorted.length-1];
				//var bad_price = avg+(2*sd);
				var bad_price = sorted[Math.floor(prices.length*5/6)];
				//var poor_price = avg+sd;
				var poor_price = sorted[Math.floor(prices.length*4/6)];
				//var good_price = avg-sd;
				var good_price = sorted[Math.floor(prices.length*2/6)];
				//var best_price = avg-(2*sd);
				var great_price = sorted[Math.floor(prices.length*1/6)];
				var min_price = sorted[0];
				if (!((bad_price < max_price) && (bad_price > mid_price)))$('.bp').hide();
				if (!((poor_price < bad_price) && (poor_price > mid_price))) $('.pp').hide();
				if (!((good_price > great_price) && (good_price < mid_price))) $('.gop').hide();
				if (!((great_price > min_price) && (great_price < mid_price))) $('.grp').hide();
				$('#worst_price').text(formatMoney(max_price));
				$('#bad_price').text('>= '+formatMoney(bad_price));
				$('#poor_price').text('>= '+formatMoney(poor_price));
				$('#average_price').text(formatMoney(mid_price));
				$('#good_price').text('<= '+formatMoney(good_price));
				$('#great_price').text('<= '+formatMoney(great_price));
				$('#best_price').text(formatMoney(min_price));
				$('#price_table').removeClass('hidden');
			}
			
			function resetform()
			{
				oFormObject = document.forms['searchfrm'];
				oFormObject.elements["searchtxt"].value = '';
				if (oFormObject.elements["type"].options[0].text = ' '){
					oFormObject.elements["type"].selectedIndex = 0;
				} else {
					oFormObject.elements["type"].selectedIndex = 1;
				}				
				if (oFormObject.elements[4].options[0].text = ' '){
					oFormObject.elements[4].selectedIndex = 0;
				} else {
					oFormObject.elements[4].selectedIndex = 1;
				}				
			}
		</script>
	</head>
	<body>
		<table width="100%">
		<tr>
			<td width="100px"> <a href="<?php echo htmlentities($_SERVER['PHP_SELF']); ?>"><img src="Cigar_small.png" border="0"></a> </td>
			<td> <h2><center>CigarBid Completed Auction Search</center></h2> </td>
			<td width="100px"> <a href="<?php echo htmlentities($_SERVER['PHP_SELF']); ?>"><img src="Cigar_small2.png" border="0"></a> </td>
		</tr>
		<tr></table>
		<center>

		<form action="<?php echo htmlentities($_SERVER['PHP_SELF']); ?>" method="GET" id="searchfrm">
			<fieldset>
				<ol>
					<li>
						<label for=searchtxt>Search for text</label>
						<input type="text" name="searchtxt" value="<?php
						if ($specific != 'true'){
						 	echo $searchtxt;
						 } 
						 ?>"><br />
						<table border=0><tr>
						<td><input type="radio" name="txttype" value="items" <?php
						if ($txttype != 'lots'){
						 	echo 'checked';
						 } 
						 ?>><label for=searchtxt>Search individual lots</label></td>
						<td><input type="radio" name="txttype" value="lots" <?php
						if ($txttype == 'lots'){
						 	echo 'checked';
						 } 
						 ?>><label for=searchtxt>Search lot titles</label></td>
						</tr></table>
					</li>
					<li>
						<label for=item>List item history</label>
						<select name="item">
							<?php
								if (($item != '') or ($specific != '')) {
									if ($specific != '') {					
										$listfirst = $searchtxt;
									} else {
										$listfirst = $item;
									}				
									$db = db_open();
									$query = "SELECT compitemname, compitemnum
													FROM compitemlist
													WHERE compitemname = '" . $listfirst . "'";
									foreach ($db->query($query) as $line) {
										?>
											<option value="<?= $line["compitemname"] ?>"><?= $line["compitemname"] ?> - [<?= $line["compitemnum"] ?> Auctions]</option>
										<?php
									}
									$db = null;	
								}
								?>
								<option value=""></option>
								<?php								
								
								$db = db_open();
								$query = 'SELECT compitemname, compitemnum
												FROM compitemlist
												ORDER BY compitemname';
								
								foreach ($db->query($query) as $line) {
									?>
										<option value="<?= $line["compitemname"] ?>"><?= $line["compitemname"] ?> - [<?= $line["compitemnum"] ?> Auctions]</option>
									<?php
								}
								$db = null;
							?>
						</select>
					</li>
					<li>
						<label for=item>Restrict search to</label>
						<select name="type">
						<?php
						if ($type != ''){ 
						?>
							<option value="<?= $type ?>"><?= $type ?></option>
						<?php
						}
						?>
							<option value=""></option>
							<?php
								$db = db_open();
								$query = 'SELECT compitem
												FROM compitemtype
												ORDER BY compitem';
								
								foreach ($db->query($query) as $line) {
									?>
										<option value="<?= $line["compitem"] ?>"><?= $line["compitem"] ?></option>
									<?php
								}
								$db = null;
							?>
						</select>
					</li>
					<input type="hidden" name="issearch" value="true" />
				</ol>
			</fieldset>
			<fieldset>
				<ol><li>
				<table>
				<tr><td><button type="submit">Search</button></td><td></td><td><button type="button" onClick="resetform();">Reset</button></td></tr>
				</table>
				</li></ol>
			</fieldset>
			
		</form>

		<br />
		<br />
		<?php
		if ($issearch != ''){
			?>
		<h5>Your search returned <?= $rowcount ?> results</h5>
		<?php
		}
		?>
		
		<?php
			if ($txttype == 'items') {
			?>
				<div id="chart" class="hidden" style="width: 90%; height: 300px;"></div>
				<script type="text/javascript">
					drawChart();
				<?php
					$ua=getBrowser();
					if (($ua['name'] == 'Google Chrome') or ($ua['name'] == 'Apple Safari')) {
						echo 'drawChart()';
					}
				?>
				</script>
				<br />
				<div id="price_table" class="hidden">
					<table align="center">
						<tr>
							<td align="center" colspan="5"><h2>Price Stats</h2></td>
						</tr>
						<tr class="price">
							<td>Worst Price</td>
							<td class="bp">Bad Price</td>
							<td class="pp">Poor Price</td>
							<td>Average</td>
							<td class="gop">Good Price</td>
							<td class="grp">Great Price</td>
							<td>Best Price</td>
						</tr>
						<tr class="price">
							<td><div id="worst_price"></div></td>
							<td class="bp"><div id="bad_price"></div></td>
							<td class="pp"><div id="poor_price"></div></td>
							<td><div id="average_price"></div></td>
							<td class="gop"><div id="good_price"></div></td>
							<td class="grp"><div id="great_price"></div></td>
							<td><div id="best_price"></div></td>
						</tr>
					</table>
				</div>
				<script type="text/javascript">
					populatePriceData();
				</script>
		<?php
			}
		?>
		<br />
		<?php
			$db = db_open();
			if(!empty($_GET['issearch'])){
				if ($_GET['txttype'] == 'items'){
					$getstr = '&sortdir=' . $newsortdir . '&searchtxt=' . urlencode($searchtxt) . '&txttype=' . $txttype . '&item=' . urlencode($item) . '&issearch=' . $issearch;
				
		?>
		<table width="100%" id="itemlist" class="tablesorter">
		<thead>
			<tr>
				<th>Item Name</th>
				<th>Auction Type</th>
				<th>Buy Type</th>
				<th>Winning Bid</th>
				<th>Close Date</th>
				<th>Lot#</th>

			</tr>
		</thead>
		<tbody>
			<?php
				if ($tablequery != ""){
					$db = db_open();
					foreach ($db->query($tablequery) as $line) {
						?>
						<tr>
							<td><?= $line["auitem"] ?></td>
							<td><?= $line["autype"] ?></td>
							<td><?= $line["aubuytype"] ?></td>
							<td><?= '$'.number_format($line["caubid"], 2) ?></td>
							<td><?= $line["auclosedate"] ?></td>
							<td><a href="http://www.cigarbid.com/Auction/Lot/<?= $line["aulotid"] ?>" target="_new"><?= $line["aulotid"] ?></a></td>
						</tr>
						<?php
					}
					$db = null;
				}
			?>
			</tbody>
		</table>
		<?php
			} else {
		?>
		<h3>Select lot title to list individual auctions</h3>
		<table width="100%" id="itemlist" class="tablesorter">
		<thead>
			<tr>
				<th>Lot Title</th>
				<th># of Auctions</th>
				<th>First Auction</th>
				<th>Last Auction</th>
				<th>Average Price</th>
				<th>Max Price</th>
				<th>Min Price</th>
				<th>CI Search</th>
			</tr>
		</thead>
		<tbody>
					<?php
						$db = db_open();
						if(!empty($_GET[searchtxt])){
							$searchstr = '';
							$searchstr = $_GET['searchtxt'];
							$searchstr = str_replace("'","",$searchstr);
							$searchstr = str_replace('"','',$searchstr);
							$searchstr = trim($searchstr);
							if (strlen($searchstr) == 0){
								$query = "SELECT *
												FROM compauction
												WHERE 0=1";
							}else{
								$query = "SELECT auitem, COUNT(auitem) AS cnt, min(auclosedate) as mindte, max(auclosedate) as maxdte, CAST(avg(aubid) as DECIMAL(5,2)) as avgbid, max(aubid) as maxbid, min(aubid) as minbid
												FROM compauction
												WHERE INSTR(auitem,'" . $searchstr . "')>0
												GROUP BY auitem";
							}
						}
						foreach ($db->query($query) as $line) {
							?>
								<tr>
								<td><a href="<?= htmlentities($_SERVER['PHP_SELF']) . '?searchtxt=' . urlencode($line["auitem"]) . '&specific=true&issearch=true&txttype=items' . '">' . $line["auitem"] ?></a></td>
								<td><?= $line["cnt"] ?></td>
								<td><?= $line["mindte"] ?></td>
								<td><?= $line["maxdte"] ?></td>
								<td><?= $line["avgbid"] ?></td>
								<td><?= $line["maxbid"] ?></td>
								<td><?= $line["minbid"] ?></td>
								<td><a href="http://www.cigarsinternational.com/search/search.asp?keyword=<?= urlencode($line["auitem"]) ?>" target="_new">Search CI</a></td>
								</tr>
							<?php
						}
						$db = null;
					?>
			</tbody>
		</table>
		<?php		
				}
			}
		?>
	</body>
</html>
