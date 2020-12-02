from django.shortcuts import redirect
from django.db import connection

#streaming part
import os
import re
import mimetypes
from wsgiref.util import FileWrapper
from django.http import HttpResponse
from django.http.response import StreamingHttpResponse


range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)


class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data


def stream_video(request, file_name):
    if request.session.get('is_logged_in'):
        print("here")
        range_header = request.META.get('HTTP_RANGE', '').strip()
        range_match = range_re.match(range_header)
        path = "E:\\"+file_name
        size = os.path.getsize(path)
        print(path)
        print(size)
        content_type, encoding = mimetypes.guess_type(path)
        content_type = content_type or 'application/octet-stream'
        if range_match:
            print("range_match")
            first_byte, last_byte = range_match.groups()
            first_byte = int(first_byte) if first_byte else 0
            last_byte = int(last_byte) if last_byte else size - 1
            if last_byte >= size:
                last_byte = size - 1
            length = last_byte - first_byte + 1
            resp = StreamingHttpResponse(RangeFileWrapper(open(path, 'rb'), offset=first_byte, length=length), status=206, content_type=content_type)
            resp['Content-Length'] = str(length)
            resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
            print('bytes %s-%s/%s' % (first_byte, last_byte, size))
        else:
            print("not range_match")
            resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
            resp['Content-Length'] = str(size)
        resp['Accept-Ranges'] = 'bytes'
        print("at the end")
        return resp
    else:
        return redirect("http://127.0.0.1:8000/user/login")

def pushintoDhistory(show_id,user_id):
    print(show_id)
    print(user_id)
    #generate download_id
    cursor = connection.cursor()
    sql_ID = "SELECT NVL(MAX(DOWNLOAD_ID),0) FROM DOWNLOAD_HISTORY"
    cursor.execute(sql_ID)
    result = cursor.fetchall()
    for i in result:
        down_ID = i[0]
    cursor.close()
    down_ID = down_ID+1
    print(down_ID)

    #get subscription_id
    cursor = connection.cursor()
    sql = "SELECT SUBSCRIPTION_ID FROM SUBSCRIPTION WHERE USER_IDSUB = %s AND  SHOW_IDSUB = %s"
    cursor.execute(sql,[user_id,show_id])
    result = cursor.fetchall()
    for i in result:
        sub_ID = i[0]
    cursor.close()
    print(sub_ID)

    #generate download time
    cursor = connection.cursor()
    curr_date_sql = "SELECT TO_CHAR(SYSDATE, 'YYYY-MM-DD') FROM dual"
    curr_date_list = cursor.execute(curr_date_sql)
    for i in curr_date_list:
        curr_date = str(i[0])
    print(curr_date)
    cursor.close()
    isFav = "no"
    #insert into download_history
    cursor = connection.cursor()
    sql = "INSERT INTO DOWNLOAD_HISTORY VALUES(%s, %s, %s, %s)"
    cursor.execute(sql, [down_ID,curr_date,isFav,sub_ID])
    connection.commit()
    cursor.close()



def download_video(request,file_name):
    if request.session.get('is_logged_in'):
        user_id = request.session.get('user_ID', -1)
        print("here in download")
        file_name = file_name.split("-")
        print(file_name[0])
        print(file_name[1])
        show_id = file_name[1]
        path = "E:\\"+file_name[0]
        if os.path.exists(path):
            pushintoDhistory(show_id,user_id)
            with open(path,'rb') as fh:
                print("got the movie")
                response = HttpResponse(fh.read(),content_type = "application/force-download")
                response['Content-Disposition'] = 'inline;file_name'
                return response
        raise Http404
    else:
        return redirect("http://127.0.0.1:8000/user/login")
