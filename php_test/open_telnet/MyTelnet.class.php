<?php
class MyTelnet{
	function __construct($ip,$port){
		$this->socket       = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
		$this->connection   = socket_connect($this->socket, $ip, $port) or die("Could not connect  host\n");
		$this->device_type = $this->get_device_type($ip);//返回设备类型,根据类型设定不同的密码
		$this->wait_for_info();
		$res=$this->input_username();
        if(explode("\r\n",$res)[1]=='Password: '){
            $this->input_password();
        }
	}
	
	public function get_device_type($IP){
		/*********返回设备类型*********/
		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL,"http://".$IP."/?jcpcmd=version%20-act%20list");// 
		curl_setopt($ch, CURLOPT_RETURNTRANSFER,1);	//
		curl_setopt($ch, CURLOPT_HEADER,0);	//
		curl_setopt($ch, CURLOPT_TIMEOUT,1);//
		/*****************伪造cookie******************/
		$cookie="loginflag_192.168.120.227=1";
		curl_setopt($ch, CURLOPT_COOKIE , $cookie );
		/***********************************/
		$output = curl_exec($ch);//
		if($output){
			$device_type = explode('=',explode(';',$output)[0])[2];
			return $device_type;
			curl_close($ch);
		}else{
			curl_close($ch);
			return false;
		}
	}
	
	public function input_username(){
		return $this->write("root");
	}
	
	public function input_password(){
		switch($this->device_type){
			case 'mstar':
				$this->write("jco16888");
				break;
			case 'sstar':
				$this->write("jco16888");
				break;
			case 'ingenic':
				$this->write("jco666888");
				break;
			case 'grain':
				$this->write("jabsco668");
				break;
			default:
				echo "unknow device_type";
				exit(0);
		}
	}
	
	public function char_set($str){
		return str_replace(chr(255),chr(255).chr(255),$str);
	}
	
	public function write($msg){
		$msg = str_replace(chr(255),chr(255).chr(255),$msg);
        $msg = $msg."\r\n";
		socket_write($this->socket,$msg,strlen($msg));
        return $this->wait_for_info();
	}
	
	public function getstr(){
		return socket_read($this->socket,65535);
	}
	
	public function close(){
        if($this->socket){ 
            socket_close($this->socket);
            $this->socket=false;
        }else{
            echo "socket is closed\r\n";
        }
	}
	
	public function getlog($cmd,$file){
		$res=$this->write("$cmd");
		file_put_contents($file,$res,FILE_APPEND);
		//$this->close();
	}
	
	function wait_for_info(){
		$buf = '';
		$IAC     = chr(255);//选项协商的第一个字节
		$DONT    = chr(254);//拒绝选项请求
		$DO      = chr(253);//认可选项请求
		$WONT    = chr(252);//拒绝启动选项
		$WILL    = chr(251);//同意启动enable
		$theNULL = chr(0);
		while(1){
			$c = $this->getstr();
			if($c === false){
				return $buf;
			}
			if($c == $theNULL){
				return $buf;
			}
			if($c == "1"){
				continue;
			}
			if($c != $IAC){
				$buf .= $c;
				if(substr($buf,-2) == ': '|substr($buf,-2) == '# '){
					return $buf;
				}else{
					continue;
				}
			}
			$c = $this->getstr();
			if ($c == $IAC) {
				$buf .= $c;
			}else if (($c == $DO) || ($c == $DONT)) {
				$opt = $this->getstr();
				$this->write($IAC.$WONT.$opt);
			}elseif (($c == $WILL) || ($c == $WONT)) {
				$opt = $this->getstr();
				$this->write($socket,$IAC.$DONT.$opt);
			}else {
				echo '';
			}
		}
	}
}

