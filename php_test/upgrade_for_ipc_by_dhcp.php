<?php
class UpgradeTest{
	
	private $upgrade_url = "/webs/updateCfg";   //升级包提交到IPC的URL
	
	public $upgrade_file_dir = 'upgrade_file/';//存放升级包文件夹
	
	private $root_path;                         //脚本根目录
	
	private $sleep_time = 80;                   //单个设备升级休息间隔时间
	
	private $sleep_time_nums;                   //多个设备升级,每一次升级等待的时间,根据采集数据自动获得
	
	private $test_nums = 2;                     //采集数据时每个包升级的次数
	
	private $test_sleep_time = 30;              //采集数据时的间隔时间
	
	private $wait_result_nums = 20;             //等待超时的次数，每次10秒
	
	private $time_array;                        //存放每个升级包的升级时间,多个IP升级时才会用到
		
	private $file_name = 'upgrade.log';         //日志文件称
	
	public  $log_file;                          //最终的日志文件名,加时间前缀
	
	public  $log_dir = '/log';                  //日志文件所在文件夹
	
	public  $upgrade_port = 8006;
	
	public function __construct(){//对象实例化时，自动识别升级包文件
        if(!file_exists($this->upgrade_file_dir)){
            echo "The upgrade package folder does not exist\r\n";
            exit(0);
        }
        $time = date('Ymd-H.i.s');
		$script_path     = __FILE__;//脚本绝对路径
		$script_name     = $_SERVER['SCRIPT_FILENAME'];//脚本名称
		$this->root_path = explode("$script_name",$script_path)[0];//脚本根目录
		if (!file_exists($this->root_path.$this->log_dir)){//不存在log文件夹就创建一个
            mkdir ($this->root_path.$this->log_dir);
        } 
		$this->log_file = "{$time}-{$this->file_name}";
		require_once('MyTelnet.class.php');
        require_once('Progessbar.class.php');
        
	}
    
    public function sendUdpCmd($ID,$cmd){//发送UDP命令
        $sock = socket_create( AF_INET, SOCK_DGRAM, SOL_UDP );
        socket_set_option($sock,SOL_SOCKET,SO_BROADCAST,1);
        socket_set_option($sock,SOL_SOCKET,SO_RCVTIMEO,array("sec"=> 1, "usec"=> 0 ) ); // 接收
        socket_set_option($sock,SOL_SOCKET,SO_SNDTIMEO,array("sec"=> 1, "usec"=> 0 ) ); // 发送 
        $CMD = "JCPMETHOD * HDS/1.0\r\nID=$ID#JcpCmd=$cmd#";
        if(socket_sendto($sock,$CMD,strlen($CMD),0,"255.255.255.255",8002)){
            @socket_recvfrom($sock,$buf,65535,0,$name,$port);
            socket_close($sock);
            if(strlen($buf)>0){
                return $buf;
            }else{
                return false;
            }
        }
    }
    
    public function get_ip_from_broadcast($id){
        $cmd='wifilist -act status';
        $res=$this->sendUdpCmd($id,$cmd);
        echo $res."\n";
        if ($res){
            $arr=explode(';',$res)[1];
            $ip=explode('=',$arr)[1];
            return $ip;
        }else{
            return false;
        }
    }
    
    public function get_version($IP){//获取设备的版本信息
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
		if($output){
			$version = explode('=',explode(';',$output)[4])[1];
			return $version;
			curl_close($ch);
		}else{
			curl_close($ch);
			return false;
		}
	}
    
