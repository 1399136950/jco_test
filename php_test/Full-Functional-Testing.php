<?php
class Test{
	private $log_file;
	private $file_name = 'test.log';
	private $log_dir = '/log';
	private $root_path;
	public $ip;//目标地址
	public $url;//目标url
	public $sleeptime;//命令间隔时间
	public $model;//测试模式,a:音频测试 v:视频测试 r:镜像测试 p:图像测试 h:高级设置 e:扩展设置 i:红外测试 n:网络测试
	public $vencsize;//最大分辨率
	public $codec;//编码方式
	/*******************************音频参数********************************/
	public $inenable;//音频开关
	public $involume;//输入音量
	public $outvolume;//输出音量
	public $codetype;
	public $inputtype;
	/*******************************主码流参数******************************/
	public $array0;//主码流数组:1080P-5 VGA-7 960P-8 D1-2 720P-3 
	public $size0;//主码流分辨率
	public $fps0;//主码流帧率
	public $gop0;
	public $fixbps0;
	public $bps0;
	public $codec0;//编码方式
	/*******************************次码流参数******************************/
	public $array1;//次码流数组:1080P-5 VGA-7 960P-8 D1-2 720P-3 
	public $enable1;//次码流开关
	public $size1;
	public $fps1;//子码流帧率
	public $bps1;//子码流码率
	public $gop1;//子码流I帧间隔
	public $fixbps1;
	public $codec1;//编码方式
	/*******************************图像参数********************************/
	public $reverse;//视频镜像参数(0,1,2,3)
	public $nightluma;//夜视亮度(1,100)
	public $bright;//亮度(1,255)
	public $contrast;//对比度(1,255)
	public $saturation;//饱和度(1,255)
	public $sharpness;//锐度(1,255)
	public $gain;//增益(1,255)
	public $suppress;//强光抑制(0,100)
	public $lampfrequency;//光源频率(0,1)
	public $brightlevel;//亮度水平-2
	/*******************************高级设置********************************/
	public $aeCtrlMode;//曝光
	public $awbCtrlMode;//白平衡模式
	public $redGain;//红增益
	public $blueGain;//蓝增益
	public $lowlightenhance;//低照增强
	/*******************************红外设置********************************/
	public $irswitchmode=2;//自动模式
	public $turnonlux=1;
	/*******************************扩展配置********************************/
	public $vesizeArray=array(1,2,3,5,6,7,8);
	public $vesize;//分辨率(1,2,3,5,6,7,8)
	public $profile;//编码Profile(0,1,2)
	/*******************************网络参数********************************/
	public $ethip;//IP地址
	public $ethmask="255.255.255.0";//子网掩码
	public $ethgw;
	/******************************OSD参数**********************************/
	public $timeleft;//时间字幕坐标横(0,1920)
	public $timetop;//时间字幕纵坐标(0,1080)
	public $timeen;//时间字幕开关(0,1)
	public $nameleft;//名称属性
	public $nametop;
	public $nameen;	
	public $left;//字幕属性
	public $top;
	public $enable;
	public $name='测试专用首开纪录后第三方';
	public $colormode=1;
	/******************************隐私遮挡*********************************/
	public $maskid;
	public $masken;
	public $color;//(0,13)
	public $maskleft;//(0,1814)
	public $masktop;//(0,1001)
	public $maskright;//(99,1913)
	public $maskbottom;//(73,1075)
	/******************************报警设置*********************************/
	public $alarmtype;//1,2,4
	/*******************************发送命令********************************/
	
