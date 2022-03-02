Search.setIndex({docnames:["README","index","manafa","manafa.parsing","manafa.parsing.batteryStats","manafa.parsing.hunter","manafa.parsing.perfetto","manafa.parsing.powerProfile","manafa.resources","manafa.resources.profiles","manafa.services","manafa.tests","manafa.tests.batterystats","manafa.tests.perfetto","manafa.utils","modules"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":3,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.viewcode":1,sphinx:56},filenames:["README.md","index.rst","manafa.rst","manafa.parsing.rst","manafa.parsing.batteryStats.rst","manafa.parsing.hunter.rst","manafa.parsing.perfetto.rst","manafa.parsing.powerProfile.rst","manafa.resources.rst","manafa.resources.profiles.rst","manafa.services.rst","manafa.tests.rst","manafa.tests.batterystats.rst","manafa.tests.perfetto.rst","manafa.utils.rst","modules.rst"],objects:{"":{manafa:[2,0,0,"-"]},"manafa.emanafa":{EManafa:[2,1,1,""],get_last_boot_time:[2,4,1,""]},"manafa.emanafa.EManafa":{bat_events:[2,2,1,""],batterystats:[2,2,1,""],boot_time:[2,2,1,""],bts_out_file:[2,2,1,""],calculate_cpu_energy:[2,3,1,""],calculate_glob_and_component_consumption:[2,3,1,""],calculate_non_cpu_energy:[2,3,1,""],clean:[2,3,1,""],config:[2,3,1,""],get_consumption_in_between:[2,3,1,""],infer_power_profile:[2,3,1,""],init:[2,3,1,""],parse_results:[2,3,1,""],perfetto:[2,2,1,""],pft_out_file:[2,2,1,""],plug_back:[2,3,1,""],power_profile:[2,2,1,""],resources_dir:[2,2,1,""],start:[2,3,1,""],stop:[2,3,1,""],timezone:[2,2,1,""],unplug_if_fully_charged:[2,3,1,""],unplugged:[2,2,1,""]},"manafa.hunter_emanafa":{HunterEManafa:[2,1,1,""]},"manafa.hunter_emanafa.HunterEManafa":{calculate_function_consumption:[2,3,1,""],clean:[2,3,1,""],init:[2,3,1,""],parse_results:[2,3,1,""],power_profile:[2,2,1,""],resources_dir:[2,2,1,""],start:[2,3,1,""],stop:[2,3,1,""],timezone:[2,2,1,""],unplugged:[2,2,1,""]},"manafa.main":{create_manafa:[2,4,1,""],has_connected_devices:[2,4,1,""],main:[2,4,1,""],parse_results:[2,4,1,""],print_profiled_stats:[2,4,1,""]},"manafa.parsing":{batteryStats:[4,0,0,"-"],hunter:[5,0,0,"-"],perfetto:[6,0,0,"-"],powerProfile:[7,0,0,"-"]},"manafa.parsing.batteryStats":{BatteryStatsConstants:[4,0,0,"-"],BatteryStatsParser:[4,0,0,"-"]},"manafa.parsing.batteryStats.BatteryStatsParser":{BatteryEvent:[4,1,1,""],BatteryStatsParser:[4,1,1,""],safe_division:[4,4,1,""]},"manafa.parsing.batteryStats.BatteryStatsParser.BatteryEvent":{add_events:[4,3,1,""],concurrentUpdates:[4,2,1,""],current:[4,2,1,""],get_current_of_batStatEvent:[4,3,1,""],get_voltage_value:[4,3,1,""],is_concurrent:[4,3,1,""],time:[4,2,1,""],updates:[4,2,1,""]},"manafa.parsing.batteryStats.BatteryStatsParser.BatteryStatsParser":{add_update:[4,3,1,""],android_version:[4,2,1,""],definitions:[4,2,1,""],determinate_component_current:[4,3,1,""],estimate_current_consumption:[4,3,1,""],events:[4,2,1,""],get_CPU_samples_in_between:[4,3,1,""],get_closest_pair:[4,3,1,""],get_definition_val:[4,3,1,""],get_events_in_between:[4,3,1,""],is_trival:[4,3,1,""],load_definition_file:[4,3,1,""],parse_file:[4,3,1,""],parse_history:[4,3,1,""],parse_states:[4,3,1,""],powerProfile:[4,2,1,""],start_time:[4,2,1,""],timezone:[4,2,1,""]},"manafa.parsing.hunter":{AppConsumptionStats:[5,0,0,"-"],HunterParser:[5,0,0,"-"]},"manafa.parsing.hunter.AppConsumptionStats":{AppConsumptionStats:[5,1,1,""]},"manafa.parsing.hunter.AppConsumptionStats.AppConsumptionStats":{app_traces:[5,2,1,""],clean:[5,3,1,""],get_output_filepath:[5,3,1,""],results_dir:[5,2,1,""],save_function_info:[5,3,1,""],write_consumptions:[5,3,1,""]},"manafa.parsing.hunter.HunterParser":{HunterParser:[5,1,1,""]},"manafa.parsing.hunter.HunterParser.HunterParser":{add_consumption:[5,3,1,""],add_cpu_consumption_to_trace_file:[5,3,1,""],boot_time:[5,2,1,""],end_time:[5,2,1,""],parse_file:[5,3,1,""],parse_history:[5,3,1,""],return_cpu_consumption_and_time_by_function:[5,3,1,""],trace:[5,2,1,""],update_trace_return:[5,3,1,""],verify_function:[5,3,1,""]},"manafa.parsing.perfetto":{perfettoParser:[6,0,0,"-"]},"manafa.parsing.perfetto.perfettoParser":{CPU_STATE:[6,1,1,""],PerfettoCPUEvent:[6,1,1,""],PerfettoCPUfreqParser:[6,1,1,""],interpolate:[6,4,1,""]},"manafa.parsing.perfetto.perfettoParser.CPU_STATE":{ACTIVE:[6,2,1,""],AWAKE:[6,2,1,""],IDLE:[6,2,1,""],SUSPEND:[6,2,1,""]},"manafa.parsing.perfetto.perfettoParser.PerfettoCPUEvent":{calculate_CPUs_current:[6,3,1,""],init_all:[6,3,1,""],update:[6,3,1,""],vals:[6,2,1,""]},"manafa.parsing.perfetto.perfettoParser.PerfettoCPUfreqParser":{add_event:[6,3,1,""],get_closest_pair:[6,3,1,""],load_power_profile:[6,3,1,""],parse_event:[6,3,1,""],parse_file:[6,3,1,""],parse_history:[6,3,1,""],start_time:[6,2,1,""],timezone:[6,2,1,""]},"manafa.parsing.powerProfile":{PowerProfile:[7,0,0,"-"]},"manafa.parsing.powerProfile.PowerProfile":{PowerProfile:[7,1,1,""]},"manafa.parsing.powerProfile.PowerProfile.PowerProfile":{add_component:[7,3,1,""],get_CPU_core_speed_pair:[7,3,1,""],get_CPU_state_current:[7,3,1,""],merge_two_dicts:[7,3,1,""]},"manafa.resources":{profiles:[9,0,0,"-"]},"manafa.services":{LogService:[10,0,0,"-"],batteryStatsService:[10,0,0,"-"],perfettoService:[10,0,0,"-"],service:[10,0,0,"-"]},"manafa.services.LogService":{LogService:[10,1,1,""]},"manafa.services.LogService.LogService":{boot_time:[10,2,1,""],clean:[10,3,1,""],config:[10,3,1,""],get_results_filename:[10,3,1,""],init:[10,3,1,""],output_res_folder:[10,2,1,""],start:[10,3,1,""],stop:[10,3,1,""]},"manafa.services.batteryStatsService":{BatteryStatsService:[10,1,1,""]},"manafa.services.batteryStatsService.BatteryStatsService":{boot_time:[10,2,1,""],clean:[10,3,1,""],config:[10,3,1,""],init:[10,3,1,""],output_res_folder:[10,2,1,""],start:[10,3,1,""],stop:[10,3,1,""]},"manafa.services.perfettoService":{PerfettoService:[10,1,1,""]},"manafa.services.perfettoService.PerfettoService":{"export":[10,3,1,""],cfg_file:[10,2,1,""],clean:[10,3,1,""],config:[10,3,1,""],default_out_dir:[10,2,1,""],get_run_id_from_perfetto_file:[10,3,1,""],init:[10,3,1,""],output_res_folder:[10,2,1,""],start:[10,3,1,""],stop:[10,3,1,""]},"manafa.services.service":{Service:[10,1,1,""]},"manafa.services.service.Service":{clean:[10,3,1,""],config:[10,3,1,""],results_dir:[10,2,1,""],save_results:[10,3,1,""],start:[10,3,1,""],stop:[10,3,1,""]},"manafa.tests":{batterystats:[12,0,0,"-"],perfetto:[13,0,0,"-"]},"manafa.tests.batterystats":{test_batteryStatsService:[12,0,0,"-"]},"manafa.tests.batterystats.test_batteryStatsService":{TestBatteryStatsService:[12,1,1,""]},"manafa.tests.batterystats.test_batteryStatsService.TestBatteryStatsService":{test_stop:[12,3,1,""]},"manafa.tests.perfetto":{test_perfettoService:[13,0,0,"-"]},"manafa.tests.perfetto.test_perfettoService":{TestPerfettoService:[13,1,1,""]},"manafa.tests.perfetto.test_perfettoService.TestPerfettoService":{test_clean:[13,3,1,""],test_export:[13,3,1,""],test_start:[13,3,1,""],test_stop:[13,3,1,""]},"manafa.utils":{Logger:[14,0,0,"-"],Utils:[14,0,0,"-"],dateUtils:[14,0,0,"-"]},"manafa.utils.Logger":{LogSeverity:[14,1,1,""],getColor:[14,4,1,""],log:[14,4,1,""]},"manafa.utils.Logger.LogSeverity":{ERROR:[14,2,1,""],FATAL:[14,2,1,""],INFO:[14,2,1,""],SUCCESS:[14,2,1,""],WARNING:[14,2,1,""]},"manafa.utils.Utils":{execute_shell_command:[14,4,1,""],get_pack_dir:[14,4,1,""],get_reference_dir:[14,4,1,""],get_resources_dir:[14,4,1,""],get_results_dir:[14,4,1,""],is_float:[14,4,1,""],mega_find:[14,4,1,""]},"manafa.utils.dateUtils":{batStatResetTimeToTimeStamp:[14,4,1,""],convertBatStatTimeToTimeStamp:[14,4,1,""],convertDateToTimeStamp:[14,4,1,""],convertToUnixTimestamp:[14,4,1,""],epochToDate:[14,4,1,""]},manafa:{emanafa:[2,0,0,"-"],hunter_emanafa:[2,0,0,"-"],main:[2,0,0,"-"],parsing:[3,0,0,"-"],resources:[8,0,0,"-"],services:[10,0,0,"-"],tests:[11,0,0,"-"],utils:[14,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","attribute","Python attribute"],"3":["py","method","Python method"],"4":["py","function","Python function"]},objtypes:{"0":"py:module","1":"py:class","2":"py:attribute","3":"py:method","4":"py:function"},terms:{"0":[0,2,4,5,6,10,14],"1":1,"10":4,"1000":0,"1646224033":14,"2":[1,4],"3a":0,"45831":14,"4a":0,"5g":0,"60":0,"8":[0,6],"9":0,"9223372036854775807":[2,5],"999":14,"abstract":[2,10],"case":[12,13],"class":[2,3,4,5,6,7,10,12,13,14],"default":[2,6,10],"enum":[4,6,14],"export":[0,10],"float":[2,4,5,6,10],"function":[2,4,5,10],"int":[4,5,6],"new":[0,4],"return":[2,4,5,6,7,10],"static":[4,5,6,7],"super":2,"true":4,A:[6,10],For:1,In:[0,7],It:[4,5],The:[0,10],To:10,_:0,__extractpowerprofil:2,abc:10,abl:0,about:[0,7],abov:0,accur:0,activ:6,adb:2,add:[4,6,7],add_compon:7,add_consumpt:5,add_cpu_consumption_to_trace_fil:5,add_ev:[4,6],add_funct:5,add_upd:4,addit:0,adequ:2,after:[6,7,10],afterward:10,aka:4,all:[2,6],allow:2,also:[0,2,4,5,10],alwai:0,an:[0,2,6,10,14],analyz:1,android:[1,4],android_hom:0,android_vers:4,ands:4,ani:0,api:10,app:[2,5],app_trac:5,apparatu:0,appconsumptionstat:[2,3],appropri:2,ar:[0,2],arg:[2,14],argument:6,ask:10,associ:4,attribut:[4,5,6,7,10],aux:2,avail:0,avoid:4,awak:6,b:4,back:2,base:[0,2,4,5,6,7,10,12,13,14],basedir:14,bash:0,bashrc:0,bat_ev:[0,2,4],batstat:4,batstatresettimetotimestamp:14,batstatsfil:0,batstattim:14,battarystat:2,batteri:[0,2,10],batteryev:4,batterystat:[0,2,3,5,10,11],batterystatsconst:[2,3],batterystatspars:[2,3],batterystatsservic:[2,15],batterystatu:4,befor:[6,7,10],begin:[0,2],behaviour:2,being:[4,6,7],between:[0,2,4,6],bf:0,bin:[0,10],blank:10,bool:4,boot:[2,5,10],boot_tim:[2,5,10],bound:[5,6],brief:10,bt:0,bt_event:4,bts_file:2,bts_out_fil:2,c:0,calcul:[0,2,4],calculate_cpu_energi:2,calculate_cpus_curr:6,calculate_function_consumpt:2,calculate_glob_and_component_consumpt:2,calculate_non_cpu_energi:2,call:[2,5,10],can:[0,2],cfg_file:10,chang:4,charg:[0,2],charger:2,check:[2,4,5],clean:[2,5,10],clear:5,closest:[4,6,7],cmd:14,code:2,collect:0,com:0,come:[3,4],command:[1,4],comp_nam:4,compat:10,compon:[0,2,4,5,7],conceicao:10,concurr:4,concurrentupd:4,config:[2,10],connect:2,consecut:4,consid:[2,6,10],constant:4,consum:[0,2,4,5,6,7],consumpt:[0,2,4,5,7],contain:[0,2,3,4,5,7,10],content:15,convertbatstattimetotimestamp:14,convertdatetotimestamp:14,converttounixtimestamp:14,core:[6,7],core_freq:7,core_id:7,correspond:6,count:0,cpu:[0,2,4,6,7],cpu_consumpt:5,cpu_freq:6,cpu_id:6,cpu_stat:6,cpufreq:6,create_manafa:2,cross:10,current:[0,4,5,6,7,10],custom:5,da_tim:5,data:[0,10],date:14,dateutil:[2,15],ddr:0,def_fil:4,default_len:6,default_out_dir:10,default_res_dir:14,default_results_dir:14,definit:[4,5],delta_tim:2,deriv:0,descript:10,design:2,determin:[2,5],determinate_component_curr:4,develop:0,devi:10,devic:[1,2,4,5,6,7,10],dict:[2,4,5,7],differ:7,dir:10,directori:[2,5],disabl:5,discard:10,divis:4,do_work_to_profil:0,docstr:10,doe:10,drawn:0,dump:10,dumpsi:[2,4],durat:2,dure:[2,4,5,10],each:[0,2,4,6,7,10],either:2,elaps:5,em:0,emanafa:[0,4,5,15],enabl:5,end:[0,2,4,5],end_tim:[2,4,5],energi:[1,2,5],enumer:[6,14],env:0,enviro:0,epochtod:14,equival:5,error:14,est:[4,6,14],estim:[0,2,4,7],estimate_current_consumpt:4,ev_str:6,event:[0,2,4,5,6,10],event_tim:6,event_timelin:2,everi:2,exampl:[0,10],except:2,execut:[0,5,10],execute_shell_command:14,expect:6,extend:2,extern:0,extract:[0,2],f:0,fals:[4,5],far:[0,2,5],fatal:14,field:4,file:[0,2,4,5,6,7,10],file_id:10,filenam:[2,5,6,7,10],filepath:[4,5,6,10],filter:[4,5],filter_zero:5,fine:0,first:[0,4],fix:7,folder:[0,10],follow:0,forget:10,format:6,formula:0,framework:[0,2,10],freq:6,frequenc:[0,6,7],from:[1,2,3,4,5,6,7,10],fst_pair:7,fulli:2,function_nam:5,g:0,gener:[2,5],get:[4,5],get_closest_pair:[4,6],get_consumption_in_between:2,get_cpu_core_speed_pair:7,get_cpu_samples_in_between:4,get_cpu_state_curr:7,get_current_of_batstatev:4,get_definition_v:4,get_events_in_between:4,get_last_boot_tim:2,get_output_filepath:5,get_pack_dir:14,get_reference_dir:14,get_resources_dir:14,get_results_dir:14,get_results_filenam:10,get_run_id_from_perfetto_fil:10,get_voltage_valu:4,getcolor:14,getconsumptioninbetween:0,git:0,github:0,given:[2,4,6,7,10],global:2,googl:0,grain:0,granular:2,guidelin:0,handl:4,hardwar:4,has_connected_devic:2,have:[4,6],help:10,high:0,him:10,histori:[4,5],home:0,htr_file:2,http:0,hunter:[2,3,10],hunter_emanafa:15,hunteremanafa:2,hunterpars:[2,3],i:6,id:[2,6,7,10],identifi:[4,7],idl:6,index:[1,4,5,6],individu:0,infer:4,infer_power_profil:2,info:[2,5,7,14],inform:[0,3,4,5,6,7,10],init:[0,2,6,10],init_al:6,initi:4,inner:2,input:10,insert:6,instal:1,instant:4,instantan:6,instrument:5,instrument_fil:2,interpol:[6,7],interv:2,is_concurr:4,is_float:14,is_triv:4,its:10,itself:2,joul:0,json:4,kei:4,known:[4,5],kwarg:[2,10],last:[0,2,4,5,10],last_ev:2,last_export:10,lasti:6,least:0,leav:10,level:[0,2],lifecycl:10,line:[1,4,5,6,10],linear:6,lines_list:[4,5],linux:0,list:[4,5,6],lite:0,load:[4,5,6],load_definition_fil:4,load_power_profil:6,local:2,log:[0,2,5,6,10,14],log_sev:14,logcat:[2,3],logfil:5,logger:[2,15],logservic:[2,15],logsever:14,lower:[5,6],m:0,maatrail:0,mac:0,mai:10,main:15,mainli:0,manag:10,mani:7,manipul:[3,4],manufactur:0,matim:14,maxdepth:14,mean:4,measur:[0,7],mega_find:14,memori:0,memorypow:0,memorypowercalcul:0,merge_two_dict:7,messag:14,method:[2,5],methodnam:[12,13],metric:[2,5],mi:0,mindepth:14,misc:10,model:[0,2],modul:[1,15],monitor:1,monsoon:0,more:4,most:2,ms:[2,4],n:[0,14],name:[2,4,5,10],need:[0,7,10],new_ev:4,nix:0,none:[2,4,5,6,10],not_instrument_fil:2,note:0,number:[4,5,6],object:[4,5,6,7],obtain:[2,4,6],occur:[0,2,4],ok:4,one:[4,10],ones:7,onli:[2,10],opt:4,option:[4,5,10],order:[0,4,7,10],os:0,other:2,otherwis:[2,4],output:[2,4,5,6,10],output_dir:10,output_nam:10,output_res_fold:10,over:10,overal:10,p:0,packag:[1,15],packnam:14,page:1,pair:7,param:[2,4,5,6,7,10],paramet:[2,4,7],paramm:5,pars:[2,15],parse_ev:6,parse_fil:[4,5,6],parse_histori:[4,5,6],parse_result:2,parse_st:4,parsefil:[4,5],parser:2,parseresult:0,pass:6,path:[0,2,5,6,7,10],pattern:14,patttern:6,per:[0,2,5],per_comp_consumpt:2,per_compon:2,per_component_consumpt:[2,5],perfetto:[0,2,3,10,11],perfetto_filepath:10,perfettocpuev:6,perfettocpufreqpars:6,perfettofil:0,perfettopars:[2,3],perfettoservic:[2,15],perform:[0,4,6],period:10,pf:0,pf_file:2,pf_out_fil:2,pft:0,pft_out_fil:2,pick:2,pip:1,pixel:0,plai:0,platform:0,plug:[0,2],plug_back:2,plugin:5,posit:5,possibl:4,possible_st:4,power:[0,2,4,5,6,7],power_profil:[2,4,6],powerprofil:[2,3,4],practic:0,present:2,previou:[2,10],print:0,print_profiled_stat:2,prior:10,procedur:[0,2],product:2,prof:0,profiil:10,profil:[0,2,4,5,6,7,8,10],program:10,properti:2,provid:0,pull:10,purpos:10,py:[0,4],python:1,quot:4,r:0,rang:4,rate:0,read:[0,4],record:[2,4,7,10],refer:[4,5,6,10],regard:[6,7],regist:[4,5],relat:[0,4],releas:[0,4],remov:10,replac:0,repo:[2,4,5],repres:0,reset:10,resourc:[0,2,4,14,15],resources_dir:2,respect:[2,4],respons:10,rest:10,result:[2,4,5,6,10,14],results_dir:[5,10],retriev:[2,7],return_cpu_consumption_and_time_by_funct:5,right:10,ro:2,root:0,rrua:0,rtype:[5,6,10],ruirua:[2,4,5],run:[0,7,10],run_id:[2,10],runtest:[12,13],s:[2,4,5,10],safe:4,safe_divis:4,same:[4,10],sampl:[0,6],save:[5,10],save_function_info:5,save_result:10,script:0,sdk:0,search:1,sec:2,self:[2,7],sensor:4,servic:[2,4,15],session:[2,6,10],set:[0,4],setup:1,sev:14,shell:0,should:10,sinc:0,snd_pair:7,so:[0,2,5],softwar:0,sourc:[1,2,4,5,6,7,10,12,13,14],specif:[0,7],start:[0,2,4,5,10],start_tim:[2,4,5,6],startup:0,stat:[5,10],state:[0,2,4,5,6,7,10],step:2,stop:[0,2,10],storag:10,store:[2,4,5,6,7,10],str:[2,4,5,7,10],string:[4,6,14],studio:0,sub:4,submodul:[3,11,15],subpackag:15,success:[4,14],successfuli:0,summari:10,suppli:0,support:[1,4],suspend:6,system:[0,2],systrac:6,t:0,task:10,tech:0,termin:10,test:[2,15],test_batterystatsservic:[2,11],test_clean:13,test_export:13,test_id:5,test_perfettoservic:[2,11],test_start:13,test_stop:[12,13],testbatterystatsservic:12,testcas:[12,13],testperfettoservic:13,than:4,them:4,thi:[0,3,4,5,10],time:[0,2,4,5,6,7,10,14],timem:0,timestamp:[2,4,5,6,10],timestmp:5,timezon:[0,2,4,6,14],todo:1,tool:0,total:[0,2,4],total_consumpt:2,trace:[2,5,10],traceconv:10,ts:14,txt:0,type:[2,4,5,6,7,10],type_fil:14,tz:0,unittest:[12,13],unplug:2,unplug_if_fully_charg:2,updat:[4,5,6],update_trace_return:5,upper:5,us:[0,2,4,5,10],usag:[1,4,10],user:[0,2,4,5],utc:14,util:[2,4,15],val:[4,6],valu:[4,5,6,7,14],verify_funct:5,version:4,via:[1,2],virtual:2,voltag:4,wa:[0,2,5],warn:14,well:10,when:[4,5,10],where:[2,5,10],which:2,whose:2,wide:0,wipe:10,without:2,write:[0,5],write_consumpt:5,written:5,x1:6,x2:6,x:[6,7],xiaomi:0,xml:[0,2,4,7],xml_profil:6,y1:6,y2:6,y:7,your:0,z:0,zaidu:10,zero:5},titles:["E-MANAFA: Energy Monitor and ANAlyzer For Android","Welcome to E-MANAFA\u2019s documentation!","manafa package","manafa.parsing package","manafa.parsing.batteryStats package","manafa.parsing.hunter package","manafa.parsing.perfetto package","manafa.parsing.powerProfile package","manafa.resources package","manafa.resources.profiles package","manafa.services package","manafa.tests package","manafa.tests.batterystats package","manafa.tests.perfetto package","manafa.utils package","manafa"],titleterms:{"1":0,"2":0,"3":0,"4":0,"6":0,For:0,activ:0,analyz:0,android:0,appconsumptionstat:5,batterystat:[4,12],batterystatsconst:4,batterystatspars:4,batterystatsservic:10,clone:0,command:0,content:[1,2,3,4,5,6,7,8,9,10,11,12,13,14],dateutil:14,defin:0,dev:0,devic:0,document:1,e:[0,1],emanafa:2,energi:0,environ:0,from:0,hunter:5,hunter_emanafa:2,hunterpars:5,indic:1,instal:0,line:0,local:0,logger:14,logservic:10,main:2,manafa:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],modul:[2,3,4,5,6,7,8,9,10,11,12,13,14],monitor:0,packag:[0,2,3,4,5,6,7,8,9,10,11,12,13,14],pars:[3,4,5,6,7],perfetto:[6,13],perfettopars:6,perfettoservic:10,pip:0,powerprofil:7,profil:9,python:0,replic:0,repo:0,requir:0,resourc:[8,9],s:1,servic:10,setup:0,sourc:0,submodul:[2,4,5,6,7,10,12,13,14],subpackag:[2,3,8,11],support:0,tabl:1,test:[11,12,13],test_batterystatsservic:12,test_perfettoservic:13,todo:0,usag:0,util:14,variabl:0,via:0,virtual:0,virtualenv:0,welcom:1}})