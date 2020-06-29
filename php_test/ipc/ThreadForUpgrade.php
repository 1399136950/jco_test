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
	
	public function get_version($IP){//获取设备的版本信息
		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL,"http://".$IP."/?jcpcmd=version%20-act%20list");// 
		curl_setopt($ch, CURLOPT_RETURNTRANSFER,1);	//
		curl_setopt($ch, CURLOPT_HEADER,0);	//
		curl_setopt($ch, CURLOPT_TIMEOUT,1);//
		/*****************伪造cookie******************/
		$cookie="languages=0; stream=stream1; webport=80; ftport=21; has_dome=0; has_ptz_ctrl=0; has_3d=0; has_MCUupgrade=0; has_alarmin=0; has_alarmout=0; has_audio=1; graintype=0; shelter=0; master_stream=5; master_enb=1; slave_stream=7; slave_enb=1; playsize_width=1920; playsize_height=1080; rtspport=554; url=192.168.120.227; ocxversion=6.0.0.4; dome_modle=WLX-IPCAM; curr_menu_id=-1; platform=danale%2Cguobiao; maxheight=1080; user=test; passwd=test; main_stream=stream1; playMode=2; ljtypes=1; loginflag_192.168.120.227=1";
		curl_setopt($ch, CURLOPT_COOKIE , $cookie );
		/***********************************/
		$output = curl_exec($ch);//
		if($output){
			$version = explode('=',explode(';',$output)[4])[1];
			return $version;
			curl_close($ch);
		}else{
			curl_close($ch);
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