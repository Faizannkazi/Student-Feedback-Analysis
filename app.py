from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from textblob import TextBlob

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/favicon.ico')
def favicon():
    return '', 204

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        
        if user:
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('feedback'))
        else:
            return "Invalid Credentials. Please try again."
            
    return render_template('login.html')

@app.route('/feedback', methods=('GET', 'POST'))
def feedback():
    if request.method == 'POST':
        subject = request.form['subject']
        faculty_name = request.form['faculty_name']
        rating = request.form['rating']
        comments = request.form['comments']
        
        
        sentiment = "Neutral"
        if comments.strip():
            analysis = TextBlob(comments)
            if analysis.sentiment.polarity > 0.1:
                sentiment = "Positive"
            elif analysis.sentiment.polarity < -0.1:
                sentiment = "Negative"
        
        conn = get_db_connection()
        conn.execute('INSERT INTO feedback (subject, faculty_name, rating, comments, sentiment) VALUES (?, ?, ?, ?, ?)',
                     (subject, faculty_name, rating, comments, sentiment))
        conn.commit()
        conn.close()
        return "Feedback Submitted Successfully!"
        
    return render_template('feedback.html')

@app.route('/dashboard')
def dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    
    
    total_feedback = conn.execute('SELECT COUNT(*) FROM feedback').fetchone()[0]
    avg_query = conn.execute('SELECT AVG(rating) FROM feedback').fetchone()[0]
    average_rating = round(avg_query, 1) if avg_query else 0.0 
    
    feedbacks = conn.execute('SELECT * FROM feedback').fetchall()
    
    
    rating_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    counts_query = conn.execute('SELECT rating, COUNT(*) as count FROM feedback GROUP BY rating').fetchall()
    for row in counts_query:
        rating_counts[row['rating']] = row['count']
    doughnut_data = [rating_counts[5], rating_counts[4], rating_counts[3], rating_counts[2], rating_counts[1]]
    
    
    subject_stats = []
    subject_labels = []
    subject_averages = []
    
    sub_query = conn.execute('SELECT subject, AVG(rating) as avg_rating FROM feedback GROUP BY subject').fetchall()
    for row in sub_query:
        avg_r = round(row['avg_rating'], 2)
        subject_stats.append({'subject': row['subject'], 'avg': avg_r})
        subject_labels.append(row['subject'])
        subject_averages.append(avg_r)
        
    conn.close()
    
    return render_template('dashboard.html', 
                           total_feedback=total_feedback, 
                           average_rating=average_rating, 
                           feedbacks=feedbacks, 
                           doughnut_data=doughnut_data,
                           subject_stats=subject_stats,
                           subject_labels=subject_labels,
                           subject_averages=subject_averages)

if __name__ == '__main__':
    app.run(debug=True)