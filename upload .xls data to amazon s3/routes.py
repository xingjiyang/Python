import os
import pandas as pd
import gspread
import boto3
import json
import xlsxwriter
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
from flask import Flask, request, redirect, render_template,url_for
from pandas import ExcelWriter
from pandas import ExcelFile
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploadfile'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

@app.route('/', methods=['GET','POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		global filename
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		xls = pd.ExcelFile(filename)
		df = pd.read_excel(xls, 'Sheet1')
		column = df.columns

		#upload file to s3, not required in this method.
		#s3=boto3.client('s3')
		#s3.upload_file(filename,'inventory-db',filename)
		
		dframe = pd.read_excel(filename)
		dframe.to_excel("data.xlsx", index=False)

		return render_template("upload.html", file_columns=column, filename=filename)
	return render_template("upload.html")

@app.route('/import', methods=['POST'])
def import_data():
	#download file from s3, not required in this method.	
	#bucketname = 'inventory-db' # replace with your bucket name
	#s3 = boto3.resource('s3')
	#s3.Bucket(bucketname).download_file(filename, filename)
	
	#read selected columns, and write to data.xlsx
	selected_columns = request.form['input_columns']
	selected_columns = selected_columns.split(',')
	df = pd.read_excel(filename, sheet_names ='Sheet1', usecols=selected_columns)
	df.to_excel("data.xlsx", index=False)

	#upload data.xlsx to s3
	s3=boto3.client('s3')	
	s3.upload_file("data.xlsx",'inventory-db',"data.xlsx")

	return render_template("upload.html") 

@app.route('/uploadlink/')
def upload_link():
	scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
	creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
	client = gspread.authorize(creds)
	sheet = client.open("test").sheet1  # Open the spreadhseet.sheet1
	values_list = sheet.row_values(1)  # Get a specific column (in row 1)
	return render_template("upload.html", file_columns=values_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)




