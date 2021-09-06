Search.setIndex({docnames:["cli/cli","general/general","index","package/api","package/common","package/core","package/database","package/objects"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":4,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,"sphinx.ext.viewcode":1,sphinx:56},filenames:["cli/cli.rst","general/general.rst","index.rst","package/api.rst","package/common.rst","package/core.rst","package/database.rst","package/objects.rst"],objects:{"CveXplore.api.connection":{api_db:[3,0,0,"-"]},"CveXplore.api.connection.api_db":{ApiDatabaseCollection:[3,1,1,""],ApiDatabaseSource:[3,1,1,""]},"CveXplore.api.connection.api_db.ApiDatabaseCollection":{__init__:[3,2,1,""],__repr__:[3,2,1,""],find:[3,2,1,""],find_one:[3,2,1,""]},"CveXplore.api.connection.api_db.ApiDatabaseSource":{__init__:[3,2,1,""],__repr__:[3,2,1,""]},"CveXplore.api.helpers":{cve_search_api:[3,0,0,"-"]},"CveXplore.api.helpers.cve_search_api":{CveSearchApi:[3,1,1,""]},"CveXplore.api.helpers.cve_search_api.CveSearchApi":{__init__:[3,2,1,""],__iter__:[3,2,1,""],__next__:[3,2,1,""],__repr__:[3,2,1,""],limit:[3,2,1,""],next:[3,2,1,""],query:[3,2,1,""],skip:[3,2,1,""],sort:[3,2,1,""]},"CveXplore.common":{cpe_converters:[4,0,0,"-"],data_source_connection:[4,0,0,"-"],generic_api:[4,0,0,"-"]},"CveXplore.common.cpe_converters":{from2to3CPE:[4,3,1,""],from3to2CPE:[4,3,1,""]},"CveXplore.common.data_source_connection":{DatasourceConnection:[4,1,1,""]},"CveXplore.common.data_source_connection.DatasourceConnection":{__init__:[4,2,1,""]},"CveXplore.common.generic_api":{GenericApi:[4,1,1,""]},"CveXplore.common.generic_api.GenericApi":{__init__:[4,2,1,""],__repr__:[4,2,1,""],call:[4,2,1,""],del_header_field:[4,2,1,""],headers:[4,4,1,""],reset_headers:[4,2,1,""],set_header_field:[4,2,1,""]},"CveXplore.database.connection":{mongo_db:[6,0,0,"-"]},"CveXplore.database.connection.mongo_db":{MongoDBConnection:[6,1,1,""]},"CveXplore.database.connection.mongo_db.MongoDBConnection":{__del__:[6,2,1,""],__init__:[6,2,1,""],__repr__:[6,2,1,""],disconnect:[6,2,1,""]},"CveXplore.database.helpers":{cvesearch_mongo_database:[6,0,0,"-"],generic_db:[6,0,0,"-"],specific_db:[6,0,0,"-"]},"CveXplore.database.helpers.cvesearch_mongo_database":{CveSearchCollection:[6,1,1,""],CveSearchCursor:[6,1,1,""]},"CveXplore.database.helpers.cvesearch_mongo_database.CveSearchCollection":{__init__:[6,2,1,""],__repr__:[6,2,1,""],find:[6,2,1,""]},"CveXplore.database.helpers.cvesearch_mongo_database.CveSearchCursor":{__init__:[6,2,1,""],__next__:[6,2,1,""],__repr__:[6,2,1,""],next:[6,2,1,""]},"CveXplore.database.helpers.generic_db":{GenericDatabaseFactory:[6,1,1,""],GenericDatabaseFieldsFunctions:[6,1,1,""]},"CveXplore.database.helpers.generic_db.GenericDatabaseFactory":{__init__:[6,2,1,""],__repr__:[6,2,1,""],get_by_id:[6,2,1,""]},"CveXplore.database.helpers.generic_db.GenericDatabaseFieldsFunctions":{__init__:[6,2,1,""],__repr__:[6,2,1,""],find:[6,2,1,""],search:[6,2,1,""]},"CveXplore.database.helpers.specific_db":{CvesDatabaseFunctions:[6,1,1,""]},"CveXplore.database.helpers.specific_db.CvesDatabaseFunctions":{__init__:[6,2,1,""],__repr__:[6,2,1,""],get_cves_for_vendor:[6,2,1,""]},"CveXplore.database.maintenance":{Config:[6,0,0,"-"],DownloadHandler:[6,0,0,"-"],LogHandler:[6,0,0,"-"],Sources_process:[6,0,0,"-"],content_handlers:[6,0,0,"-"],file_handlers:[6,0,0,"-"],main_updater:[6,0,0,"-"]},"CveXplore.database.maintenance.Config":{Configuration:[6,1,1,""]},"CveXplore.database.maintenance.DownloadHandler":{DownloadHandler:[6,1,1,""]},"CveXplore.database.maintenance.DownloadHandler.DownloadHandler":{__init__:[6,2,1,""],__repr__:[6,2,1,""],chunk_list:[6,2,1,""],get_session:[6,2,1,""],process_downloads:[6,2,1,""],store_file:[6,2,1,""]},"CveXplore.database.maintenance.LogHandler":{HelperLogger:[6,1,1,""],HostnameFilter:[6,1,1,""],UpdateHandler:[6,1,1,""]},"CveXplore.database.maintenance.LogHandler.HelperLogger":{__init__:[6,2,1,""],critical:[6,2,1,""],debug:[6,2,1,""],error:[6,2,1,""],info:[6,2,1,""],warning:[6,2,1,""]},"CveXplore.database.maintenance.LogHandler.HostnameFilter":{filter:[6,2,1,""]},"CveXplore.database.maintenance.LogHandler.UpdateHandler":{__init__:[6,2,1,""]},"CveXplore.database.maintenance.Sources_process":{CAPECDownloads:[6,1,1,""],CPEDownloads:[6,1,1,""],CVEDownloads:[6,1,1,""],CWEDownloads:[6,1,1,""],DatabaseIndexer:[6,1,1,""],MongoAddIndex:[6,1,1,""],MongoUniqueIndex:[6,1,1,""],VIADownloads:[6,1,1,""]},"CveXplore.database.maintenance.Sources_process.CAPECDownloads":{__init__:[6,2,1,""]},"CveXplore.database.maintenance.Sources_process.CPEDownloads":{__init__:[6,2,1,""]},"CveXplore.database.maintenance.Sources_process.CVEDownloads":{__init__:[6,2,1,""],get_cve_year_range:[6,2,1,""]},"CveXplore.database.maintenance.Sources_process.CWEDownloads":{__init__:[6,2,1,""]},"CveXplore.database.maintenance.Sources_process.DatabaseIndexer":{__init__:[6,2,1,""]},"CveXplore.database.maintenance.Sources_process.MongoAddIndex":{__getnewargs__:[6,2,1,""],__new__:[6,2,1,""],__repr__:[6,2,1,""],index:[6,5,1,""],name:[6,5,1,""]},"CveXplore.database.maintenance.Sources_process.MongoUniqueIndex":{__getnewargs__:[6,2,1,""],__new__:[6,2,1,""],__repr__:[6,2,1,""],index:[6,5,1,""],name:[6,5,1,""],unique:[6,5,1,""]},"CveXplore.database.maintenance.Sources_process.VIADownloads":{__init__:[6,2,1,""],file_to_queue:[6,2,1,""]},"CveXplore.database.maintenance.content_handlers":{CWEHandler:[6,1,1,""],CapecHandler:[6,1,1,""]},"CveXplore.database.maintenance.content_handlers.CWEHandler":{__init__:[6,2,1,""],characters:[6,2,1,""],endElement:[6,2,1,""],startElement:[6,2,1,""]},"CveXplore.database.maintenance.content_handlers.CapecHandler":{__init__:[6,2,1,""],characters:[6,2,1,""],endElement:[6,2,1,""],startElement:[6,2,1,""]},"CveXplore.database.maintenance.file_handlers":{JSONFileHandler:[6,1,1,""],XMLFileHandler:[6,1,1,""]},"CveXplore.database.maintenance.file_handlers.JSONFileHandler":{__init__:[6,2,1,""],__repr__:[6,2,1,""],file_to_queue:[6,2,1,""]},"CveXplore.database.maintenance.file_handlers.XMLFileHandler":{__init__:[6,2,1,""],__repr__:[6,2,1,""],process_item:[6,2,1,""]},"CveXplore.database.maintenance.main_updater":{MainUpdater:[6,1,1,""]},"CveXplore.database.maintenance.main_updater.MainUpdater":{__init__:[6,2,1,""],initialize:[6,2,1,""],update:[6,2,1,""]},"CveXplore.main":{CveXplore:[5,1,1,""]},"CveXplore.main.CveXplore":{__init__:[5,2,1,""],__repr__:[5,2,1,""],capec_by_cwe_id:[5,2,1,""],cve_by_id:[5,2,1,""],cves_for_cpe:[5,2,1,""],get_db_content_stats:[5,2,1,""],get_multi_store_entries:[5,2,1,""],get_single_store_entries:[5,2,1,""],get_single_store_entry:[5,2,1,""],last_cves:[5,2,1,""],version:[5,4,1,""]},"CveXplore.objects":{capec:[7,0,0,"-"],cpe:[7,0,0,"-"],cves:[7,0,0,"-"],cwe:[7,0,0,"-"],via4:[7,0,0,"-"]},"CveXplore.objects.capec":{Capec:[7,1,1,""]},"CveXplore.objects.capec.Capec":{__eq__:[7,2,1,""],__init__:[7,2,1,""],__ne__:[7,2,1,""],__repr__:[7,2,1,""],iter_related_capecs:[7,2,1,""],iter_related_weaknessess:[7,2,1,""],to_dict:[7,2,1,""]},"CveXplore.objects.cpe":{Cpe:[7,1,1,""]},"CveXplore.objects.cpe.Cpe":{__eq__:[7,2,1,""],__init__:[7,2,1,""],__ne__:[7,2,1,""],__repr__:[7,2,1,""],iter_cpe_names:[7,2,1,""],iter_cves_matching_cpe:[7,2,1,""],to_dict:[7,2,1,""]},"CveXplore.objects.cves":{Cves:[7,1,1,""]},"CveXplore.objects.cves.Cves":{__eq__:[7,2,1,""],__init__:[7,2,1,""],__ne__:[7,2,1,""],__repr__:[7,2,1,""],iter_capec:[7,2,1,""],iter_references:[7,2,1,""],iter_vuln_configurations:[7,2,1,""],to_dict:[7,2,1,""]},"CveXplore.objects.cwe":{Cwe:[7,1,1,""]},"CveXplore.objects.cwe.Cwe":{__eq__:[7,2,1,""],__init__:[7,2,1,""],__ne__:[7,2,1,""],__repr__:[7,2,1,""],iter_related_capecs:[7,2,1,""],iter_related_weaknessess:[7,2,1,""],to_dict:[7,2,1,""]},"CveXplore.objects.via4":{Via4:[7,1,1,""]},"CveXplore.objects.via4.Via4":{__eq__:[7,2,1,""],__init__:[7,2,1,""],__ne__:[7,2,1,""],__repr__:[7,2,1,""],to_dict:[7,2,1,""]},CveXplore:{main:[5,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","function","Python function"],"4":["py","property","Python property"],"5":["py","attribute","Python attribute"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:function","4":"py:property","5":"py:attribute"},terms:{"0":[1,2,6],"0001":5,"0018":[2,5],"010":2,"0387":2,"1":[1,2,6],"10":[2,5],"1191":2,"1193":2,"12":1,"122":2,"1220":2,"1224":2,"1244":2,"1252":2,"1257":2,"1262":2,"1268":2,"127":6,"1283":2,"13122":2,"1338":2,"14444":2,"14445":2,"14446":2,"15":5,"1574":2,"1574_010":2,"16344":2,"16345":2,"16346":2,"16347":2,"168":2,"17022":2,"17223":2,"192":2,"1935":2,"2":[1,2,4,5,6],"2009":[2,5],"2010":2,"2011":2,"2013":2,"2014":2,"2015":2,"2016":2,"2017":2,"2018":2,"2020":[2,5],"2354":2,"242":2,"26":1,"27017":[2,6],"276":2,"285":2,"2926":2,"3":[1,2,4,5,6],"3053":2,"32":2,"35":2,"3633":2,"3807":2,"4":1,"4031":2,"429":6,"434":2,"443":2,"5":2,"500":6,"502":6,"503":6,"504":6,"5735":2,"58":1,"6":1,"62":1,"693":2,"7":1,"721":2,"732":2,"77":2,"78":[2,5],"8":[1,2],"8154":2,"8273":2,"8302":2,"8327":2,"8421":2,"8476":2,"8500":2,"8540":2,"8626":2,"8658":2,"byte":6,"case":2,"class":[3,4,5,7],"default":[2,3,4,5,6,7],"do":[3,6],"function":[0,4,5,7],"import":2,"int":[2,3,5,6],"new":[3,5,6],"return":[2,3,4,5,6,7],"static":6,"true":6,"try":6,A:[2,5,6],And:2,As:2,At:2,By:[2,5,6,7],For:[1,5],If:[2,3,4,6],In:2,It:[2,3],Not:2,OR:2,Or:2,Such:2,The:[0,2,3,4,5,6],To:[2,6],__default_field:6,__del__:6,__eq__:7,__fields_map:6,__getnewargs__:6,__init__:[3,4,5,6,7],__iter__:3,__ne__:7,__new__:6,__next__:[3,6],__repr__:[3,4,5,6,7],_cl:6,abc:6,abil:2,abl:2,abov:2,access:[2,5],accord:5,acl:2,action:[2,6],add:4,addit:[2,6],address:[2,3,4],administr:2,advanc:6,agent:3,aim:2,alert:6,alia:6,all:[2,4,5,6],allow:5,alter:[2,6],ambigu:[2,3],amount:[3,5,6],an:[2,3,6],ani:[2,3,4,6],ansicolor:1,api:[2,5],api_connection_detail:[2,5],api_db:3,api_path:[2,3,4],apidatabasecollect:3,apidatabasesourc:3,app:2,append:2,appli:[2,6],applic:[2,6],appropri:6,ar:[2,5],arg:6,argument:[3,4,6],associ:2,assum:2,attack:2,attr:6,attribut:[2,6],authent:2,author:2,autofil:4,automat:2,avail:[0,2],backend:6,backoff_factor:6,base:[2,3,4,5,6,7],been:6,befor:[2,3],behaviour:3,being:2,besid:2,better:2,binari:2,bit:6,bodi:4,bool:[4,7],both:2,brute:2,build:2,busi:2,call:[2,4,6],caller:4,can:[2,3,4,6],capabl:2,capec:[2,5,6],capec_by_cwe_id:5,capecdownload:6,capechandl:6,captur:2,ch:6,chang:5,charact:6,check:[2,5],choic:5,chunk:6,chunk_list:6,cli:0,click:[0,1,2],collect:[3,4,5,6,7],collnam:3,color:6,come:6,command:[0,2,6],common:[2,3,6,7],commun:4,compon:2,compromis:2,config:6,configur:[3,4,5,7],connect:[2,5,7],consist:5,constrain:2,contain:[5,6],content_handl:6,content_typ:6,contenthandl:6,contigu:6,control:2,convert:[2,6,7],copi:6,core:2,could:2,count:5,cpe2:4,cpe:[2,5,6],cpe_convert:4,cpe_nam:7,cpe_str:5,cpedownload:6,creat:[2,3,4,5,6,7],creation:6,credenti:2,critic:6,current:[0,4,5,7],cursor:[3,6],custom:6,custon:6,cve:[2,5,6],cve_by_id:5,cve_id:5,cve_search:6,cve_search_api:3,cvedb:[5,6],cvedownload:6,cves_for_cp:5,cvesdatabasefunct:6,cvesearch_mongo_databas:6,cvesearchapi:3,cvesearchcollect:[3,6],cvesearchcursor:6,cvexplor:[0,1,2,3,4,5,6,7],cvss:[2,6],cvx:2,cwe:[2,5,6],cwe_id:5,cwedownload:6,cwehandl:6,dashboard:6,data:[3,5,6,7],data_source_connect:[4,6,7],databas:[3,4,5,7],databaseindex:6,datasourc:6,datasourceconnect:[4,6,7],dateutil:1,db_collect:3,debug:6,debugg:2,deem:6,defin:[4,7],del_header_field:4,delet:4,deni:2,deriv:6,descend:[2,3,6],descript:2,detail:[2,5],determin:6,develop:0,dict:[3,4,5,6,7],dict_filt:5,dictionari:[2,5,6,7],dicttoxml:1,differ:[2,3],dir:6,direct:[2,3],directli:2,directori:6,disabl:2,disconnect:6,discover:2,docker:2,document:[0,5,7],done:2,doubl:4,down:2,downloadhandl:6,drill:2,e:[3,4,5,6],each:[2,6],easili:2,either:[2,3],element:[2,6],end:[4,6],endel:6,endpoint:[2,3,5],enter:5,entir:[2,7],entiti:6,entri:6,entry_id:2,entry_nam:2,entry_typ:5,environ:2,eq:2,equip:2,error:6,establish:[5,6],event:6,everi:[2,6],exampl:[2,5],exc_info:6,except:6,execut:2,execution_flow:2,expect:2,experi:2,exploit:2,explor:2,expos:2,extend:6,extern:6,fail:2,fals:[4,6,7],feed_typ:6,feedback:6,fetch:6,field:[2,3,4,5,6,7],file_handl:6,file_to_queu:6,file_tupl:6,filenam:6,filter:[3,5,6],find:[2,3,6],find_on:3,flow:2,follow:[1,2],forc:2,forgotten:2,form:2,format:[4,6],framework:2,free:[3,4],fresh:6,from2to3cp:4,from3to2cp:4,from:[2,5,6,7],full:6,fulli:2,further:[2,6],fuzz:2,g:[3,4,5,6],garbag:6,gener:7,generic_api:[3,4],generic_db:6,genericapi:[3,4],genericdatabasefactori:6,genericdatabasefieldsfunct:6,get:[2,4,6],get_by_id:6,get_cve_year_rang:6,get_cves_for_vendor:[2,6],get_db_content_stat:5,get_multi_store_entri:[2,5],get_sess:6,get_single_store_entri:[2,5],github:2,given:[2,3,6],go:2,grant:2,guess:2,gui:[2,6],ha:[0,1,2,6],handl:[3,4,6],have:[2,6],header:[4,6],hell:6,helper:2,helperlogg:6,high:2,higher:2,hijack:2,hold:6,host:[2,3,4,6],hostnam:6,hostnamefilt:6,houston:6,howev:6,http:[2,3,4],hyphen:4,id:[2,5,6],identifi:2,ijson:1,imposs:2,impun:2,inappropri:2,index:[2,6],individu:[2,3,4],info:6,inform:[2,6],init:6,initi:[2,6],input:2,insert:[2,6],instanc:[2,3,5,6],instanti:6,instead:[6,7],intend:2,interact:2,interest:6,interpret:0,inventori:2,invok:2,ip:[3,4],item:6,iter:[2,3,7],iter_capec:[2,7],iter_cpe_nam:7,iter_cves_matching_cp:7,iter_refer:7,iter_related_capec:7,iter_related_weaknessess:7,iter_vuln_configur:7,json:6,jsonfilehandl:6,just:[2,6],keyword:6,kwarg:[6,7],last:5,last_cv:5,len:2,let:2,level:[2,6],librari:2,like:2,limit:[0,2,3,5,6],line:[0,2,5],link:2,list:[2,5,6],loa:2,localhost:[2,3,6],locat:6,logger:6,loghandl:6,logic:2,lst:6,machin:2,made:[5,7],magenta:6,mai:[2,6],main:2,main_updat:6,mainten:2,maintenainc:6,mainupdat:6,major:6,make:3,manag:[2,6],manner:2,map:2,mark:2,match:[5,7],mechan:2,messag:6,method:[2,3,4,5,6,7],microsoft:[2,5,6],might:2,mimic:3,mitig:2,mitr:2,mode:6,modifi:[5,6],modul:2,mongo_db:6,mongoaddindex:6,mongocli:6,mongodb:[2,3,5],mongodb_connection_detail:[2,5],mongodbconnect:[3,6],mongouniqueindex:6,more:2,msg:6,multipl:[2,5],must:[2,6],myhead:4,myloc:2,n:6,name:[2,3,4,6],namespac:6,navig:2,need:[2,3,4,5,6],network:2,next:[3,6],nice:6,non:[3,6],none:[3,4,5,6],normal:1,note:2,notif:6,now:2,number:[2,5,6],o:5,obj:[3,4],object:[2,3,4,5,6],objectifi:5,obtain:2,occur:2,onc:2,one:2,ones:2,onli:[2,6],onward:2,oper:[1,2],option:6,order:[2,3],org:2,origin:2,os:2,other:[2,5,6,7],otherwis:[2,6],over:[2,7],packag:5,packet:2,page:2,panda:1,paramet:[2,3,4,5,6,7],pars:6,parser:6,particular:2,particularli:2,pass:6,path:3,per:[5,6],perfect:2,perform:[2,3,5,6],permiss:2,phase:2,physic:2,pickl:6,pip:2,place:6,plain:6,pleas:[2,5],point:4,port:[2,3,4,6],possibl:2,post:[2,4,5],pprint:2,prefix:6,prerequisit:2,print:2,privileg:2,problem:6,process_download:6,process_item:6,product:[2,7],progress:2,properli:2,properti:[4,5],protocol:[2,3,4],provid:[2,3,5,6],proxi:[3,4],put:[4,6],pymongo:[1,2,3,5,6],pypi:2,python:[0,1,6],queri:[3,4,5,6],queue:6,quot:4,rather:2,raw:[2,6],re:2,reachabl:3,receiv:6,record:[2,3,6],red:6,refer:[3,6,7],regex:6,relat:[2,5,6,7],related_capec:2,related_weak:2,report:6,repres:5,represent:[3,4,5,6,7],request:[1,2,3,4,6],reset:4,reset_head:4,resourc:[2,3,4],respons:6,response_cont:6,restrict:2,result:[2,3,4,5,6],retri:6,retriev:5,role:2,root:3,run:[2,3,6],s:[0,2,3,4,5,6,7],same:[2,6],sax:6,script:6,search:[2,5,6,7],section:2,secur:2,self:[4,6,7],sensit:2,serial:2,serv:[4,6],servicesfil:2,session:6,set:[2,3,4],set_header_field:4,setuptool:1,sever:6,shall:6,shell:6,should:[4,5,6],signal:6,simpl:6,singl:[2,5,6],site:[2,6],size:6,skip:[2,3],sniffer:2,so:[2,3,6],softwar:2,solut:2,some:2,somehow:2,sort:[2,3,6],sourc:[2,3,5,7],sources_process:6,sp1:5,specif:[3,5],specifi:[2,6],specific_db:6,spider:2,split:6,start:6,startel:6,stat:5,state:2,statist:5,status_forcelist:6,step:2,still:[0,2],store:[5,6],store_fil:6,str:[3,4,5,6,7],string:[3,4,5,6,7],subsect:2,subsequ:6,success:6,summari:2,support:[2,5,6],suppos:2,survei:2,system:2,t1574:2,talk:[2,3],target:2,task:6,taxonomi:2,techniqu:2,th:6,than:2,thei:[2,6],them:[2,6],thi:[2,3,6,7],thing:2,thorni:6,those:2,thread:6,thu:2,time:5,to_dict:[2,7],togeth:2,tool:2,toward:[4,6],tqdm:1,traffic:2,transfer:6,transform:4,tri:2,tupl:[3,4,5,6],two:2,type:[2,3,4,5,6,7],typical_sever:2,under:0,uniform:6,uniqu:6,updatehandl:6,upon:2,uri:6,url:[2,6],urllib3:1,us:[2,3,4,6],user:[2,3],user_ag:[3,4],valid:2,valu:[3,4,6,7],variou:2,vendor:[2,6],version:[2,3,5],via4:[2,5,6],via:[2,6],viadownload:6,visual:6,vuln_prod_search:7,vulner:7,vulnerable_configur:7,wai:[2,3,6],warn:6,we:6,weak:[2,7],web:2,when:[2,3,4,6],where:6,whether:4,which:[2,5,6],white:6,windows_7:5,within:4,without:2,work:6,worker:6,would:[2,3,6],written:6,xmlfilehandl:6,year:6,yellow:6,yield:[2,6],you:[2,3,4,5,6],your:2,zip:6},titles:["General","Dependencies","Dependencies","API","Common","Core","Database","Objects"],titleterms:{"class":6,"function":[2,6],api:[3,4],capec:7,cli:2,collect:2,common:4,configur:6,connect:[3,4,6],content:6,convert:4,core:5,cpe:[4,7],cve:[3,7],cwe:7,data:[2,4],databas:[2,6],db:6,depend:[1,2],document:2,download:6,file:6,format:2,free:2,gener:[0,2,4,6],handler:6,helper:[3,6],indic:2,instal:2,instanti:2,local:2,log:6,main:[5,6],mainten:6,mongo:6,mongodb:6,object:7,packag:2,popul:2,process:6,queri:2,search:3,sourc:[4,6],specif:[2,6],tabl:2,tool:4,updat:[2,6],usag:2,via4:7,xml:6}})