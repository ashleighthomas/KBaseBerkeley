from flask import Flask
from flask import request
from flask import Response
from assembleText import assemble
app = Flask(__name__)

@app.route('/assemble', methods=['POST'])
def call_main():
	fragments = request.form['fragments']
	text = assemble(fragments.split('\n'))
	return Response(text, status=200)	
	
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)
