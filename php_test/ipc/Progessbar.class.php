<?php
class Progessbar{
    function __construct($length=100,$strType='*',$info="{}%"){
        $this->length=$length;
        $this->strType=$strType;
        $this->info=$info;
    }
    
    public function showProgessBar($progess){//$progess[1~100]
        $ProgessStr_length=floor($progess*$this->length/100);
        $Space_length=$this->length-$ProgessStr_length;
        $progessStr=$this->makeProgessStr($ProgessStr_length);
        $spaceStr=$this->makeSpace($Space_length);  
        $info=str_replace("{}",$progess,$this->info);
        echo "\r[".$progessStr.$spaceStr."]".$info;
    }
    
    public function makeSpace($length){
        $str='';
        for($i=1;$i<=$length;$i++){
            $str=$str.' ';
        }
        return $str;
    }
    
    public function makeProgessStr($length){
        $str='';
        for($i=1;$i<=$length;$i++){
            $str=$str.$this->strType;
        }
        return $str;
    }
}
