import requests
team_token = ''

def submit_preds(user_id, description, filename)
	files={'files': open('sample_submission.csv','rb')}

	data = {
	    "user_id": user_id,
	    "team_token": team_token,
	    "description": description,
	    "filename": filename
	}
	url = 'https://biendata.com/competition/kdd_2018_submit/'
	response = requests.post(url, files=files, data=data)
	print(response.text)