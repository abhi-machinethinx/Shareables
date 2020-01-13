from flask import Flask
from flask import request
from flask_restful import Resource
from flask_restful import Api
from os import makedirs

app = Flask(__name__)
api = Api(app)

class Code_Upload(Resource):
    def post(self):
        file = request.files['file']
        if file:
            filename = file.filename
            cwd = "C:/Users/Admin/Documents/Python_Scripts/REST/files/"
            file.save(open(cwd+"/"+filename,"wb"))
            return

api.add_resource(Code_Upload, '/rcv_code')


if __name__ == '__main__':
    app.run(host='172.172.172.122', port='6005')