	public function __construct(){
		$time = date('Ymd-H.i.s');
		$script_path     = __FILE__;//脚本绝对路径
		$script_name     = $_SERVER['SCRIPT_FILENAME'];//脚本名称
		$this->root_path = explode("$script_name",$script_path)[0];//脚本根目录
		/*if(file_exists($this->root_path.$this->log_file)){
			unlink($this->root_path.$this->log_file);
		}*/
		$this->log_file = "{$time}_{$this->file_name}";
		if(!file_exists($this->root_path.$this->log_dir)){
			mkdir($this->root_path.$this->log_dir);
		}
	}	
	/************************获取最大分辨率以及视频压缩格式*************************/
	public function getVideoInfo(){
		$url = "http://$this->ip/?jcpcmd=devvecfg%20-act%20list";
		$curl = curl_init();
		curl_setopt($curl, CURLOPT_URL, $url);
		curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
		curl_setopt($curl, CURLOPT_TIMEOUT,2); 
		$data = curl_exec($curl);
		$video_array = array();
		if($data){
			$array =  explode(';',  explode('#id=1', explode('[Success]',$data)[1])[0]);
			for($i=0;$i<count($array)-1;$i++){
				$video_array[explode('=',$array[$i])[0]] = explode('=',$array[$i])[1];
			}	
		}
		curl_close($curl);
		$this->vencsize = $video_array['vencsize'];
		$this->codec    = $video_array['codec'];
		$this->write_upgrade_log('[getVideoInfo][Vencsize] IS '.$this->vencsize);
		$this->write_upgrade_log('[getVideoInfo][Codec] IS '.$this->codec);			
	}
	/************************根据最大分辨率来设置主码流分辨率*************************/
	public function getVideoSize(){
		switch ($this->vencsize){
			case 13:
				$this->array0=array(2,3,5,7,8,9,12,13);
				break;
			case 12:
				$this->array0=array(2,3,5,7,8,9,12);
				break;
			case 9:
				$this->array0=array(2,3,5,7,8,9);
				break;
			case 5:
				$this->array0=array(2,3,5,7,8);
				break;
			case 8:
				$this->array0=array(2,3,7,8);
				break;
			case 3:
				$this->array0=array(2,3,7);
				break;
			default:
				echo "Error Video Size\r\n";
				exit;
		}
		$this->size0=$this->array0[array_rand($this->array0)];
	}	
	/*****************根据压缩格式来设置当前压缩格式********************/
	public function getCodec(){
		switch($this->codec){
			case 2:
				$this->codec0 = 2;
				$this->codec1 = 2;
				break;
			case 7:
				$array=array(2,7);
				$this->codec0 = $array[array_rand($array)];
				$this->codec1 = $array[array_rand($array)];
				break;
		}	
	}
	/*****************视频测试****************/
	public function video_test(){
		for($i=1;$i<=3;$i++){
			$this->getVideoSize();//获取分辨率
			$this->fps0=rand(1,25);
			$this->gop0=rand(1,50);
			$this->fixbps0=rand(0,1);
			/************设置码流*************/
			if($this->size0==7||$this->size0==2){
				$this->bps0=rand(1024,2048);	
			}else{
				$this->bps0=rand(2048,4096);	
			}
			/*********************************/
			$this->enable1=rand(0,1);
			/*********设置子码流分辨率******/
			if($this->size0==7){
				$this->array1=array(1,6);	
			}elseif($this->size0==2){
				$this->array1=array(1,6,7);
			}else{
				$this->array1=array(1,2,6,7);
			}
			/*******************************/
			$this->size1=$this->array1[array_rand($this->array1)];
			$this->fps1=rand(1,25);
			$this->bps1=rand(32,1024);
			$this->gop1=rand(1,50);
			$this->fixbps1=rand(0,1);
			$this->getCodec();//获取主/从码流的压缩格式，H264/H265
			$this->url="http://$this->ip/?jcpcmd=devvecfg%20-act%20set%20-id%200%20-enable%201%20-vencsize%20$this->size0%20-fps%20$this->fps0%20-bps%20$this->bps0%20-gop%20$this->gop0%20-fixbps%20$this->fixbps0%20-codec%20$this->codec0%20-id%201%20-enable%20$this->enable1%20-vencsize%20$this->size1%20-fps%20$this->fps1%20-bps%20$this->bps1%20-gop%20$this->gop1%20-fixbps%20$this->fixbps1%20-codec%20$this->codec1";
			/*******************************/
			$data = $this->send_command($this->url);//发送命令
			$this->write_upgrade_log('[video_test]'.$this->url);
			curl_close($this->curl);
			if($data){
				echo "NO.$i---";	
				print_r($data);
				$this->write_upgrade_log("[video_test]NO.$i---".$data);
			}else{
				echo "\r\n\r\nSTOP RUNNING\r\n\r\n";
				$this->write_upgrade_log("[video_test]STOP RUNNING");
				echo "RUNS      :$i\r\n\r\n";
				echo "MODEL IS  :[video_test]\r\n\r\n";
				$this->write_upgrade_log("[video_test]RUNS      :$i");
				$this->write_upgrade_log("[video_test]MODEL IS  :[$this->model]");
				//$end_time=date('Y-m-d H:i:s');
				//echo "START_TIME:$start_time\r\n\r\n";
				//echo "END_TIME  :$end_time\r\n\r\n";
				return false;
			}
			sleep(7);
		}
		
	}
	/*****************音频测试****************/
	public function audio_test(){
		for($i=1;$i<=3;$i++){
			$this->inenable=rand(0,1);
			$this->involume=rand(1,100);
			$this->outvolume=rand(1,100);
			$this->codetype=rand(1,2);
			$this->inputtype=rand(0,1);
			$this->url="http://$this->ip/?jcpcmd=audiocfg%20-act%20set%20%20-inenable%20$this->inenable%20-involume%20$this->involume%20-outvolume%20$this->outvolume%20-codetype%20$this->codetype%20-inputtype%20$this->inputtype";
			/****************************/
			$data = $this->send_command($this->url);//发送命令
			$this->write_upgrade_log('[audio_test]'.$this->url);
			curl_close($this->curl);
			/****************************/
			if($data){
				echo "NO.$i---";	
				print_r($data);
				$this->write_upgrade_log("[audio_test]NO.$i---".$data);
			}else{
				echo "\r\n\r\nSTOP RUNNING\r\n\r\n";
				$this->write_upgrade_log("[audio_test]STOP RUNNING");
				echo "RUNS      :$i\r\n\r\n";
				echo "MODEL IS  :[audio_test]\r\n\r\n";
				$this->write_upgrade_log("[audio_test]RUNS      :$i");
				$this->write_upgrade_log("[audio_test]MODEL IS  :[audio_test]");
				return false;
			}
			sleep(1);	
		}
		
	}
	/*****************图像测试****************/
	public function image_test(){
		//图像
		for($i=1;$i<=3;$i++){
			$this->nightluma    =rand(1,100);
			$this->bright       =rand(1,255);
			$this->contrast     =rand(1,255);
			$this->saturation   =rand(1,255);
			$this->sharpness    =rand(1,255);
			$this->gain         =rand(1,255);
			$this->suppress     =rand(0,100);
			$this->lampfrequency=rand(0,1);
			$this->brightlevel  =2;
			$this->url="http://$this->ip/?jcpcmd=vicfg%20-act%20set%20-nightluma%20$this->nightluma%20-bright%20$this->bright%20-contrast%20$this->contrast%20-saturation%20$this->saturation%20-sharpness%20$this->sharpness%20-gain%20$this->gain%20-suppress%20$this->suppress%20%20-lampfrequency%20$this->lampfrequency%20-brightlevel%20$this->brightlevel";
			/****************************/
			$data = $this->send_command($this->url);//发送命令
			$this->write_upgrade_log('[image_test]'.$this->url);
			curl_close($this->curl);
			/****************************/
			if($data){
				echo "NO.$i---";	
				print_r($data);
				$this->write_upgrade_log("[image_test]NO.$i---".$data);
			}else{
				echo "\r\n\r\nSTOP RUNNING\r\n\r\n";
				$this->write_upgrade_log("[image_test]STOP RUNNING");
				echo "RUNS      :$i\r\n\r\n";
				echo "MODEL IS  :[audio_test]\r\n\r\n";
				$this->write_upgrade_log("[image_test]RUNS      :$i");
				$this->write_upgrade_log("[image_test]MODEL IS  :[image_test]");
				return false;
			}
			sleep(1);	
		}
		//镜像
		for($j=1;$j<=3;$j++){
			$this->reverse=rand(0,3);
			$this->url="http://$this->ip/?jcpcmd=vicfg%20-act%20set%20-reverse%20$this->reverse";
			/****************************/
			$data = $this->send_command($this->url);//发送命令
			$this->write_upgrade_log('[image_test]'.$this->url);
			curl_close($this->curl);
			/****************************/
			if($data){
				echo "NO.$j---";	
				print_r($data);
				$this->write_upgrade_log("[image_test]NO.$j---".$data);
			}else{
				echo "\r\n\r\nSTOP RUNNING\r\n\r\n";
				$this->write_upgrade_log("[image_test]STOP RUNNING");
				echo "RUNS      :$j\r\n\r\n";
				echo "MODEL IS  :[audio_test]\r\n\r\n";
				$this->write_upgrade_log("[image_test]RUNS      :$j");
				$this->write_upgrade_log("[image_test]MODEL IS  :[image_test]");
				return false;
			}
			sleep(1);
		}
		//扩展设置
		for($k=1;$k<=3;$k++){
			$this->aeCtrlMode     =rand(0,11);
			$this->awbCtrlMode    =rand(0,7);
			$this->redGain        =rand(1,255);
			$this->blueGain       =rand(1,255);
			$this->lowlightenhance=rand(0,100);
			$this->url="http://$this->ip/?jcpcmd=aeawbblccfg%20-act%20set%20-aeCtrlMode%20$this->aeCtrlMode%20-awbCtrlMode%20$this->awbCtrlMode%20-redGain%20$this->redGain%20-blueGain%20$this->blueGain%20-lowlightenhance%20$this->lowlightenhance";
			/****************************/
			$data = $this->send_command($this->url);//发送命令
			$this->write_upgrade_log('[image_test]'.$this->url);
			curl_close($this->curl);
			/****************************/
			if($data){
				echo "NO.$k---";	
				print_r($data);
				$this->write_upgrade_log("[image_test]NO.$k---".$data);
			}else{
				echo "\r\n\r\nSTOP RUNNING\r\n\r\n";
				$this->write_upgrade_log("[image_test]STOP RUNNING");
				echo "RUNS      :$k\r\n\r\n";
				echo "MODEL IS  :[audio_test]\r\n\r\n";
				$this->write_upgrade_log("[image_test]RUNS      :$k");
				$this->write_upgrade_log("[image_test]MODEL IS  :[image_test]");
				return false;
			}
			sleep(1);
		}
	}
	
