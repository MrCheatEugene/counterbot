<?php
// Добавьте в Cron
$directory= "/test/bot/" // ваша папка с ботом
$json = json_decode(file_get_contents($directory."usersDB.json"),true);
if(!is_null($json)){
	if(isset($json['null']) == true){
		unset($json['null']);
	}
	$keys=  array_keys($json);
	$foolOfDay = '@'.$keys[array_rand($keys)];
	$fPair= '@'.$keys[array_rand($keys)];
	$sPair= '@'.$keys[array_rand($keys)];
	$pairOfDay = $fPair.' {ANDSIGN} '.$sPair;
	$nicestOfDay = '@'.$keys[array_rand($keys)];
		while ($fPair == $sPair) {
			$fPair= '@'.$keys[array_rand($keys)];
			$sPair= '@'.$keys[array_rand($keys)];		
		}
	
		while ($sPair == '@null' or $fPair == '@null') {
			$fPair= '@'.$keys[array_rand($keys)];
			$sPair= '@'.$keys[array_rand($keys)];		
		}
	$pairOfDay = $fPair.' {ANDSIGN} '.$sPair;
	
	echo $pairOfDay;
	file_put_contents($directory."foolOfDay", $foolOfDay);
	file_put_contents($directory."pairOfDay", $pairOfDay);
	file_put_contents($directory."nicestOfDay", $nicestOfDay);
}
$newJson = $json;
foreach ($json as $key => $value) {
	if(is_array($value)){
		 $value[0] = 200;
		 $value[1] = 200;
		 $value[2] = 200;
	}
	$newJson[$key] = $value;
}
unlink($directory."usersDB.json");
file_put_contents($directory."usersDB.json",json_encode($newJson,JSON_UNESCAPED_UNICODE));
