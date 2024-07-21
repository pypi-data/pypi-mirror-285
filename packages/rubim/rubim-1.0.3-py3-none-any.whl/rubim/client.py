from requests.sessions import Session ; Session = Session() 
from .config import config

class req:

    def __init__(self,auth:str):
        self.auth = auth

    def send_request(self,data:dict,method:str):
        try:
            response = Session.post(url="https://rubino17.iranlms.ir/",headers=config.headers,json={
                "api_version": "0",
                "auth": self.auth,
                "client":config.android,
                "data": data,
                "method": method
            })
        except Exception:
            print(Exception)
        else:
            return response.json()
        
    def requestUploadFile(self,file_name:str,size:str,file_type:str,profile_id:str=None):
        return self.send_request({
            "file_name": file_name,
            "file_size": str(size), 
            "file_type": file_type,
            "profile_id": profile_id
        },"requestUploadFile")

    def upload(self,post_file:str,post_type:str,profile_id:str=None):
        file_byte_code = post_file if type(post_file) is bytes else open(post_file,"rb").read()
        upload_res = self.requestUploadFile("video.mp4" if post_type == "Video" else "picture.jpg",len(file_byte_code),post_type,profile_id)
        if upload_res != None:
            upload_res = upload_res["data"]
            total_part = len(file_byte_code) // 131072
            upload_data = 0
            for part in range(1, total_part + 2):
                beyte_part = file_byte_code[131072 * (part - 1) : 131072 * part]
                header={
                    "part-number":str(part),
                    "total-part":str(total_part + 1),
                    "auth":self.auth,
                    "hash-file-request":upload_res["hash_file_request"],
                    "file-id":str(upload_res["file_id"]),
                    "content-type": "application/octet-stream",
                    "content-length": str(len(beyte_part)),
                    "Host":upload_res["server_url"].replace("https://","").replace("/UploadFile.ashx",""),
                    "Connection":"Keep-Alive",
                    "accept-encoding": "gzip",
                    "user-agent": "okhttp/3.12.1",
                }
                while True:
                    response = Session.post(data=beyte_part,url=upload_res["server_url"],headers=header)
                    if response.status_code == 200:
                        upload_data += round(len(beyte_part) / 1024)
                        print(f'\r{upload_data / 1000} MB | {round(len(file_byte_code) / 1024) / 1000} MB',end=f'')
                        break
            print("\n")
            return [upload_res, response.json()["data"]["hash_file_receive"]]