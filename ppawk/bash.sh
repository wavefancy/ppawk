echo -e '#1 2\n1 2\n3 4\n2.2 2.2' | python3 ./ppawk.py -B 'c=0' -E '"Total lines:"+str(c)' -f 'f[0]>1' 'c+=1;f[1],f[0]=f[0],f[1];f'
