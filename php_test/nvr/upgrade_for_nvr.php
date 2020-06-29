<?php
function myerr($errno,$errstr,$errfile,$errline){
        throw new Exception("$errstr",1);
}

class upgradeTest{
	
	private $upgrade_file_dir = 'upgrade_file/';//存放升级包文件夹
	
	private $root_path;                         //脚本根目录
	
	private $sleep_time = 120;                   //单个设备升级休息间隔时间
	
	private $sleep_time_nums;                   //多个设备升级,每一次升级等待的时间,根据采集数据自动获得
	
	private $test_nums = 2;                     //采集数据时每个包升级的次数
	
	private $test_sleep_time = 30;              //采集数据时的间隔时间
	
	private $wait_result_nums = 20;             //等待超时的次数，每次10秒
	
	private $time_array;                        //存放每个升级包的升级时间,多个IP升级时才会用到
		
	private $file_name = 'upgrade.log';         //日志文件称
	
	public  $log_file;                          //最终的日志文件名,加时间前缀
	
	public  $log_dir = '/log';                  //日志文件所在文件夹
	
	public  $telnetport = 9527;                 //设备的telnet端口,升级失败时获取升级日志用到
	
	public function __construct(){//对象实例化时，自动识别升级包文件
		$time = date('Ymd-H.i.s');
		$script_path     = __FILE__;//脚本绝对路径
		$script_name     = $_SERVER['SCRIPT_FILENAME'];//脚本名称
		$this->root_path = explode("$script_name",$script_path)[0];//脚本根目录
		if (!file_exists($this->root_path.$this->log_dir)){//不存在log文件夹就创建一个
            mkdir ($this->root_path.$this->log_dir);
        } 
		$this->log_file = "{$time}-{$this->file_name}";
		//require_once('MyTelnet.class.php');
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
	
	
	public function get_update_progressbar($IP){//获取设备的版本信息
		set_error_handler("myerr");
        if($this->check_connect_port($IP,9999)){
			$socket=socket_create(AF_INET, SOCK_STREAM, SOL_TCP) or die("Could not create  socket\n");
			$progressbar=0;
			if(@$connection= socket_connect($socket, $IP, 9999)){
				
				$cmd='update -act list';//NVR
				$len=strlen($cmd);
				socket_write($socket, $cmd, $len);
                $flag=true;
                try{
                    $buffer=socket_read($socket, 65535);
                }catch(Exception $e){
                    echo ",socket_read catch error";
                    $flag=false;
                }
                if($flag){
                    if($buffer=="[Error] Failure of authentication\r\n"){
                        echo $buffer;
                        $this->write_upgrade_log("[get_version][Error] Failure of authentication");
                        exit(0);
                    }else{
                        if($buffer){
                            $progressbar=explode('=',explode(';',$buffer)[0])[1];
                            $this->write_upgrade_log("[get_version]connect port 9999 success;progressbar is $progressbar");
                        }
                    }
                }else{//socket_read()报错
                    $progressbar=false;
                }
			}
			socket_close($socket);
			return $progressbar;
		}else{
            $this->write_upgrade_log("[get_version]can't connect port 9999");
			return false;
		}
	}
	
	public function is_update($IP){//升级状态,判断是否正确升级
		$res=$this->get_update_progressbar($IP);
        if($res){
            echo "\rprogess bar:{$res}%";
            if($res==100){
                echo ",update success,wait for reboot \r\n";
            }else if($res>0 && $res<100){
                sleep(2);
                $this->is_update($IP);
            }else{
                echo ",progess error\r\n";
                exit(0);
            }
        }else{
			echo ",device is reboot now\r\n";
		}
	}
	
	
	public function start_upgrade_by_tgzs($IP,$FILE){//多个升级包，多个IP升级测试
		require_once('MyTelnet.class.php');
		/*****************采集测试数据********************/
		echo "\r\nBegin collecting test data......\r\n\r\n";
		$this->write_upgrade_log("[start_upgrade_by_tgzs]Begin Collecting Test Data......");
		$version_array = $this->new_before_upgrade_test($IP,$FILE);
		echo "The collected data are as follows:\r\n";
		foreach($version_array as $key=>$value){
			echo $key.'  ==>  '.$value."\r\n";
		}
		echo "\r\nData collection complete!Start Upgrading Now!\r\n\r\n";
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
				$this->write_upgrade_log("[start_upgrade_by_tgzs:79]NO.$i--".$FILE[$tttt]);
				$this->upload_file($IP,$FILE[$tttt]);
				$this->write_upgrade_log('[start_upgrade_by_tgzs:81]Upload Finshed,Sleep('.$this->sleep_time.')');
				sleep($this->sleep_time);
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
						$this->write_upgrade_log('[start_upgrade_by_tgzs]sleep(100)');
						sleep(100);
						$status_2 = $this->get_version($IP);
						if($status_2){
							if($status_2 == $version_array[$FILE[$tttt]]){
								$this->write_upgrade_log("[start_upgrade_by_tgzs]Upgrade Success!");
								$this->write_upgrade_log("[start_upgrade_by_tgzs]The Version Is $status_2");
								echo "Upgrade Success!\r\n";
								echo "The Version Is $status_2\r\n\r\n";	
							}else{
								/************************通过telnet获取升级日志***************************/
								if($this->check_connect_port($IP,$this->telnetport)){
									$telnet=new MyTelnet($IP,$this->telnetport);
									$res=$telnet->write("cat /opt/log/upgrade.log\r\n");
									$telnet->close();
									file_put_contents("log/".$IP.'_'.date('Ymd-H.i.s').'_upgrade.log',$res);
								}else{
									echo "can't telnet $IP $this->telnetport\r\n";
								}
								echo "Upgrade Error!\r\n";
								$this->write_upgrade_log("[start_upgrade_by_tgzs]Upgrade Error!");
								echo "The Version Is $status_2\r\n\r\n";
								$this->write_upgrade_log("[start_upgrade_by_tgzs]The Version Is $status_2");
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
							/************************通过telnet获取升级日志***************************/
							if($this->check_connect_port($IP,$this->telnetport)){
								$telnet=new MyTelnet($IP,$this->telnetport);
								$res=$telnet->write("cat /opt/log/upgrade.log\r\n");
								$telnet->close();
								file_put_contents("log/".$IP.'_'.date('Ymd-H.i.s').'_upgrade.log',$res);
							}else{
								echo "can't telnet $IP $this->telnetport\r\n";
							}
							echo "Version Is Error!\r\n\r\n";
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
			$j = 1;
			$fail_nums    = 0;//初始化总失败次数
			$success_nums = 0;//初始化总成功次数
			while(true){
				$count = $j * count($IP);//总升级次数
				$this_fial_nums    = 0;//初始化本次升级失败次数
				$this_success_nums = 0;//初始化本次升级成功次数
				/***********根据$j确定上传哪个升级包**********/
				$tttt = $j % count($FILE) - 1;
				if($tttt == -1){
					$tttt = count($FILE) - 1;
				}
				echo 'NO.'.$j."---$FILE[$tttt]\r\n";
				/******************根据不同升级包确定对应升级时间********************/
				$this->sleep_time_nums=$this->time_array[$FILE[$tttt]];
				/****************************************/
				$this->write_upgrade_log('[start_upgrade_by_tgzs]NO.'.$j."---$FILE[$tttt]");
				/****************************************/
				
				$is_loaded_pthread=extension_loaded('pthreads');
				if($is_loaded_pthread){
					require_once('ThreadForNvrUpload.class.php');//导入多线程类
					/****************************************/
					$t1 = microtime(true);
					echo "Start Threads For Upload File Now\r\n";
					/*************利用多线程来上传文件***********/
					$Thread=array();
					for($i = 0;$i < count($IP);$i++){
	
						$Thread[$i]=new ThreadForUpgrade($IP[$i],$FILE[$tttt],$this->root_path,$this->log_file);
						$Thread[$i]->start();	
					}
					/*************等待线程同步完成**************/
					for($i = 0;$i < count($IP);$i++){
						$Thread[$i]->join();
					}
					/****************************************/
					$t2 = microtime(true);
					echo "It's take ".round($t2-$t1,3)." secs\r\n";
					/****************************************/
				}else{
					echo "can't load extension pthread\r\n";
					$t1 = microtime(true);
					for($i = 0;$i < count($IP);$i++){
						$this->write_upgrade_log('[start_upgrade_by_tgzs]sleep(2)');
						sleep(2);//每次上传文件间隔2秒
						
						$this->upload_file($IP[$i],$FILE[$tttt]);	
					}
					$t2 = microtime(true);
					echo "It's take ".round($t2-$t1,3)." secs\r\n";
				}
				
				echo "sleep $this->sleep_time_nums secs\r\n";
				$this->write_upgrade_log('[start_upgrade_by_tgzs]sleep('.$this->sleep_time_nums.')');	
				sleep($this->sleep_time_nums);
				//$upgrade_result = array();
				/*************获取升级结果*************/
				for($l = 0;$l < count($IP);$l++){
					$upgrade_result = $this->get_version($IP[$l]);
					if(!$upgrade_result){
						$this->write_upgrade_log("[start_upgrade_by_tgzs]$IP[$l]---Not Online!");
						echo $IP[$l]."---Not Online!\r\n";
						$fail_nums++;
						$this_fial_nums++;
					}else{
						if($upgrade_result == $version_array[$FILE[$tttt]]){
							echo $IP[$l]."---Upgrade Success!;\r\n";
							$this->write_upgrade_log('[start_upgrade_by_tgzs]'.$IP[$l]."---Upgrade Success!---Version Is $upgrade_result");
							$success_nums++;
							$this_success_nums++;
						}else{
							echo $IP[$l]."---Upgrade Failed!---Version Is $upgrade_result;\r\n";
							$this->write_upgrade_log('[start_upgrade_by_tgzs]'.$IP[$l]."---Upgrade Failed!Version Is $upgrade_result;");
							$fail_nums++;
							$this_fial_nums++;	
						}
					}
				}
				if($this_fial_nums > 0){//说明本次升级有失败的
					$this_fial_nums_two = 0;
					$fail_nums    = $fail_nums - $this_fial_nums;//还原统计值
					$success_nums = $success_nums - $this_success_nums;//还原统计值
					echo "Upgrade Error!Retry Get Uprgade Info Now!\r\n\r\n";
					$this->write_upgrade_log('[start_upgrade_by_tgzs]Fail Nums > 0,Retry Get Uprgade Info!');
					$this->write_upgrade_log('[start_upgrade_by_tgzs]Sleep('.$this->sleep_time_nums.')');
					sleep($this->sleep_time_nums);//再等待一次时间
					$timeout_upgrade_result = array();
					for($m = 0;$m < count($IP);$m++){
						$timeout_upgrade_result[] = $this->get_version($IP[$m]);
					}
					print_r($timeout_upgrade_result);
					for($p = 0;$p < count($timeout_upgrade_result);$p++){
						if($timeout_upgrade_result[$p] == $version_array[$FILE[$tttt]]){
							echo $IP[$p]."---Upgrade Success!;\r\n";
							$this->write_upgrade_log('[start_upgrade_by_tgzs]'.$IP[$p]."---Upgrade Success!---Version Is $timeout_upgrade_result[$p]");
							$success_nums++;
						}else{
							/************************通过telnet获取升级日志***************************/
							if($this->check_connect_port($IP[$p],$this->telnetport)){
								$telnet=new MyTelnet($IP[$p],$this->telnetport);
								$res=$telnet->write("cat /opt/log/upgrade.log\r\n");
								$telnet->close();
								file_put_contents("log/".$IP[$p].'_'.date('Ymd-H.i.s').'_upgrade.log',$res);
							}else{
								echo "can't telnet $IP[$p] $this->telnetport\r\n";
							}
							echo $IP[$p]."---Upgrade Failed!;\r\n";
							$this->write_upgrade_log('[start_upgrade_by_tgzs]'.$IP[$p]."---Upgrade Failed!;");
							$fail_nums++;
							$this_fial_nums_two++;
						}
					}
					//注销此段代码表示升级出现异常继续运行
					/*if($this_fial_nums_two > 0){
						$this->write_upgrade_log('[start_upgrade_by_tgzs]Stop Running!Upgrade Failed!');
						echo "Stop Running!Upgrade Fail!\r\n";
						echo "Count:$count,Success:$success_nums,Fail:$fail_nums;\r\n\r\n";
						$this->write_upgrade_log("[start_upgrade_by_tgzs]Count:$count,Success:$success_nums,Fail:$fail_nums;");
						exit;
					}*/
				}
				echo "Count:$count,Success:$success_nums,Fail:$fail_nums;\r\n\r\n";
				$this->write_upgrade_log("[start_upgrade_by_tgzs]Count:$count,Success:$success_nums,Fail:$fail_nums;");
				$j++;
				$this->write_upgrade_log('[start_upgrade_by_tgzs]sleep(10)');
				sleep(10);//每升级完成一次，休息10秒；
			}	
		}
	}
	
	public function Continuous_send_request($require_nums,$ip){
		$status = false;
		$result = array();
		for($i = 0;$i <= $require_nums;$i++){
			$version = $this->get_version($ip);	
			if($version){
				$status = true;
				break;
			}else{
				$this->write_upgrade_log('[Continuous_send_request]No Answer,Sleep(10)');
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
		if(count($ip) > 1){
			$ip = $ip[0];
		}
		
		$version_array = array();
		$time_array=array();//记录每次升级时间
		for($file_num = 0; $file_num < count($file);$file_num++){
			$version = array();
			for($i=1;$i<=$this->test_nums;$i++){
				$this->write_upgrade_log('[new_before_upgrade_test]Upload File Now');
				$this->write_upgrade_log("[new_before_upgrade_test]NO.$i,FILE IS $file[$file_num]");
				$this->upload_file($ip,$file[$file_num]);
				$start=microtime(true);
				
				
				/*if($this->is_update($ip)){
					$end=microtime(true);
					$time1=ceil($end-$start);
				}else{
					echo "update error\r\n";
					exit(0);
				}*/
               
                $this->is_update($ip);
                $end=microtime(true);
				$time1=ceil($end-$start);
				
                $this->write_upgrade_log('[new_before_upgrade_test]Upload Finished,Sleep(40)');
				sleep(40);
				$k = $i - 1;
				for($require_nums = 0;$require_nums <= $this->wait_result_nums;$require_nums++){
					if($this->get_version($ip)){
						$version[$k] = $this->get_version($ip);
						echo $version[$k]."\r\n";
						$this->write_upgrade_log("[new_before_upgrade_test]Result Is $version[$k]");
						$time = $time1 + 40 + 10 * $require_nums;
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
	

	public function upload_file($ip, $file_path){//上传升级包
		/*****************************分块上传***************************/
		/*
        $port=8006;
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
		}
        */
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
		echo "\r\nExecute Script After $sleep_time seconds!\r\n\r\n";
		$this->write_upgrade_log("[before_execute_script]Execute Script After $sleep_time seconds!");
		$this->write_upgrade_log('[before_execute_script]Sleep('.$sleep_time.')');
		for($i=$sleep_time;$i>=1;$i--){
			echo "$i ";
			sleep(1);
		}
		$this->write_upgrade_log('[before_execute_script]Start!');
		echo "Start!\r\n\r\n";
	}
	
	public function write_upgrade_log($msg){//记录日志
		file_put_contents($this->root_path.$this->log_dir.'\\'.$this->log_file,'['.date('Y-m-d H:i:s').']'.$msg.PHP_EOL, FILE_APPEND);	
	}
}

/************************************************************/
$opt=getopt('i:n:');	
if(!empty($opt['i'])){
	$tt =  new upgradeTest();
	if($tt -> check_ip_address($opt['i'])){//确定IP地址输入正确
		$file_array = $tt -> get_upload_file();
		if($file_array){//升级包数量大于2
			if(!empty($opt['n']) && $opt['n'] > 1){//测试的IP为多个
				if($opt['n'] > 10){
					echo "The -n are too large,it should be less than 10\r\n";
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
					echo "Please check Device!\r\n";
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
	echo "\r\nInput Error!\r\n";
	echo "\r\nUsage:\r\n";
	echo "    php upgrade_for_nvr.php -i [-n]\r\n";
	echo "    [-i] NVR IP address\r\n";
	echo "    [-n] The number of devices that need to be upgraded;Default one for empty\r\n";
}