# JJALBot

[![Build Status](https://travis-ci.com/RUN-KAIST/jjalbot.svg?branch=master)](https://travis-ci.com/RUN-KAIST/jjalbot)

## What is JJALBot?
짤봇은 슬랙에 짤을 업로드해주는 슬랙 앱입니다. 슬랙에는 다양한 이미지를 이모지라는 것으로 만들어 
사용할 수 있지만, 항상 정사각형 이미지만 가능하고 크기가 작기 때문에 한계가 있습니다. 그렇지만 
단순 이미지 업로드는 짤을 찾아서 업로드하는 시간이 길기 때문에 불편함이 많습니다. 짤봇은 이러한 
불편함을 해결해주는 앱입니다.

## How to use JJALBot?
1. 먼저 [짤 등록 페이지](https://run.kaist.ac.kr/jjalbot/)에 접속하고, Log in with Slack 
버튼을 눌러 슬랙으로 로그인합니다.

2. 아직 슬랙에 짤봇을 설치하지 않았다면, Add to Slack 버튼을 눌러 슬랙에 설치합니다. 슬랙 
관리자 권한이 필요할 수도 있습니다.

3. Add to Slack 버튼 위에 있는 링크를 클릭해 짤봇에게 슬랙 채팅 업로드, 파일 업로드 권한을 
부여해야 슬랙에서 짤봇이 짤을 업로드할 수 있습니다.

4. 짤 이름과 짤 이미지를 업로드합니다.

5. 슬랙에서 채팅으로 `/bigemoji [짤 이름]`을 치면 잠시 후에 짤 이름에 대응되는 이미지가 업로드됩니다.

## Development guide

1. If you have [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/),
you can just run `docker-compose up`. Otherwise, follow the steps below.

1. Install [Poetry](https://github.com/sdispater/poetry). 

1. Install required project dependencies. It is as simple as `poetry install`.

1. Prepare your own [Slack app](https://api.slack.com/apps).

1. Add Slack slash commands `/bigemoji` and `/bigemoji_list`, which both POST
to `http://localhost:8000/jjalbot/app/`.

1. Run `python manage.py migrate`, and create a super user by `python manage.py createsuperuser`.

1. Open `http://localhost:8000/jjalbot/admin/`, and login with the user you just created.

1. In `SITES` category, open `Sites` admin page and change the domain name `example.com` to `localhost:8000`.

1. In `SOCIAL ACCOUNTS` category, open `Social applications` admin page and click 
`ADD SOCIAL APPLICATION`. 

1. Select `Slack` for provider, set the `Client id` and `Secret key` you obtained 
from your Slack app at step 3. Add `localhost:8000` site and save.

1. Now you should be ready to use all functionality.