    public function get_id($IP){//获取设备的ID
		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL,"http://".$IP."/?jcpcmd=prienv%20-act%20list");// 
		curl_setopt($ch, CURLOPT_RETURNTRANSFER,1);	//
		curl_setopt($ch, CURLOPT_HEADER,0);	//
		curl_setopt($ch, CURLOPT_TIMEOUT,3);//
		/*****************伪造cookie******************/
		$cookie="loginflag_192.168.120.227=1";
		curl_setopt($ch, CURLOPT_COOKIE , $cookie );
		/***********************************/
		$output = curl_exec($ch);//
		if($output){
            preg_match('/device_id=(.*?) /i', $output,$res);
			curl_close($ch);
            echo $res[1]."\n";
            return $res[1];
		}else{
			curl_close($ch);
			return false;
		}
	}
    
	public function get_upgrade_log($IP){//通过telnet获取升级日志
		if($this->check_connect_port($IP,9527)){
			$port=9527;
		}else{
			if($this->check_connect_port($IP,24)){
				$port=24;
			}else{
				$port=false;
			}
		}
		if($port){
            $cmd='cat /opt/log/upgrade.log';
			$file="log/".$IP.'_'.date('Ymd-H.i.s').'_upgrade.log';
			$telnet=new MyTelnet($IP,$port);
			$telnet->getlog($cmd,$file);
            $telnet->close();
			echo "GET UPGRADE LOG-------$file\r\n";
			$this->write_upgrade_log("[get_upgrade_log]GET UPGRADE LOG-------$file");	
		}else{
			echo "can't telnet $IP\r\n";
			$this->write_upgrade_log("[get_upgrade_log]can't telnet $IP");
		}
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
	
	public function get_update_progressbar($IP){//获取升级进度
		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL,"http://".$IP."/?jcpcmd=update%20-act%20list");// 
		curl_setopt($ch, CURLOPT_RETURNTRANSFER,1);	//
		curl_setopt($ch, CURLOPT_HEADER,0);	//
		curl_setopt($ch, CURLOPT_TIMEOUT,6);//
		/*****************伪造cookie******************/
		$cookie="loginflag_192.168.120.227=1";
		curl_setopt($ch, CURLOPT_COOKIE , $cookie );
		/***********************************/
		$output = curl_exec($ch);
		if($output){
            $update_progressbar = explode('=',explode(';',$output)[2])[1];
			$this->write_upgrade_log("[get_update_progressbar] $update_progressbar");
			curl_close($ch);
			return $update_progressbar;
		}else{
			curl_close($ch);
			return -1;
		}
	}
	
	public function is_update($IP){//升级状态,判断是否正确升级
		$res=$this->get_update_progressbar($IP);
        echo "\rprogressbar:{$res}%";
		if($res==100){
			echo ",OK,Please wait for the upgrade to complete\r\n";
			return true;
		}else if($res>=0 && $res<100){
			sleep(2);
			return $this->is_update($IP);
		}else{
			return false;
		}
	}
	
	public function get_version_by_socket($IP){//获取设备的版本信息
		$socket=socket_create(AF_INET, SOCK_STREAM, SOL_TCP) or die("Could not create  socket\n");
		$version=0;
		if(@$connection= socket_connect($socket, $IP, 9999)){
			$this->write_upgrade_log("[get_version]connect port 9999 success");
			$cmd='version -act list';//IPC
			$len=strlen($cmd);
			socket_write($socket, $cmd, $len);
			$buffer=socket_read($socket, 65535);
			if($buffer=="[Error] Failure of authentication\r\n"){
				echo $buffer;
				$this->write_upgrade_log("[get_version][Error] Failure of authentication");
				exit(0);
			}else{
				$version=explode('=',explode(';',$buffer)[4])[1];
			}
		}
		socket_close($socket);
		return $version;
	}
	
    public function getBlankStr($len){
        $str='';
        for($i=0;$i<$len;$i++){
            $str.=' ';
        }
        return $str;
    }
    
	public function start_upgrade_by_tgzs($IP,$FILE){//多个升级包，多个IP升级测试
		/*****************采集测试数据********************/
		echo "\r\n";
		echo "           ++++++++++++++++++++++++++++++++++\r\n";
		echo "           +   Begin collecting test data   +\r\n";
		echo "           ++++++++++++++++++++++++++++++++++\r\n";
		echo "\r\n";
		$this->write_upgrade_log("[start_upgrade_by_tgzs]Begin Collecting Test Data......");
		$version_array = $this->new_before_upgrade_test($IP,$FILE);
		echo "The collected data are as follows:\r\n";
		
        foreach($version_array as $key=>$value){
			$str_len[]=strlen($key);
		}
        $max_len=max($str_len);
        foreach($version_array as $key=>$value){
            $blank_str=$this->getBlankStr($max_len-strlen($key));
            echo $key.$blank_str.'  ==>  '.$value."\r\n";
		}
		
		echo "\r\n";
		echo "   +++++++++++++++++++++++++++++++++++++++++++++++++++\r\n";
		echo "   +  Data collection complete!Start Upgrading Now!  +\r\n";
		echo "   +++++++++++++++++++++++++++++++++++++++++++++++++++\r\n";
		echo "\r\n";
		
		$this->write_upgrade_log("[start_upgrade_by_tgzs]Data Collection Complete!Start Upgrading Now!");
		/*****************正式升级测试********************/
		//单个IP升级
		if(count($IP) == 1){
			$i = 1;
            
			while(true){
				$tttt = $i % count($FILE) - 1;
				if($tttt == -1){
					$tttt = count($FILE) - 1;
				}
				echo "NO.$i--".$FILE[$tttt]."\r\n";
                $IP=$this->get_ip_from_broadcast($this->id);
                echo "$IP\r\n";
				$this->write_upgrade_log("[start_upgrade_by_tgzs:79]NO.$i--".$FILE[$tttt]);
				$ret=$this->upload_file($IP,$FILE[$tttt]);
                if(!$ret){
                    echo "sleep 40\r\n";
                    sleep(40);
                    
                    $this->upload_file($IP,$FILE[$tttt]);
                }
				$this->write_upgrade_log('[start_upgrade_by_tgzs:81]Upload Finshed,Sleep('.$this->sleep_time.')');
				if($this->is_update($IP)){
                    sleep($this->sleep_time);
                }else{
                    echo ",err\r\n";
                    exit(0);
                }
                #$IP=$this->get_ip_from_broadcast($this->id);
				$status = $this->Continuous_send_request($this->wait_result_nums,$IP);//连续发送多次请求的结果，返回数组
				if($status){//有结果
					if($status['version'] == $version_array[$FILE[$tttt]]){
						$upgrade_time = $this->sleep_time + $status['require_nums'] * 10;
						echo "Upgrade Success!It takes $upgrade_time Seconds!\r\n";
						echo "The Version Is $status[version]\r\n\r\n";
						$this->write_upgrade_log("[start_upgrade_by_tgzs]Upgrade Success!It Takes $upgrade_time Seconds!");
						$this->write_upgrade_log("[start_upgrade_by_tgzs]The Version Is $status[version]");
					}else{//结果与预期不一致，说明升级超时
						$this->write_upgrade_log('[start_upgrade_by_tgzs]Inconsistent with the expected version!');
						echo "Inconsistent with the expected version!\r\n";
						$this->write_upgrade_log('[start_upgrade_by_tgzs]sleep(180)');
						sleep(180);
						$status_2 = $this->get_version($IP);
						if($status_2){
							if($status_2 == $version_array[$FILE[$tttt]]){
								$this->write_upgrade_log("[start_upgrade_by_tgzs]Upgrade Success!");
								$this->write_upgrade_log("[start_upgrade_by_tgzs]The Version Is $status_2");
								echo "Upgrade Success!\r\n";
								echo "The Version Is $status_2\r\n\r\n";	
							}else{
								echo "Upgrade Error!\r\n";
								$this->write_upgrade_log("[start_upgrade_by_tgzs]Upgrade Error!");
								echo "The Version Is $status_2\r\n\r\n";
								$this->write_upgrade_log("[start_upgrade_by_tgzs]The Version Is $status_2");
								$this->get_upgrade_log($IP);
								$this->write_upgrade_log("[start_upgrade_by_tgzs]EXIT");
								exit;			
							}	
						}else{
							echo "Can't Get Upgrade Result!\r\n\r\n";
							$this->write_upgrade_log("[start_upgrade_by_tgzs]Can't Get Upgrade Result!");
							$this->write_upgrade_log("[start_upgrade_by_tgzs]EXIT");
							exit;		
						}
					}
				}else{//没有结果，说明设备还没有起来
					$this->write_upgrade_log("[start_upgrade_by_tgzs]Upgrade Time Out!Relaunch A Request Now!");
					$timeout_status = $this->Continuous_send_request(5,$IP);
					if($timeout_status){
						if($timeout_status['version'] == $version_array[$FILE[$tttt]]){
							$upgrade_time = $this->sleep_time + $this->wait_result_nums * 10 + $this->sleep_time + $timeout_status['require_nums'] * 10;
							echo "Upgrade Success!It Takes $upgrade_time Seconds!\r\n";
							echo "The Version Is $timeout_status[version]\r\n\r\n";
							$this->write_upgrade_log("[start_upgrade_by_tgzs]Upgrade Success!It Takes $upgrade_time Seconds!");
							$this->write_upgrade_log("[start_upgrade_by_tgzs]The Version Is $timeout_status[version]");
						}else{
							echo "Version Is Error!\r\n\r\n";
							$this->get_upgrade_log($IP);//获取升级日志文件
							$this->write_upgrade_log("[start_upgrade_by_tgzs]Version Is Error!");
							exit;
						}
					}else{
						echo "Upgrade Time Out!\r\n\r\n";
						$this->write_upgrade_log("[start_upgrade_by_tgzs]Upgrade Time Out!");
						exit;
					}
				}
				$i++;
				$this->write_upgrade_log('[start_upgrade_by_tgzs]sleep(30)');
				sleep(30);
			}
		//多个IP升级
		}else{
			exit(0);
		}
	}
	
	public function Continuous_send_request($require_nums,$ip){
		$status = false;
		$result = array();
		for($i = 0;$i <= $require_nums;$i++){
            $ip=$this->get_ip_from_broadcast($this->id);
            if ($ip){
                $version = $this->get_version($ip);	
                if($version){
                    $status = true;
                    break;
                }else{
                    $this->write_upgrade_log('[Continuous_send_request]No Answer,Sleep(10)');
                    sleep(10);
                }
            }else{
                sleep(10);
            }
		}
		if($status){
			$result['version']      = $version;
			$result['require_nums'] = $i;
			return $result;
		}else{
			return false;	
		}	
	}
	
	public function new_before_upgrade_test($ip,$file){//此处的ip,file为数组	
        if(is_array($ip)){
			$ip = $ip[0];
		}
        $this->id=$this->get_id($ip);
		$version_array = array();
		$time_array=array();//记录每次升级时间
        $test_index=1;
		for($file_num = 0; $file_num < count($file);$file_num++){
			$version = array();
			for($i=1;$i<=$this->test_nums;$i++){
                echo "NO.{$test_index}\r\n";
                $test_index++;
				$this->write_upgrade_log('[new_before_upgrade_test]Upload File Now');
				$this->write_upgrade_log("[new_before_upgrade_test]NO.$i,FILE IS $file[$file_num]");
				$ret=$this->upload_file($ip,$file[$file_num]);
                if(!$ret){
                    echo "sleep 40\r\n";
                    sleep(40);
                    $this->upload_file($ip,$file[$file_num]);
                }
				$start_time=microtime(true);
				/**************判断是否正确升级****************/
				//echo "progressbar:";
				if($this->is_update($ip)===false){
					echo ",update error\r\n";
					$this->write_upgrade_log('[new_before_upgrade_test]progressbar error');
					exit(0);
				}
				/*******************************************/
				$this->write_upgrade_log('[new_before_upgrade_test]Upload Finished,Sleep('.$this->sleep_time.')');
				sleep($this->sleep_time);
				$k = $i - 1;
				for($require_nums = 0;$require_nums <= $this->wait_result_nums;$require_nums++){
					$ip=$this->get_ip_from_broadcast($this->id);
                    if($ip && $this->get_version($ip)){
                        echo "$ip\r\n";
						$version[$k] = $this->get_version($ip);
						$this->write_upgrade_log("[new_before_upgrade_test]Result Is $version[$k]");
						$end_time=microtime(true);
						$time=ceil($end_time-$start_time);
						$time_array[$file[$file_num]][]=$time;
						echo "Get Test Data......It takes $time secends\r\n\r\n";
						$this->write_upgrade_log("[new_before_upgrade_test]Get Test Data......It takes $time secends");
						$this->write_upgrade_log('[new_before_upgrade_test]Sleep('.$this->test_sleep_time.')');
						sleep($this->test_sleep_time);
						break;
					}else{
						$version[$k] = false;
						$this->write_upgrade_log('[new_before_upgrade_test]No Answer,Sleep(10)');
						sleep(10);
					}	
				}
				if(!$version[$k]){//请求无结果
					echo "Upgrade Time Out!Relaunch A Request Now!\r\n\r\n";
					$this->write_upgrade_log("[new_before_upgrade_test]Upgrade Time Out!Relaunch A Request Now!");
					$timeout_result_array = $this->Continuous_send_request(10,$ip);
					if($timeout_result_array){
						$time_out    = $this->sleep_time + 10 * $this->wait_result_nums + 10 * $timeout_result_array['require_nums'];
						$version[$k] = $timeout_result_array['version'];
						echo "Get Test Data......It takes $time_out secends\r\n\r\n";
						$this->write_upgrade_log("[new_before_upgrade_test]Get Test Data......It takes $time_out secends");
						$this->write_upgrade_log('[new_before_upgrade_test]Sleep('.$this->test_sleep_time.')');
						sleep($this->test_sleep_time);
					}else{
						$this->write_upgrade_log('[new_before_upgrade_test]Upgrade Error! Inconsistent results!');
						echo "Upgrade Error! Inconsistent results!\r\n\r\n";
						exit;
					}
				}
			}	
			$this->time_array[$file[$file_num]]=ceil(max($time_array[$file[$file_num]])*1.2);//找出最长升级时间
			if($version[0] == $version[1]){
				$version_array[$file[$file_num]] = $version[0];
			}else{
				$this->write_upgrade_log('[new_before_upgrade_test]Upgrade Result Error!Please Check Device!');
				echo "Upgrade Result Error!Please Check Device!";
				exit;
			}
		}
		$this->write_upgrade_log("[new_before_upgrade_test]Corresponding Software Version Is:");
		foreach($version_array as $k => $v){
			$this->write_upgrade_log("[new_before_upgrade_test]$k--$v");	
		}
		return 	$version_array;
	}
	
	public function upload_file_by_curl($url,$file_path){//上传升级包
		$ip = explode('//', explode($this->upgrade_url,$url)[0])[1];
		if($this->get_version($ip)){
			$this->write_upgrade_log("[upload_file][$ip]IS ON-LINE!");
			$curl = curl_init();
			if (class_exists('\CURLFile')) {//
				curl_setopt($curl, CURLOPT_SAFE_UPLOAD, true);
				$data = array('filepath' => new \CURLFile(realpath($this->root_path.$this->upgrade_file_dir.'\\'.$file_path)));//>=5.5
			} else {
				if (defined('CURLOPT_SAFE_UPLOAD')) {
					curl_setopt($curl, CURLOPT_SAFE_UPLOAD, false);
				}
				$data = array('file' => '@' . realpath($this->root_path.$this->upgrade_file_dir.'\\'.$file_path));//<=5.5
			}
			curl_setopt($curl, CURLOPT_URL, $url);
			curl_setopt($curl, CURLOPT_POST, 1 );
			curl_setopt($curl, CURLOPT_POSTFIELDS, $data);
			curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
			curl_setopt($curl, CURLOPT_TIMEOUT,40); 
			
			/*****************伪造cookie******************/
			$cookie="loginflag_192.168.120.227=1";
			curl_setopt($curl, CURLOPT_COOKIE , $cookie );
			/*********************************************/
			
			$this->write_upgrade_log("[upload_file][$url]Start Send Curl!");	
			$result = curl_exec($curl);
			$error  = curl_error($curl);
			$this->write_upgrade_log("[upload_file][$url]Close Curl!");	
			curl_close($curl);
		}else{
			echo "$ip IS NOT ONLINE!\r\n";
			$this->write_upgrade_log("[upload_file][$ip]IS NOT ONLINE!");		
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
				$this->write_upgrade_log("[upload_file][$ip]send file now");
				socket_write($socket,$content,$filesize);
				$this->write_upgrade_log("[upload_file][$ip]send file finished");
			}
			socket_close($socket);
			fclose($fd);
            return true;
		}else{
			echo "$ip IS NOT ONLINE!\r\n";
			$this->write_upgrade_log("[upload_file][$ip]IS NOT ONLINE!");
            return false;
		}
	}
	
	public function get_upload_file(){//返回根目录升级包信息
		$handler = opendir($this->root_path.$this->upgrade_file_dir);
		$tgz=array();
		while(($filename = readdir($handler)) !== false){
			if($filename != '.' && $filename != '..' && preg_match('/\.'."tgz".'$/', $filename)){
				$tgz[] = $filename;
			}
		}
		closedir($handler);
		if(count($tgz) < 2){
			return false;
		}else{
			foreach($tgz as $k => $v){
				$this->write_upgrade_log("[get_upload_file]Upgrade Pack Is--$v");	
			}
			return $tgz;
		}
	}
	
	public function get_ip_array($ip,$nums){//获取IP队列
		$last_num = explode('.',$ip)[3];
		$first_num = explode('.',$ip)[0].'.'.explode('.',$ip)[1].'.'.explode('.',$ip)[2].'.';
		$ip_array=array();
		for($i=0;$i<$nums;$i++){
			$new_last_num = $last_num + $i;
			$ip_array[] = $first_num.$new_last_num;
		}
		return $ip_array;
	}
	
	public function check_ip_address($ip){
		$rule = '/^((([1-9])|((0[1-9])|([1-9][0-9]))|((00[1-9])|(0[1-9][0-9])|((1[0-9]{2})|(2[0-4][0-9])|(25[0-5]))))\.)((([0-9]{1,2})|(([0-1][0-9]{2})|(2[0-4][0-9])|(25[0-5])))\.){2}(([1-9])|((0[1-9])|([1-9][0-9]))|(00[1-9])|(0[1-9][0-9])|((1[0-9]{2})|(2[0-4][0-9])|(25[0-5])))$/';  
        preg_match($rule,$ip,$result);  
        return $result;  
	}
	
	public function before_execute_script($tgz_pack_array,$sleep_time){//执行脚本前的倒计时
		echo "\r\nUpgrade pack is:\r\n\r\n";
		foreach($tgz_pack_array as $value){
			echo "$value\r\n";
		}
		
		$this->write_upgrade_log("[before_execute_script]Execute Script After $sleep_time seconds!");
		$this->write_upgrade_log('[before_execute_script]Sleep('.$sleep_time.')');
		for($i=$sleep_time;$i>=1;$i--){
            if($i<10){
                $tmp='0'.$i;
            }else{
                $tmp=$i;
            }
			echo "\rExecute Script After $tmp seconds";
			sleep(1);
		}
		$this->write_upgrade_log('[before_execute_script]Start!');
		echo "\r                               ";
	}
	
	public function write_upgrade_log($msg){//记录日志
		file_put_contents($this->root_path.$this->log_dir.'/'.$this->log_file,'['.date('Y-m-d H:i:s').']'.$msg.PHP_EOL, FILE_APPEND);	
	}
    
    public function showProgess($nums){
        for($i=1;$i<=$nums;$i++){
            $progess=($i/$nums)*100;
            $progess=sprintf("%.2f",$progess);//保留两位小数
            $this->p->showProgessBar($progess);
            sleep(1);
        }
        echo "\r\n";
    }
}

