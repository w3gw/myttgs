from flask import Flask, request
from flask_mail import Message, Mail

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='wnorar@gmail.com',
    MAIL_PASSWORD='wogayehumeki'
)
mail = Mail(app)


@app.route("/hello/", methods=['GET', 'POST'])
def index():
    name = request.args.get('name')
    age = request.args.get('age')
    print("""hello %s .and %s 
		"""
		%(name, age))
    return name


@app.route('/send-mail/')
def send_mail():
    try:
        msg = Message("Send Mail Tutorial!",
                      sender="wnorar@gmail.com",
                      recipients=["w3gwmak@gmail.com"])
        msg.body = "Yo!\nHave you heard the good word of Python???"
        mail.send(msg)
        return 'Mail sent!'
    except Exception as e:
        return(str(e))


if __name__ == '__main__':
    app.run(debug=True)
