deploy:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 369149519541.dkr.ecr.ap-northeast-1.amazonaws.com
	docker build -t geniac_takahashi .
	docker tag geniac_takahashi:latest 369149519541.dkr.ecr.ap-northeast-1.amazonaws.com/geniac_takahashi:latest
	docker tag geniac_takahashi:latest 369149519541.dkr.ecr.ap-northeast-1.amazonaws.com/geniac_takahashi:latest
	docker push 369149519541.dkr.ecr.ap-northeast-1.amazonaws.com/geniac_takahashi:latest