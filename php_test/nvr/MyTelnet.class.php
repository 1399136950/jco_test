<?php
class MyTelnet{
	function __construct($ip,$port){
		$this->socket       = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
		$this->connection   = socket_connect($this->socket, $ip, $port) or die("Could not connect  host\n");
		$this->wait_for_info();
		$this->input_username();
		$this->input_password();
	}
	
	public function input_username(){
		$this->write("root\r\n");
	}
	
	public function input_password(){
		
		$this->write("jco168168\r\n");

	}
	
	public function char_set($str){
		return str_replace(chr(255),chr(255).chr(255),$str);
	}
	
	public function write($msg){
		$msg = str_replace(chr(255),chr(255).chr(255),$msg);
		socket_write($this->socket,$msg,strlen($msg));
		return $this->wait_for_info();
	}
	
	public function getstr(){
		return socket_read($this->socket,65535);
	}
	
	public function close(){
		socket_close($this->socket);
	}
	
	public function getlog($cmd,$file){
		$res=$this->write("$cmd\r\n");
		file_put_contents($file,$res);
		$this->close();
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
			
			}
		}
	}
}

