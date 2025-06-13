from datetime import datetime
import time, sys, os, wx, re, requests, urllib3   
import Global_var
import database
from TOTS3UploadLibrary.upload import UploadFile

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def log_exception_details(e,docpath):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    Error_Message = str(e)
    Line_No = exc_tb.tb_lineno
    Exception_Type = exc_type.__name__
    Function_name = exc_tb.tb_frame.f_code.co_name
    File_Name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    Source_Name = str(Global_var.source_name)
    Error_Final = f"Error_Message: {Error_Message} | Function: {Function_name} | Exception_Type: {Exception_Type} | File_Name: {File_Name} | Line_No: {Line_No}"
    print(Error_Final)
    if 'timed out' not in str(e):
        Error_Log(Error_Final, Function_name, Source_Name, docpath)
    time.sleep(10)

def print_exception_details(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    Exception_Type = exc_type.__name__
    Line_No = exc_tb.tb_lineno
    Error_Message = str(e)
    Function_name = exc_tb.tb_frame.f_code.co_name
    File_Name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    Error_Final = f"Error_Message: {Error_Message} | Function: {Function_name} | Exception_Type: {Exception_Type} | File_Name: {File_Name} | Line_No: {Line_No}"
    print(Error_Final)
    time.sleep(10)
    
def Error_Log(Error, Function_name, Source_Name, doc_path):
    while True:
        if Global_var.errorcount > 100:
            print(f"Error occurred more than 100 times.\n{Error}")
            wx.MessageBox("Error occurred more than 100 times..!!\n\nPlease give it for maintenance..!!\n\nERROR: " + str(Error), str(Global_var.source_name), wx.OK | wx.ICON_ERROR)

        connection = database.DB_Connection()
        mycursor = connection.cursor()
        thread_id = connection.thread_id()
        sql = "INSERT INTO errorlog_tbl(Error_Message,Function_Name,Exe_Name,doc_path) VALUES(%s,%s,%s,%s)"
        val = (str(Error), str(Function_name), str(Source_Name), str(doc_path))
        try:
            mycursor.execute(sql, val)
            connection.commit()
            mycursor.close()
            connection.close()
            Global_var.errorcount += 1
            print("Code Reached On insert_in_Local")
            break
        except Exception as e:
            database.kill_query(thread_id)
            print_exception_details(e)

def check_Duplication(segfield):
    while True:
        try:
            print("Code On check_Duplication")
            connection = database.DB_Connection()
            mycursor = connection.cursor()
            thread_id = connection.thread_id()
            if segfield[13] != '' and segfield[24] != '' and segfield[7] != '':
                commandText = "SELECT Posting_Id FROM " + Global_var.local_table_name + " WHERE tender_notice_no = %s AND country = %s AND doc_last = %s LIMIT 1"
                params = (segfield[13], segfield[7], segfield[24])
            elif segfield[13] != "" and segfield[7] != "":
                commandText = "SELECT Posting_Id FROM " + Global_var.local_table_name + " WHERE tender_notice_no = %s AND country = %s LIMIT 1"
                params = (segfield[13], segfield[7])
            elif segfield[19] != "" and segfield[24] != "" and segfield[7] != "":
                commandText = "SELECT Posting_Id FROM " + Global_var.local_table_name + " WHERE short_desc = %s AND doc_last = %s AND country = %s LIMIT 1"
                params = (segfield[19], segfield[24], segfield[7])
            else:
                commandText = "SELECT Posting_Id FROM " + Global_var.local_table_name + " WHERE short_desc = %s AND country = %s LIMIT 1"
                params = (segfield[19], segfield[7])
            mycursor.execute(commandText, params)
            results = mycursor.fetchall()
            mycursor.close()
            connection.close()
            print("Code Reached On check_Duplication")
            if len(results) > 0:
                # print('Duplicate Tender')
                # Global_var.duplicate += 1
                return False
            else:
                return True
        except Exception as e:
            database.kill_query(thread_id)
            log_exception_details(e,str(segfield[28]))

def create_html_file(segField, html_doc):
    while True:
        try:
            print("create_html_file...")
            exe_number = str(Global_var.exe_no) 
            Current_dateTime = datetime.now().strftime("%Y%m%d%H%M%S%f")
            Fileid = "".join([exe_number, Current_dateTime])
            Final_Doc = """
            <html>
            <head>
                <meta content="text/html; charset=utf-8" http-equiv="Content-Type" />
                <title>Tender Document</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #f5f5f5;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        padding: 20px;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                    }}
                    .source-link {{
                        margin-top: 20px;
                        padding-top: 15px;
                        border-top: 1px solid #eee;
                        font-size: 16px;
                    }}
                    .source-link a {{
                        color: #007BFF;
                        text-decoration: none;
                        font-weight: bold;
                    }}
                    .source-link a:hover {{
                        text-decoration: underline;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    {html_doc}
                    <div class="source-link">
                        <span>Click Here For Main Source Page:</span><br/>
                        <a href="{url}" target="_blank">Click Here</a>
                    </div>
                </div>
            </body>
            </html>
            """.format(html_doc=html_doc, url=segField[28])
            # Final_Doc = "<HTML><head><meta content=\"text/html; charset=utf-8\" http-equiv=\"Content-Type\" /><title>Tender Document</title></head><BODY><Blockquote style='border:1px solid; padding:10px;'>"+html_doc+"<td style=\"padding:7px;\">Click Here For Main Source Page </td><td style=\"padding:7px;\"><a href='"+ segField[28] +"' target=\"_blank\">Click here for main source page</a></td></Blockquote></BODY></HTML>"
            if Global_var.file_upload == '1':
                filename = upload_to_AWS(Fileid,Final_Doc,segField)
            else:
                filename = upload_to_Zdrive(segField,Fileid,Final_Doc)
            return Fileid,filename
        except Exception as e:
            log_exception_details(e)

def upload_to_Zdrive(segField,Fileid,Final_Doc):
    while True:
        try:
            filename =  Fileid + ".html"
            # filepath = "D:\\test\\" + filename
            filepath = "Z:\\" + filename
            file1 = open(filepath , "w" , encoding='utf-8')
            file1.write(Final_Doc)
            file1.close()
            return filename
        except Exception as e:
            log_exception_details(e,str(filename))

def upload_to_AWS(Fileid,Final_Doc,segField):
    while True:
        try:
            current_directory = 'C:\\Additional_Docs\\'
            final_directory = os.path.join(current_directory,segField[31])
            if not os.path.exists(final_directory):
                os.makedirs(final_directory)
            for filename in os.listdir(final_directory):
                try:
                    os.unlink(os.path.join(final_directory, filename))
                except: pass
            filename = Fileid + ".html"
            filepath =  final_directory +'\\'+ filename
            file1 = open(filepath, "w", encoding='utf-8')
            file1.write(str(Final_Doc))
            file1.close()
            upload_to_s3(filepath,segField,'')
            for filename in os.listdir(final_directory):
                try:
                    os.unlink(os.path.join(final_directory, filename))
                except: pass
            return filename
        except Exception as e:
            log_exception_details(e,str(filename))

def AdditionalDocs(segField,Fileid):
    while True:
        try:
            all_link = []
            attach_docs = segField[44]
            if (attach_docs != ""):
                doclinks = attach_docs.split(',')
                all_link = doclinks
                time.sleep(2)

            additional_docname = ""
            # SegFeild[44] = ""
            
            current_directory = 'C:\\Additional_Docs\\'
            final_directory = os.path.join(current_directory,Global_var.source_name)
            if not os.path.exists(final_directory):
                os.makedirs(final_directory)
                
            for link in all_link:
                name_n_file = link                    
                down_filename = Download_AdditionalDocs(name_n_file, Fileid,final_directory,segField)
                if (down_filename != ""):
                    filepath = "C:\\Additional_Docs\\" +Global_var.source_name+'\\'+ down_filename
                    upload_to_s3(filepath,segField,'additional_docs')
                    if (additional_docname == ""):
                        additional_docname = down_filename
                    else:
                        additional_docname += "," + down_filename
                
                if (len(additional_docname) > 3800):
                    path = 'toomany_additional_docs.txt'
                    my_file = open(path, "w")
                    my_file.writelines(segField[28])        
                    my_file.close()
                    break   

            clear_files = os.path.join(current_directory,Global_var.source_name)
            for filename in os.listdir(clear_files):
                os.unlink(os.path.join(clear_files, filename))
            print("Code Reached On Additional Docs")
            
            return additional_docname
        except Exception as e:
            log_exception_details(e,str(segField[28]))
           
def Download_AdditionalDocs(name_n_file, Fileid,final_directory,segField):
    # tilde_count = name_n_file.count('~')
    # if tilde_count > 1:
    #     urlnameArr = name_n_file.rsplit('~', 1) 
    # else:
    urlnameArr = name_n_file.split('~')
        
    if (urlnameArr[0].strip() == "" or len(urlnameArr) == 1):
        return ""
    
    filename = Fileid + "-" + urlnameArr[0]
    filename = re.sub('[^0-9a-zA-Z .\-_]+', ' ', filename)
    filename = re.sub(r'\s+', ' ', filename)
    filename = filename.replace(" ", "-")
    filename = filename.replace("--", "-")
    
    url = urlnameArr[1]
    d = 0
    while (d <= 5):
        try:
            # current_directory = 'C:\\Additional_Docs\\'
            # final_directory = os.path.join(current_directory,Global_var.source_name)
            # if not os.path.exists(final_directory):
            #     os.makedirs(final_directory)
            file_path = os.path.join(final_directory, filename)
            try:
                # response = requests.get(url, verify=certifi.where())
                response = requests.get(url, timeout=60, verify=False)

                response.raise_for_status()

                print("Success:", response.status_code)

                with open(file_path, 'wb') as f:
                    f.write(response.content)

                if not os.path.exists(file_path):
                    filename = '' # if flile not exist or not downloaded
                else:
                    fileSize = os.path.getsize(file_path) # check file size if <= 0 then return = ''
                    if (fileSize <= 0):
                        filename = ''
                d = 10
            except requests.exceptions.SSLError as e:
                print(f"SSL error occurred: {e}")
                return ""
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                return ""

        except Exception as e:
            log_exception_details(e,url)
            d+=1
            time.sleep(5)
            filename = ""    
    return filename

def upload_to_s3(filepath,segfield_AWS,directory):
    loop = 0
    while loop == 0:
        try:
            result = UploadFile(filepath,directory)
            if result == True:
                loop = 1 # success
            else:
                print("Error while uploading file on S3 Bucket..!")
                time.sleep(10)
        except Exception as e:
            log_exception_details(e,str(segfield_AWS[28]))
    
def insert_in_local(segfield_local,Fileid):
    while True:
        connection = database.DB_Connection()
        mycursor = connection.cursor()
        thread_id = connection.thread_id()
        # local_table = str(Global_var.local_table_name)
        # entry_date = datetime.now().strftime("%Y-%m-%d")
        sql = "INSERT INTO " + Global_var.local_table_name + " (Tender_ID,Country,tender_notice_no,short_desc,doc_last,tender_doc_file,source)VALUES(%s,%s,%s,%s,%s,%s,%s)"
        val = (str(Fileid),str(segfield_local[7]),str(segfield_local[13]),str(segfield_local[19]),str(segfield_local[24]),str(segfield_local[28]),str(segfield_local[31]))
        try:
            mycursor.execute(sql, val)
            connection.commit()
            mycursor.close()
            connection.close()
            print("Code Reached On insert_in_Local")
            break
        except Exception as e:
            database.kill_query(thread_id)
            log_exception_details(e,str(segfield_local[28]))
            
def insert_l2l_tbl(segfield_l2l,Fileid,Filename):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    added_on = current_datetime
    select_date = current_datetime
    quality_addeddate = current_datetime
    search_id = "1"
    cpv_userid = ""
    quality_id = '1'
    selector_id = ''
    Col1 = str(Global_var.Col1)
    Col2 = ''
    Col3 = ''
    Col4 = ''
    Col5 = ''
    file_name = "D:\\Tide\\DocData\\" + str(Filename)
    file_id = Fileid
    
    if segfield_l2l[7] == "" or segfield_l2l[12] == "" or segfield_l2l[19] == "" or segfield_l2l[24] == "":
        Global_var.dms_entrynotice_tblcompulsary_qc = "1"
        sql = "INSERT INTO qctenders_tbl (Source,tender_notice_no,short_desc,doc_last,Maj_Org,Address,doc_path,Country) VALUES(%s,%s,%s,%s,%s,%s,%s,%s) "
        val = (str(segfield_l2l[31]), str(segfield_l2l[13]), str(segfield_l2l[19]), str(segfield_l2l[24]), str(segfield_l2l[12]), str(segfield_l2l[2]), str(Filename), str(segfield_l2l[7]))
        while True:
            try:
                connection = database.DB_Connection()
                mycursor = connection.cursor()
                thread_id = connection.thread_id()
                mycursor.execute(sql , val)
                connection.commit()
                mycursor.close()
                connection.close()
                print("Code Reached On QCTenders")
                Global_var.QC_Tender += 1
                break
            except Exception as e:
                database.kill_query(thread_id)
                log_exception_details(e,str(segfield_l2l[28]))
    else:
        Global_var.dms_entrynotice_tblcompulsary_qc = "2"

    sql = "INSERT INTO l2l_tenders_tbl (notice_no,file_id,purchaser_name,deadline,country,description,purchaser_address,purchaser_email,purchaser_url,purchaser_emd,purchaser_value,financier,deadline_two,tender_details,ncbicb,status,added_on,search_id,cpv_value,cpv_userid,quality_status,quality_id,quality_addeddate,source,tender_doc_file,Col1,Col2,Col3,Col4,Col5,file_name,user_id,status_download_id,save_status,selector_id,select_date,datatype,compulsary_qc,notice_type,cqc_status,DocCost,DocLastDate,is_english,currency,sector,project_location,set_aside,other_details,file_upload,file_name_additional,DocStartDate,published_datetime,opening_date) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    val = (str(segfield_l2l[13]), file_id, str(segfield_l2l[12]), str(segfield_l2l[24]), str(segfield_l2l[7]), str(segfield_l2l[19]), str(segfield_l2l[2]), str(segfield_l2l[1]), str(segfield_l2l[8]), str(segfield_l2l[26]), str(segfield_l2l[20]), str(segfield_l2l[27]), str(segfield_l2l[24]), str(segfield_l2l[18]), Global_var.ncb_icb, Global_var.dms_entrynotice_tblstatus, str(added_on), search_id, str(segfield_l2l[36]),cpv_userid, Global_var.dms_entrynotice_tblquality_status, quality_id, str(quality_addeddate), str(segfield_l2l[31]), str(segfield_l2l[28]), Col1, Col2, Col3, Col4, Col5, file_name, Global_var.dms_downloadfiles_tbluser_id, Global_var.dms_downloadfiles_tblstatus, Global_var.dms_downloadfiles_tblsave_status, selector_id, str(select_date), Global_var.dms_downloadfiles_tbldatatype, Global_var.dms_entrynotice_tblcompulsary_qc, Global_var.dms_entrynotice_tblnotice_type, Global_var.dms_entrynotice_tbl_cqc_status, str(segfield_l2l[22]), str(segfield_l2l[41]), Global_var.is_english, str(segfield_l2l[21]), segfield_l2l[29], segfield_l2l[42], segfield_l2l[43],str(segfield_l2l[46]), Global_var.file_upload, str(segfield_l2l[44]), str(segfield_l2l[23]), str(segfield_l2l[47]), str(segfield_l2l[25]))
    while True:
        try:
            connection = database.DB_Connection()
            mycursor = connection.cursor()
            thread_id = connection.thread_id()
            mycursor.execute(sql, val)
            connection.commit()
            mycursor.close()
            connection.close()
            print("Code Reached On insert_L2L")
            print('😍 Live Tender 😍')
            Global_var.inserted += 1
            break
        except Exception as e:
            database.kill_query(thread_id)
            log_exception_details(e,str(segfield_l2l[28]))