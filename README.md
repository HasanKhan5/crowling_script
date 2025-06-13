||  Tenders Web Scraper  ||

This project is a web scraping automation script developed in Python to extract tender information from ocenchik.ru, a Russian tender listing website. The script navigates through multiple pages, extracts relevant tender details, and stores the data into a MySQL database, along with optional document uploads to AWS S3.


Features
* Calendar-based scraping date input using wxPython

* Crawls through paginated tender listings

* Extracts detailed tender info including:

  Tender notice number

  Organization name

  Contact info

  Description, value, currency

  Deadlines and URLs

* Validates and deduplicates data

* Saves to both local and l2l_tenders_tbl tables in MySQL

* Uploads tender documents and additional attachments to AWS S3

* Gracefully handles site CAPTCHA, retries, and Cloudflare delays
  

Project Structure

* MainCalender.py	                            

* collectlink.py	                 

* scrap.py	                           

* insert_on_database.py	            

* database.py	                     

* Global_var.py	           


Technologies Used

^ Python 3

^ Selenium – for browser automation

^ wxPython – GUI for date selection

^ MySQL – database for storing tender data

^ Requests / urllib3 – document downloading

^ AWS S3 – file storage integration

^ Regular Expressions & HTML parsing – for content cleaning
