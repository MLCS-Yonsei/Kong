import redis
import time
import numpy as np

r = redis.StrictRedis(host='redis.hwanmoo.kr', port=6379, db=0)

while True:
    ips = eval(r.hget('subscribers','list'))

    if ips is not None:
        for ip in ips:
            status = eval(r.hget('subscribers',ip))
            
            if status:
                img_shape = r.hget('person_images_shape',ip)
                if img_shape is not None:
                    img_bytes = r.hget('person_images',ip)

                    r.hdel('person_images_shape',ip)
                    r.hdel('person_images',ip)
                    r.hdel('person_attr',ip)

                    frame_frombytes = np.frombuffer(img_bytes, dtype=np.uint8).reshape(eval(img_shape))
                    
                    r.hset('person_attr',ip,'123')
            
            if status == False:
                ips.remove(ip)
    else:
        time.sleep(0.5)