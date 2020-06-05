types:
	mypy --disallow-untyped-defs *.py

format:
	black chat_thief/*.py chat_thief/**/*.py *.py
	black tests/**/*.py tests/*.py

t:
	TEST_MODE=true BLOCK_TWITCH_MSGS=true python -m pytest --cov=chat_thief tests/*

f:
	TEST_MODE=true BLOCK_TWITCH_MSGS=true python -m pytest tests/* -m focus -s

backup:
	cp db/users.json db/backups/users.json
	cp db/commands.json db/backups/commands.json
	cp db/issues.json db/backups/issues.json
	cp db/sfx_votes.json db/backups/sfx_votes.json

restore:
	cp db/backups/users.json db/users.json
	cp db/backups/commands.json db/commands.json
	cp db/backups/issues.json db/issues.json
	cp db/backups/sfx_votes.json db/sfx_votes.json

# TODO: Move log files from the day before
new_day: backup
	rm db/play_soundeffects.json
	rm db/notifications.json
	rm db/cube_bets.json
	rm db/breaking_news.json
	rm db/votes.json
	rm .welcome

sync:
	scripts/sync_html.sh | lolcat

beginworld_html:
	python beginworld_publisher.py | lolcat

deploy: beginworld_html sync invalidate_cdn

invalidate_cdn:
	aws cloudfront create-invalidation \
			--distribution-id E382OTJDHBFSJL \
			--paths "/*" "/**/*"

deploy_all:
	aws s3 sync ./build/beginworld_finance s3://beginworld.exchange-f27cf15

full_deploy: deploy_all
