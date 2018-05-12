import requests
import sys
import getopt
team_token = '4d53493e18e23fe27fde8757a56693f7fed5f663dbffe730c15081f81a4f0f8b'

def submit_preds(csv, user_id, description, filename):
	files={'files': open(csv,'rb')}

	data = {
	    "user_id": user_id,
	    "team_token": team_token,
	    "description": description,
	    "filename": filename
	}
	url = 'https://biendata.com/competition/kdd_2018_submit/'
	response = requests.post(url, files=files, data=data)
	print(response.text)

def main(argv):
    csv = ''
    user_id = ''
    from_datetime = ''
    description = ''
    example = 'submit_preds.py -c <"csv"> -u <"user_id"> -d <"description"> -f <"filename">'
    try:
        opts, args = getopt.getopt(argv,"hc:u:d:f:",["csv=","user_id=","description=","filename="])
    except getopt.GetoptError:
        print(example)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(example)
            sys.exit()
        elif opt in ("-c", "--csv"):
            csv = arg
        elif opt in ("-u", "--user_id"):
            user_id = arg
        elif opt in ("-d", "--description"):
            description = arg
        elif opt in ("-f", "--filename"):
            filename = arg
    submit_preds(csv, user_id, description, filename)

if __name__ == "__main__":
    main(sys.argv[1:])