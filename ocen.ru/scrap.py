from selenium.webdriver.common.by import By
from datetime import datetime
from insert_on_database import *
import os, sys, time, re, wx ,html
import Global_var

app = wx.App()

def remove_html(text):
    pattern = re.compile('<.*?>')
    result = re.sub(pattern, '',str(text))
    return result

def scrap(link_list,driver):
    scrap_error = True
    while scrap_error:
        try:
            for i in link_list:
                driver.get(i['link'])

                # check result table
                getAttempt = 0
                while True:
                    varify_data = driver.find_elements(By.XPATH,'/html/body/table[3]/tbody/tr[2]/td[3]/table/tbody/tr[2]/td')
                    if len(varify_data) == 0:
                        getAttempt+=1
                        time.sleep(2)
                        if getAttempt > 5:
                            driver.get(i['link'])
                        continue
                    else:
                        break

                segField = [''] * 50
                time.sleep(1)

                # -----------------------------------HTMLDOCUMENT----------------------------------
                html_doc = ''
                htmlpage = driver.find_element(By.XPATH, '/html/body/table[3]/tbody/tr[2]/td[3]/table/tbody/tr[2]/td/table/tbody/tr[3]/td').get_attribute('outerHTML')
                html_doc = re.sub(r"\s+", " ", htmlpage)
                time.sleep(2)

                # while '<img' in html_doc:
                #     remove = html_doc.partition("<img ")[2].partition('">')[0]
                #     html_doc = html_doc.replace(f'<img {str(remove)}">','')

                # -----------------------------------email_address-----------------------------------
                if 'Адрес электронной почты</td>' in html_doc:
                    segField[1] = remove_html(html_doc.partition('Адрес электронной почты</td>')[2].partition('</td>')[0]).strip()
                else:
                    segField[1] = remove_html(html_doc.partition('Адрес электронной почты:</td>')[2].partition('</td>')[0]).strip()

                # -----------------------------------address-----------------------------------
                if 'Место нахождения</td>' in html_doc:
                    Location = remove_html(html_doc.partition('Место нахождения</td>')[2].partition('</td>')[0]).strip()
                    Fax = remove_html(html_doc.partition('Факс</td>')[2].partition('</td>')[0]).strip()
                    Contact_person = remove_html(html_doc.partition('Ответственное должностное лицо</td>')[2].partition('</td>')[0]).strip()
                    Tele = remove_html(html_doc.partition('Номер контактного телефона</td>')[2].partition('</td>')[0]).strip()
                    segField[2] = f"Место нахождения: {Location}<br>\nФакс: {Fax}<br>\nОтветственное должностное лицо: {Contact_person}<br>\nНомер контактного телефона: {Tele}"
                else:
                    Location = remove_html(html_doc.partition('Место нахождения:</td>')[2].partition('</td>')[0]).strip()
                    # Fax = remove_html(html_doc.partition('Факс:</td>')[2].partition('</td>')[0]).strip()
                    Contact_person = remove_html(html_doc.partition('Ф.И.О:</td>')[2].partition('</td>')[0]).strip()
                    Tele = remove_html(html_doc.partition('Номер контактного телефона:</td>')[2].partition('</td>')[0]).strip()
                    segField[2] = f"Место нахождения: {Location}<br>\nФакс: {Fax}<br>\nФ.И.О: {Contact_person}<br>\nНомер контактного телефона: {Tele}"

                # -----------------------------------Country----------------------------------- 
                segField[7] = Global_var.country_code

                # -----------------------------------URL*-----------------------------------
                segField[8] = 'https://www.ocenchik.ru/tender/?lim=0' 

                # -----------------------------------Maj_Org-----------------------------------
                if 'Организация, осуществляющая размещение</td>' in html_doc:
                    segField[12] = remove_html(html_doc.partition('Организация, осуществляющая размещение</td>')[2].partition('</td>')[0]).strip()
                else:
                    segField[12] = remove_html(html_doc.partition('Наименование организации:</td>')[2].partition('</td>')[0]).strip()

                # -----------------------------------tender_notice_no-----------------------------------
                if 'Номер извещения</td>' in html_doc:
                    segField[13] = remove_html(html_doc.partition('Номер извещения</td>')[2].partition('</td>')[0]).strip()
                else:
                    segField[13] = remove_html(html_doc.partition('Номер извещения:</td>')[2].partition('</td>')[0]).strip()

                # -----------------------------------notice_type-----------------------------------
                segField[14] = Global_var.dms_entrynotice_tblnotice_type

                # -----------------------------------MFA-----------------------------------
                segField[17] = "0"

                # -----------------------------------short_desc-----------------------------------
                segField[19] = i['short_desc']

                # -----------------------------------tenders_details-----------------------------------   
                segField[18] = segField[19]

                # -----------------------------------value-----------------------------------
                value = i['Contract_price'].replace('руб.', '').replace(' ', '').strip()
                if 'неуказана' in value:
                    segField[20] = ''
                else:segField[20] = value
                if segField[20] != '':
                    segField[21] = 'RUB'

                # -----------------------------------Deadline-----------------------------------
                segField[24] = i['deadline']
                    
                # -----------------------------------Docpath-----------------------------------  
                segField[28] = driver.current_url

                # -----------------------------------Financier-----------------------------------
                segField[27] = "0"

                # -----------------------------------source-----------------------------------
                segField[31] = Global_var.source_name

                # -----------------------------------project_location-----------------------------------
                segField[42] = segField[7]

                segField = validate_segField(segField)
                for SegIndex, segfield_data in enumerate(segField):
                    print(f'{SegIndex} : {segfield_data}')

                print('-----------------------------------!!!scrap done!!!-----------------------------------')

                check_date_and_insert(segField, html_doc)

                Global_var.Total += 1 
                print(
                f" Total: {Global_var.Total} | Duplicate: {Global_var.duplicate} | Expired: {Global_var.expired} | "
                f"Inserted: {Global_var.inserted} | Deadline Not Given: {Global_var.deadline_Not_given} | "
                f"Skipped: {Global_var.skipped} | QC Tenders: {Global_var.QC_Tender}\n"
                )                
            scrap_error = False           
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",exc_tb.tb_lineno)      
    wx.MessageBox(f'Total: {Global_var.Total}\nDeadline Not given: {Global_var.deadline_Not_given}\nSkipped: {Global_var.skipped}\nDuplicate: {Global_var.duplicate}\nInserted: {Global_var.inserted}\nExpired: {Global_var.expired}\nQC Tenders: {Global_var.QC_Tender}', 'ocenchik.ru', wx.OK | wx.ICON_INFORMATION)
    driver.close()
    sys.exit()

