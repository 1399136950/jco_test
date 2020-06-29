<?php
function check_connect_port($ip,$port,$timeout=3){//检查端口是否可用
    $state=false;
    for($i=0;$i<$timeout;$i++){
        $socket=socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
        socket_set_nonblock($socket);
        socket_connect($socket,$ip,$port);
        $read=array();
        $write=array($socket);
        $exp=NULL;
        if(socket_select($read,$write,$exp,1)){
            socket_close($socket);
            $state=true;
            break;
        }
        socket_close($socket);
    }
    return $state;
}



require_once('MyTelnet.class.php');
$pars=getopt('i:');
if(!empty($pars['i'])){
    $ip=$pars['i'];
    if (check_connect_port($ip,24)){
        $port=24;
    }else{
        if (check_connect_port($ip,9527)){
            $port=9527;
        }else{
            $port=false;
        }
    }
    if($port){
        $tel=new MyTelnet($ip,$port);
        $res=$tel->write('rm /opt/conf/cus*');
        echo $res;
        $res1=$tel->write('ls /opt/conf/');
        echo $res1;
        $tel->close();
    }else{
        echo "can't telnet device\r\n";
    }
}