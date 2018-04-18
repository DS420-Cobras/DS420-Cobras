import requests
import sys
import getopt
team_token = ''

# def submit_preds(csv, user_id, description, filename):
# 	files={'files': open(csv,'rb')}

# 	data = {
# 	    "user_id": user_id,
# 	    "team_token": team_token,
# 	    "description": description,
# 	    "filename": filename
# 	}
# 	url = 'https://biendata.com/competition/kdd_2018_submit/'
# 	response = requests.post(url, files=files, data=data)
# 	print(response.text)
def fun(csv, user_id, description, filename):
	print(user_id)
	print(description)
	print(filename)


def main(airgv)
	csv = ''
    user_id = ''
    from_datetime = ''
    description = ''
    example = 'submit_preds.py -c <"csv"> -u <"user_id"> -d <"description"> -f <"filename">'
    try:
        opts, args = getopt.getopt(argv,"c:u:d:f:",["csv=","user_id=","description=","filename="])
    except getopt.GetoptError:
        print(example)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-c", "--csv"):
            csv = arg
        elif opt in ("-u", "--user_id"):
            user_id = arg
        elif opt in ("-d", "--description"):
            description = arg
        elif opt in ("-f", "--filename"):
            filename = arg
       	fun(csv, user_id, description, filename)

if __name__ == "__main__":
    main(sys.argv[1:])