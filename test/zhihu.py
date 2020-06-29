import requests
import re
from bs4 import BeautifulSoup
from time import sleep
import json
import random
import os
import threading
from queue import Queue


ROOT_DIR = 'pic'

def geturl():
    ulist = []
    for i in range(1, 50):
        offset = i*5
        url = 'https://www.zhihu.com/api/v4/questions/384408291/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset='+str(offset)+'&platform=desktop&sort_by=default'
        ulist.append(url)
    return ulist
        
def pic(urls, headers, img_queue):    
    for url in urls:
        reponse = requests.get(url,headers=headers,timeout=30).text
        res = json.loads(reponse)
        data =res['data']
        try:
            for i in data:
                a = i['content']
                pic_url = re.findall('data-original="(.*?)"', a)
                pic_url_set = set(pic_url)
                for u in pic_url_set:
                    print('put: ', u)
                    img_queue.put(u)
        except:
            print('没有找到图片')
    img_queue.put(None)
    
def savepic(html):
    for pic_url in html:
        if len(pic_url) > 0:
            for u in pic_url:
                sleep(0.2)
                r = requests.get(u, headers=headers, timeout=30)
                if not os.path.exists(img_path):
                    print("准备爬取" + u)
                    with open(img_path, 'wb+') as f:
                        f.write(r.content)

def get_img_thread(img_queue):
    while True:
        url = img_queue.get()
        print('get: ', url)
        if url == None:
            img_queue.put(None)
            break
        img_name = url.split(r'/')[-1]
        img_path = ROOT_DIR + "/" + img_name
        if not os.path.exists(img_path):
            print("准备爬取" + url)
            try:
                r = requests.get(url, headers=headers, timeout=30)
            except Exception as e:
                print(e)
            else:
                if r.status_code == 200:
                    with open(img_path, 'wb+') as f:
                        f.write(r.content)
        sleep(1)
    print('get_img_thread exit')
    
