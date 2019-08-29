import os, json


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_secret(k):

    secret_file = os.path.join(BASE_DIR, 'secrets.json')  # secrets.json 파일 위치를 명시

    with open(secret_file) as f:
        secrets = json.loads(f.read())

    try:
        return secrets[k]

    except KeyError:
        error_msg = "Set the {} environment variable".format(k)


# if __name__ == '__main__':
#     print(get_secret("GOOGLE_MAP_KEY"))
