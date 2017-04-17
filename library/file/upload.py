import os, time
from lykchat.settings import BASE_DIR

def upload_file(file, filename='', username=''):
    timestr = time.strftime('%Y%m%d' , time.localtime())
    timestr = str(timestr)
    logfile = os.path.join(BASE_DIR, 'file/upload/index.txt')

    upload_dir = os.path.join(BASE_DIR, 'file/upload/' + timestr + '/')
    if not os.path.exists(upload_dir):
        try :
            os.mkdir(upload_dir)
        except :
            os.makedirs(upload_dir)

    '''
    if filename == '' or not filename :
        secstr = time.strftime('%H%M%S' , time.localtime())
        secstr = str(secstr)
        randomstr = random.randint(1000, 9999)
        randomstr = str(randomstr)
        filename = timestr + '-' + secstr + randomstr
    else :
        filename = upload_dir + str(filename)
    '''
        
    datetimestr = time.strftime('%Y-%m-%d %H:%M:%S' , time.localtime())
    datetimestr = str(datetimestr)
    log = str(username) + ' ' + datetimestr + ' ' + filename + '\n'
        
    filename = upload_dir + str(filename)
    secstr = time.strftime('%H%M%S' , time.localtime())
    secstr = str(secstr)
    if os.path.exists(filename):
        os.rename(filename , filename + '-' + timestr + '-' + secstr)
    
    
    with open(filename, 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)
        
        # os.system('chmod 444 ' + filename)
        open(logfile, 'a').write(log)
        return filename
    
    return False
    
    