	public function osd_test(){
	
	}	
	
	public function send_command($url){
		$this->curl = curl_init();
		curl_setopt($this->curl, CURLOPT_URL, $url);
		curl_setopt($this->curl, CURLOPT_RETURNTRANSFER, 1);
		curl_setopt($this->curl, CURLOPT_TIMEOUT,15); 
		return curl_exec($this->curl);	
	}
	
	public function start_test(){
		/***********视频测试************/
		$this->getVideoInfo();//获取视频最大分辨率以及编码方式
		$this->video_test();
		/***********音频测试*************/
		$this->audio_test();
		/***********图像测试************/
		$this->image_test();
	}
	
	public function write_upgrade_log($msg){
		file_put_contents($this->root_path.$this->log_dir.'\\'.$this->log_file,'['.date('Y-m-d H:i:s').']'.$msg.PHP_EOL, FILE_APPEND);
	}
	
	public function send_curl(){
		date_default_timezone_set('Asia/Shanghai');
		$i=0;
		$start_time=date('Y-m-d H:i:s');
		while(true){
			
			
			
			
		
			
			/*****************扩展测试****************/
			if($this->model=='e'){
				$this->vesize=$this->vesizeArray[array_rand($this->vesizeArray)];
				$this->profile=rand(0,2);
				$this->url="http://$this->ip/?jcpcmd=veprofile%20-act%20set%20-vesize%20$this->vesize%20-profile%20$this->profile";
			}
			/*****************红外测试****************/
			if($this->model=='i'){
				if($this->turnonlux%2==0){
					$this->turnonlux=1;
				}else{
					$this->turnonlux=100;
				}
				$this->url="http://$this->ip/?jcpcmd=ircfg%20-act%20set%20-irswitchmode%20$this->irswitchmode%20-turnonlux%20$this->turnonlux";
			}
			/*****************网络测试****************/
			if($this->model=='n'){
				$last_num=rand(2,254);//尾数
				if($last_num==166){
					$last_num=167;
				}
				$network_segment_array=array(1,2,3,4,5,6,9,10,87,90,100,120,150,199);
				$network_segment=$network_segment_array[array_rand($network_segment_array)];
				$this->ethip="192.168.$network_segment.$last_num";
				$this->ethgw="192.168.$network_segment.1";
				$this->url="http://$this->ip/?jcpcmd=ethcfg%20-act%20set%20-ethip%20$this->ethip%20-ethmask%20$this->ethmask%20-ethgw%20$this->ethgw";
				$this->ip=$this->ethip;
				echo "\r\n\r\n".$this->ip."\r\n\r\n";
			}
			/*****************字幕测试****************/
			if($this->model=='o'){
				$this->timeleft =rand(0,1920);
				$this->timetop  =rand(0,1080);
				$this->timeen   =1;
				$this->nameleft =rand(0,1920);
				$this->nametop  =rand(0,1080);
				$this->nameen   =1;
				$this->url="http://$this->ip/?jcpcmd=osdcfg%20-act%20set%20-nameen%20$this->nameen%20-nameleft%20$this->nameleft%20-nametop%20$this->nametop%20-name%20$this->name%20-timeen%20$this->timeen%20-timeleft%20$this->timeleft%20-timetop%20$this->timetop";
				//
			}
			/****************字幕测试****************/
			if($this->model=='c'){
				$this->left=rand(0,1900);
				$this->top=rand(0,1080);
				$this->enable=1;
				$this->url="http://$this->ip/?jcpcmd=osdstrcfg%20-act%20set%20-index%200%20-enable%20$this->enable%20-content%20$this->name%20-left%20$this->left%20-top%20$this->top";
			}
			/**************字幕颜色测试**************/
			if($this->model=='y'){
				if($this->colormode%2==0){
					$this->colormode=1;
				}else{
					$this->colormode=2;
				}
				$this->url="http://$this->ip/?jcpcmd=osdstylecfg%20-act%20set%20-colormode%20$this->colormode";
			}
			/*****************遮挡测试****************/
			if($this->model=='s'){
				$this->maskid=rand(0,3);
				$this->masken=rand(0,1);
				$this->color=rand(0,13);
				$this->maskleft=rand(0,1814);
				$this->masktop=rand(0,1001);
				$this->maskright=rand(99,1913);
				$this->maskbottom=rand(73,1075);
				$this->url="http://$this->ip/?jcpcmd=videomaskcfg%20-act%20set%20-maskid%20$this->maskid%20-masken%20$this->masken%20-color%20$this->color%20-left%20$this->maskleft%20-top%20$this->masktop%20-right%20$this->maskright%20-bottom%20$this->maskbottom";
			}
			/*****************报警测试****************/
			if($this->model=='w'){
				$alarmtype_array=array(1,2,4);
				$this->alarmtype=$alarmtype_array[array_rand($alarmtype_array)];
				$this->url="http://$this->ip/?jcpcmd=alarmtest%20-act%20set%20-alarmtype%20$this->alarmtype%20-filter%200";	
			}
			
		}
	}
}
$opt=getopt('i:');	
if(!empty($opt['i'])){
	$test=new Test();
	$test->ip=$opt['i'];
	echo "\r\n\r\nSEND IP ADDRESS:$test->ip\r\n\r\n";
	$test->write_upgrade_log("|***********************START************************|");
	$test->write_upgrade_log("SLEEPTIME IS $test->sleeptime");
	$test->write_upgrade_log("SEND IP ADDRESS:$test->ip");
	$test->write_upgrade_log("|********************Testing Now!********************|");
	$test->start_test();
}else{
	echo "\r\n\r\n\r\nparameter declaration:\r\n\r\n";
	echo "test.php [-i]\r\n\r\n";
	echo "-i   IP Address<must>\r\n\r\n";
}