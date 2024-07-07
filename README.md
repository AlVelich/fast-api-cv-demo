## redis set get method
docker run --network host -p 6379:6379 -d redis

```shell
docker run -it --network host --rm redis redis-cli -h 192.168.1.37
set 10 11
set 20 22
keys *
get 10
```
