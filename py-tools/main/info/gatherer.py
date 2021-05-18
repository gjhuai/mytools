from xueqiu import XueQiu
import time, ssl

ssl._create_default_https_context = ssl._create_unverified_context
while(True):
    try:
        now = time.localtime()
        print("[%s] gather begin  " % time.strftime('%Y-%m-%d %H:%M:%S', now))
        picker = XueQiu()
        picker.download(-3)
        now = time.localtime()
        print("[%s] gather end  " % time.strftime('%Y-%m-%d %H:%M:%S', now))

    except Exception as e:
        print("app catch: %s\n" % ( e))
    time.sleep(2*60*60)

