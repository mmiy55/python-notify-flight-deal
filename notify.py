import requests
import creds

TOKEN = creds.line_token
api_url = 'https://notify-api.line.me/api/notify'
send_contents = 'New cheap flight available🙌!check your sheet✈️!'

TOKEN_dic = {'Authorization': 'Bearer' + ' ' + TOKEN}
send_dic = {'message': send_contents}
# print(TOKEN_dic)
# print(send_dic)

# test notification
# requests.post(api_url, headers=TOKEN_dic, data=send_dic)
