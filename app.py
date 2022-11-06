from flask import Flask,render_template,request
import summarizer1
import summarizer2

app = Flask(__name__)

@app.route('/')
def Welcome():
    return render_template('index.html')

@app.route('/submit1',methods=['POST','GET'])
def submit1():
    if(request.method=='POST'):
        summary = summarizer1.yt_summarizer(request.form['link'])
        for i in summary:
            print(i['title'])
        return render_template('result1.html',sum=summary)

@app.route('/submit2',methods=['POST','GET'])
def submit2():
    if(request.method=='POST'):
        summary = summarizer2.yt_summarizer(request.form['link'])
        print(summary)
        return render_template('result2.html',sum=summary)


if __name__ == '__main__':
    app.run(debug=True)