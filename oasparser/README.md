# How to run via docker


```bash
docker build -t oas-parser-webservice .
docker run -p 5111:5000 oas-parser-webservice
docker run -p 5111:5000 oas-parser-webservice
```

Calling the API

```bash
curl -X POST -F "file=@vampi.yaml" http://localhost:5112/parse
```

Command to see service running on port 5111
```bash
sudo netstat -tuln | grep :5111
```

Command to kill service running on port 5111
```bash
sudo kill -9 $(sudo netstat -tlnp | grep :5111 | awk '{print $7}' | cut -d'/' -f1)
```

HeartBeat

```bash
curl -X GET http://192.168.1.106:5111/heartbeat
```