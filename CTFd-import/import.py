from CTFd.models import Teams, Solves, Challenges, WrongKeys, Keys, Tags, Files, Tracking
from CTFd import create_app
import json, sys

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("Usage : %s filename.json" % sys.argv[0])
		exit()

	filename = sys.argv[1]
	__name__ = 'CTFd'
	app = create_app()

	with app.app_context():
		db = app.db
		data = json.load(open(filename))

		# Clean before update
		db.session.query(Challenges).delete()

		for challenge in data["challenges"]:
			name = challenge["name"]
			message = challenge["message"]
			value = challenge["value"]
			category = challenge["category"]
			keys = challenge["key"]
			files = challenge["files"]

			challenge_obj = Challenges(name, message, value, category)
			db.session.add(challenge_obj)
			db.session.commit()

			for key in keys:
				key_obj = Keys(challenge_obj.id, key["flag"], key["type"])
				db.session.add(key_obj)	

			for path in files:
				db.session.add(Files(challenge_obj.id, path))
			
			db.session.commit()
