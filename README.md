# JJALBot
An extended way of posting a large emoji in Slack

## Start
```
$ tmux attach -t jjalbot
$ gunicorn --bind unix:/tmp/gunicorn.sock jjalbot.wsgi:application 
```

## Reloading configuration
```
$ ps aux | grep gunicorn
$ kill -HUP [masterpid]
```