/************************************************************/
$opt=getopt('i:n:d:');	
if(!empty($opt['i'])){
	$tt =  new UpgradeTest();
    if(!empty($opt['d'])){
        $tt->upgrade_file_dir = $opt['d'].'/';
    }
	if($tt -> check_ip_address($opt['i'])){//确定IP地址输入正确
		$file_array = $tt -> get_upload_file();
		if($file_array){//升级包数量大于2
			if(!empty($opt['n']) && $opt['n'] > 1){//测试的IP为多个
				if($opt['n'] > 20){
					echo "The -n are too large,it should be less than 20\r\n";
					return false;
				}
				$ip_array = $tt->get_ip_array($opt['i'],$opt['n']);
				$not_online_dev_nums = 0;
				echo "\r\n";
				for($l = 0;$l < count($ip_array);$l++){//判断是否都在线
					if(!$tt -> get_version($ip_array[$l])){
						$not_online_dev_nums++;
						echo "$ip_array[$l] --- not online!\r\n";
					}else{
						echo "$ip_array[$l] --- online!\r\n";
					}
				}
				if($not_online_dev_nums !== 0){//有不在线的设备
					echo "Please Check Device!\r\n";
				}else{
					$tt->write_upgrade_log('[main]Sleep(3)');	
					sleep(3);
					$tt -> before_execute_script($file_array,10);
					$tt -> start_upgrade_by_tgzs($ip_array,$file_array);
				}	
			}else{//测试的IP为单个
				if($tt -> get_version($opt['i'])){//确定在线
                
					$tt -> before_execute_script($file_array,10);
					$tt -> start_upgrade_by_tgzs($opt['i'],$file_array);
				}else{
					echo "\r\nDevice is not on-line!\r\n";
					echo "Please check Device!\r\n";
				}
			}
		}else{//升级包数量不为2
			echo "The minimum number of upgrade packages is 2,Please check!\r\n";
		}
	}else{//IP格式错误
		echo "The IP format is incorrect,Please enter the correct IP address!\r\n";
	}
}else{
	echo "Input Error!\r\n";
	echo "Usage:\r\n";
	echo "    php upgrade_for_ipc.php -i [-n] [-d]\r\n";
	echo "    [-i] Device IP address;\r\n";
	echo "    [-n] The number of devices that need to be upgraded;Default one for empty;\r\n";
    echo "    [-d] Specify the upgrade package folder;Default folder is `upgrade_file`;\r\n";
}