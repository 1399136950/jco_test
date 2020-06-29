<?php
class ThreadForUpgrade extends Thread{
	
	private $upgrade_url = "/webs/updateCfg";
	
	private $upgrade_file_dir = '/upgrade_file';
	
	function __construct($url,$file_path,$root_path,$log_file){
		$this->url       = $url;
		$this->file_path = $file_path;
		$this->root_path = $root_path;
		$this->log_file  = $root_path.'/log/'.$log_file;
	}
	
	public function write_upgrade_log($msg){
		$fd=fopen($this->log_file,'a+');
		while(true){
			if(flock($fd,LOCK_EX|LOCK_NB)){//获取独占锁
				fwrite($fd,'['.date('Y-m-d H:i:s').']'.'[thread#'.$this->thread_num.']'.$msg.PHP_EOL);
				flock($fd,LOCK_UN);//解锁
				break;
			}
		}
		fclose($fd);
	}
	
	public function check_connect_port($ip,$port,$timeout=3){//检查端口是否可用
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
	
	
	public function get_version($IP){//获取设备的版本信息
		if($this->check_connect_port($IP,9999)){
			$socket=socket_create(AF_INET, SOCK_STREAM, SOL_TCP) or die("Could not create  socket\n");
			$version=0;
			if(@$connection= socket_connect($socket, $IP, 9999)){
				$this->write_upgrade_log("[get_version]connect port 9999 success");
				$cmd='device_info -act list';//NVR
				$len=strlen($cmd);
				socket_write($socket, $cmd, $len);
				$buffer=socket_read($socket, 65535);
				if($buffer=="[Error] Failure of authentication\r\n"){
					echo $buffer;
					$this->write_upgrade_log("[get_version][Error] Failure of authentication");
					exit(0);
				}else{
					$version=explode('=',explode(';',$buffer)[5])[1];
				}
			}
			socket_close($socket);
			return $version;
		}else{
			return false;
		}
	}
	
	public function upload_file($ip,$file_path){//上传升级包
		/*****************************分块上传***************************/
		/*$port=8006;
		if($this->get_version($ip)){
			$this->write_upgrade_log("[upload_file][$ip]IS ON-LINE!");
			$socket     = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
			$connection = socket_connect($socket, $ip, $port);
			$fd         = fopen($this->root_path.$this->upgrade_file_dir.'/'.$file_path,'r');
			$filesize   = filesize($this->root_path.$this->upgrade_file_dir.'/'.$file_path);
			$content    = fread($fd,$filesize);
			$data_size  = 1024*1024;
			$data_count = ceil($filesize/$data_size);
			if($connection){
				$this->write_upgrade_log("[upload_file][$ip]connect port 8006 success");
				$this->write_upgrade_log("[upload_file][$ip]start send file");
				for($i=0;$i<$data_count;$i++){
					$data=substr($content,$i*$data_size,$data_size);
					socket_write($socket,$data,$data_size);
				}
				$this->write_upgrade_log("[upload_file][$ip]send file finished");
			}
			socket_close($socket);
			fclose($fd);
		}else{
			echo "$ip IS NOT ONLINE!\r\n";
			$this->write_upgrade_log("[upload_file][$ip]IS NOT ONLINE!");		
		}*/
		/**************************一次上传******************************/
		$port=8006;
		if($this->get_version($ip)){
			$this->write_upgrade_log("[upload_file][$ip]IS ON-LINE!");
			$socket     = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
			$connection = socket_connect($socket, $ip, $port);
			$fd         = fopen($this->root_path.$this->upgrade_file_dir.'/'.$file_path,'r');
			$filesize   = filesize($this->root_path.$this->upgrade_file_dir.'/'.$file_path);
			$content    = fread($fd,$filesize);
			if($connection){
				$this->write_upgrade_log("[upload_file][$ip]connect port 8006 success");
				$this->write_upgrade_log("[upload_file][$ip]start send file");
					socket_write($socket,$content,$filesize);
				$this->write_upgrade_log("[upload_file][$ip]send file finished");
			}
			socket_close($socket);
			fclose($fd);
		}else{
			echo "$ip IS NOT ONLINE!\r\n";
			$this->write_upgrade_log("[upload_file][$ip]IS NOT ONLINE!");		
		}
	}	
	
	public function run(){
		$this->thread_num=$this->getCreatorId();
		$this->upload_file($this->url,$this->file_path);
	}
}	