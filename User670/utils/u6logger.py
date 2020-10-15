import time

def log(*a):
	now=time.ctime()
	b=[]
	for i in a:
		b.append(str(i))
	t=now+" "+(" ".join(b))+"\n"
	
	f=open("./User670/data/log.txt","a")
	f.write(t)
	f.close()
		