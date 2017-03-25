"""
This program scrapes a website which uses AJAX to render html content
Using Selenium with Chrome webdriver and BeautifulSoup
"""

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

def get_vat_details(firm_name):
	"""
	This functions returns the vat details of firm_name
	if found in the database.
	"""

	url = "https://www.mptax.mp.gov.in/mpvatweb/index.jsp#"
	driver = webdriver.Chrome()

	# Getting the home page
	driver.get(url)

	# Clicking on the menu-->submenu and entering 2nd page
	menu = WebDriverWait(driver, 10).until(
		EC.visibility_of_element_located(
			(By.XPATH, "//td[@id='mainsection']/form/table/tbody/tr[3]/td[3]/a")))
	ActionChains(driver).move_to_element(menu).perform()

	submenu = WebDriverWait(driver, 10).until(
			EC.visibility_of_element_located((By.CSS_SELECTOR, "#dropmenudiv > a")))
	ActionChains(driver).click(submenu).perform()

	# Selecting Firm Name radion button and filling the search form
	firm_name_btn = WebDriverWait(driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, "//input[@id='byName']")))
	firm_name_btn.click()

	firm_name_form = WebDriverWait(driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, "//input[@name='name']")))
	firm_name_form.send_keys(firm_name)

	firm_name_form.submit()

	# Getting the html content of the page
	html_content = driver.page_source
	try:
		soup = BeautifulSoup(html_content, 'lxml')
	except AttributeError as e:
		print(e)
		sys.exit(1)

	# Extracting data from the table
	right_table = soup.findAll('table', class_ = 'tab3')

	# Checking if the firm name exists
	if len(right_table)<2:
		x_dict = {'VAT RC NO':'Not found in databse'}
		print(json.dumps(x_dict))
	else:
		rows = right_table[2].findAll('tr')
		main_list = []
		for tr in rows:
		    cols = tr.findAll('td')
		    lis = []
		    for td in cols:
		        lis.append(td.text)
		    if 'VAT' in lis:
		    	main_list.append(lis)

		if len(main_list)<1:
			# No VAT details found in databse
			x_dict = {'VAT RC NO':'Not found in databse'}
			print(json.dumps(x_dict))
		else:
			for single_list in main_list:
				company_dict = {}
				for i in range(len(single_list)):
					if i==1:
						company_dict['Firm Name'] = single_list[i]
					if i==2:
						company_dict['TIN'] = single_list[i]
					if i==3:
						company_dict['Registration_Status'] = single_list[i]
					if i==7:
						company_dict['Circle_Name'] = single_list[i]
						
				print(json.dumps(company_dict, indent=4, separators=(',', ': ')))

	# Closinng the browser after the task is complete
	driver.quit()


if __name__ == '__main__':
	firmname = input("Please enter the firm name you wish to search: ")
	get_vat_details(firmname)
