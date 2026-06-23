with open('/opt/data/.env') as f:
    for line in f:
        if '=' in line and len(line.split('=', 1)[1].strip()) > 0:
            print(line.split('=', 1)[0])