if __name__ == '__main__':
    
    headers= {
        'referer': 'https://www.zhihu.com/question/384408291',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
        'cookie': '_zap=1510ab43-539f-499e-b20a-07fd5fb0c732; d_c0="ALAZvOH_-BCPTtV6Ingc9mFl_Or4fgRQ28I=|1584367983"; _ga=GA1.2.1688122394.1584368001; _xsrf=JfnsH7Z1yKYfcP49CG7imsa5mjbgGt3K; capsion_ticket="2|1:0|10:1585310540|14:capsion_ticket|44:M2MwZTdhZDExZmUzNGNmMjllMzhlZWMwNWY5MzlmNWU=|588069734974d216c0056bb91c58f08b3e12cca56c7f341a2b379ebd12f70566"; z_c0="2|1:0|10:1585310553|4:z_c0|92:Mi4xNDAyMkJRQUFBQUFBc0JtODRmXzRFQ1lBQUFCZ0FsVk5XVGxyWHdEZ2VLS2FPdzhMNENrVGRGdkpoTEZWN0txMWNB|02eac5fc54e2182b162cc6e211ccbf013985a5b8d7760ca61a29a07dc5afd40c"; tst=r; _gid=GA1.2.163162890.1585453007; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1585310391,1585312013,1585453006,1585456182; _gat_gtag_UA_149949619_1=1; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1585462816; KLBRSID=af132c66e9ed2b57686ff5c489976b91|1585462869|1585453005',
        'x-ab-param': 'zr_article_new=open;soc_wonderuser_recom=2;soc_brdcst3=0;tsp_videobillboard=7;zr_expslotpaid=8;tp_club_pic_swiper=1;ug_follow_topic_1=2;zr_answer_rec_cp=open;se_pek_test2=1;soc_userrec=2;soc_bigone=1;li_paid_answer_exp=1;li_tjys_ec_ab=0;li_video_section=1;li_sku_bottom_bar_re=0;soc_bignew=1;zr_slot_training=2;pf_noti_entry_num=1;ug_goodcomment_0=1;se_expired_ob=0;se_entity_model=1;se_cardrank_2=1;se_backsearch=0;tp_club_pk=1;soc_newfeed=2;pf_foltopic_usernum=50;ug_follow_answerer=0;se_topiclabel=1;tp_topic_rec=1;li_vip_no_ad_mon=0;soc_adreadline=0;qap_ques_invite=0;se_college_cm=1;top_hotcommerce=1;soc_iospinweight=0;tsp_hotlist_ui=3;li_pay_banner_type=8;zw_sameq_sorce=999;se_site_onebox=0;tp_club_join=1;ug_zero_follow_0=0;li_assessment_show=1;se_multianswer=0;tp_topic_entry=0;tp_m_intro_re_topic=1;soc_notification=1;li_catalog_card=1;se_search_feed=N;soc_ri_merge=0;ug_zero_follow=0;zr_km_answer=open_cvr;se_club_post=5;se_college=default;se_col_boost=1;se_topicfeed=0;tp_discover=1;soc_authormore=2;top_root=0;li_svip_cardshow=1;se_preset_label=1;se_cardrank_3=0;tp_sft=a;tp_club_android_feed=old;top_test_4_liguangyi=1;soc_yxzl_zcfw=0;li_android_vip=0;li_education_box=1;zr_search_sim=2;se_sug=1;se_sug_term=1;qap_question_visitor= 0;se_rel_search=1;se_subtext=1;li_answer_card=0;se_lottery=0;tp_club_android_join=1;ug_newtag=1;zr_training_first=false;se_hotsearch_num=0;se_agency= 0;se_famous=1;li_se_edu=1;li_se_across=1;zr_slotpaidexp=8;se_colorfultab=1;se_hot_timebox=1;pf_fuceng=1;ls_videoad=2;li_album_liutongab=0;zr_km_style=base;se_relationship=1;se_cbert_ab=1;zr_km_slot_style=event_card;se_auto_syn=0;soc_zcfw_broadcast2=1;se_ffzx_jushen1=0;se_cardrank_1=0;li_hot_voted=0;se_bert_comp=0;se_ios_spb309=1;se_cate_l3=0;se_highlight=0;pf_adjust=0;se_webtimebox=1;se_use_zitem=0;tp_header_style=1;ls_recommend_test=2;soc_iosintimacy=2;pf_creator_card=1;se_new_p=0;se_hotsearch_2=1;se_new_merger=1;se_p_slideshow=1;tp_club_pic=0.6;se_ctx_rerank=1;se_adxtest=1;soc_iossort=0;zr_art_rec=base;se_cardrank_4=1;soc_zcfw_shipinshiti=1;li_search_v5=1;se_preset_tech=0;tp_qa_metacard_top=top;li_se_media_icon=1;zr_test_aa1=1;tp_club_tab_feed=0;top_v_album=1;se_mobileweb=1;se_time_threshold=0;sem_up_growth=in_app;li_qa_new_cover=1;li_salt_hot=1;zr_video_rank=new_rank;tp_topic_tab_new=0-0-0;soc_special=0;soc_zuichangfangwen=0;li_svip_tab_search=1;li_ebok_chap=0;zr_rec_answer_cp=close;zr_ans_rec=gbrank;se_spb309=0;se_pek_test=1;se_pek_test3=1;se_zu_onebox=0;se_cbert=1;se_prf=0;tp_topic_style=0;soc_authormore2=2;li_answer_right=0;zr_slot_cold_start=aver;se_relation_1=2;se_billboardsearch=0;soc_adsort=0;ug_follow_answerer_0=0;tp_topic_head=0;li_yxzl_new_style_a=1;zr_km_feed_nlp=old;se_click_club=0;se_rf_w=0;se_waterfall=0;tp_club_qa_pic=1;soc_iosreadfilter=0;se_timebox_up=0;se_aa_base=0;soc_adpinweight=0;li_purchase_test=0;li_query_match=1;qap_payc_invite=0;zr_km_sku_thres=false;soc_brdcst4=3;se_ltr_cp_new=0;ls_zvideo_license=1;top_universalebook=1;li_qa_btn_text=0;li_ebook_audio=1;zr_video_rank_nn=new_rank;se_entity_model_14=0;soc_leave_recommend=2;se_websearch=3;ls_zvideo_rec=2;li_answer_label=0;li_se_section=1;zr_intervene=0;zr_rel_search=base;se_new_topic=0;se_webmajorob=0;se_sug_entrance=1;se_whitelist=1;tp_qa_toast=1;zr_km_sku_mix=sku_20;top_new_feed=5;se_ltr_video=1;se_presearch_ab=0;tp_meta_card=0;soc_update=1;ls_fmp4=0;qap_thanks=1;se_likebutton=0;se_ltr_dnn_cp=0;se_hotsearch=1;zr_update_merge_size=2;tp_sft_v2=d;soc_adreadfilter=0;soc_zcfw_badcase=0;pf_newguide_vertical=0;ug_fw_answ_aut_1=0;li_vip_verti_search=0;qap_article_like=1;top_quality=0;se_related_index=3;se_wannasearch=a;se_amovietab=1;li_ebook_read=0;li_se_heat=1;tp_score_1=a;tp_discover_copy=1;tp_qa_metacard=1;soc_zcfw_broadcast=0;tp_club_feed=1;soc_feed_intimacy=2;li_hot_score_ab=0;zr_video_recall=current_recall;se_ad_index=10;se_featured=1;se_payconsult=5;tp_club_tab=0;soc_stickypush=1;tsp_vote=2;li_answers_link=0;zr_slot_filter=false;se_hotmore=2;tp_club_qa=1;se_webrs=1;se_zu_recommend=0;tp_sticky_android=2;soc_iosreadline=0;soc_cardheight=2;tp_topic_tab=0;top_ebook=0;top_ydyq=X;qap_question_author=0;zw_payc_qaedit=0;se_movietab=1;tp_club_header=1'
    }
    
    img_queue = Queue() # 存放img链接的消息队列
    
    urls = geturl() # 获取链接
    
    threads = []
    
    for i in range(5):
        thread = threading.Thread(target=get_img_thread, args=(img_queue,)) # 下载线程
        threads.append(thread)
        
    for t in threads:
        t.start()
    
    pic(urls, headers, img_queue)   # 获取img链接，然后put到消息队列
    
    for t in threads:
        t.join()
        
    print('finished')
    
    # savepic()
    
    # t1 = threading.Thread(target=pic,args=(urls,headers))
    # t2 = threading.Thread(target=savepic,args=(html))
    # t1.setDaemon(True)
    # t1.start()
    # t2.start()