def check_date_and_insert(segField, html_doc):     
    deadline = (segField[24])
    curdate = datetime.now()
    curdate_str = curdate.strftime("%Y-%m-%d")
    try:
        if deadline != '':
            datetime_object_deadline = datetime.strptime(deadline, '%Y-%m-%d')
            datetime_object_curdate = datetime.strptime(curdate_str, '%Y-%m-%d')
            timedelta_obj = datetime_object_deadline - datetime_object_curdate
            day = timedelta_obj.days
            is_new = False
            if day > 0:
                is_new = check_Duplication(segField)
                if is_new :
                    Fileid,Filename = create_html_file(segField, html_doc)
                    # if segField[44] != '':
                    #     adddoc_Filename = AdditionalDocs(segField,Fileid) # Additional Doc comment becuz Document size are too large like 80MB 300MB
                    #     if adddoc_Filename != '':
                    #         segField[44] = adddoc_Filename 
                    insert_in_local(segField,Fileid)
                    insert_l2l_tbl(segField,Fileid,Filename)
                else:
                    print('Duplicate Tender')
                    Global_var.duplicate += 1    
            else:
                print("Expired Tender")
                Global_var.expired += 1
        else:
            print("Deadline Not Given")
            Global_var.deadline_Not_given += 1
    except Exception as e:
        print(e)

def validate_segField(segfields):
    for i in range(len(segfields)):
        segfields[i] = html.unescape(segfields[i])
        # segfields[i] = segfields[i].replace("'", "''")
        segfields[i] = segfields[i].strip()
    
    for i in range(len(segfields)):
        if len(segfields[i]) > 1500:
            segfields[i] = segfields[i][:1500] + "..."
        if segfields[i] == "":
            segfields[i] = ""
            
    if segfields[18] == '':
        segfields[18] = segfields[19]
        
    if len(segfields[19]) > 200:
        if segfields[19].lower() not in segfields[18].lower():
            segfields[18] = segfields[19]+'<br>\n'+segfields[18]
        segfields[19] = segfields[19][:200].strip() + "..."
    
    if len(segfields[2]) > 500:
        segfields[2] = segfields[2][:500].strip() + "..."
    return segfields            