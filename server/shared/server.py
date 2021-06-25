from flask import Flask, abort, jsonify, request, Response
import re
import csv
from BDAwork import analyze
app = Flask(__name__)

import sqlite3
db = sqlite3.connect('/shared/db.sqlite3', check_same_thread=False)

# api
@app.route('/v1/questions')
def get_questions():
  question_pool = [
#   'アメリカ大統領選挙では不正があったと思いますか？',
#   'アメリカ次期大統領のどこに期待していますか？',
#   'ドナルド・トランプ大統領の選挙後の行動についてどう思いますか？',
#   '今後の経済はどのようになっていくと思いますか？',
    'アメリカ大統領選挙において、あなたが不正を行ったと思う候補者はいましたか？そう思う理由を教えて下さい。',
    '2016年にトランプ氏が当選したとき、アメリカ国民はトランプ氏にどのようなことを期待したと思いますか？',
    '多くのグローバル企業がトランプ氏のSNSアカウントを凍結しています。これについてあなたはどのような感想を持ちましたか？',
    'トランプ氏は現在弾劾訴追されています。トランプ氏は今後どのような点で訴追されると思いますか？',
  ]
  questions = question_pool # random.sample(question_pool, 4)
  return jsonify(questions)

@app.route('/v1/answers', methods=['POST'])
def post_answers():
  """
    description: 回答を受信し、分析結果を送信
    requestBody: {
      "answers": string[],
    }
    response: [x: number, y: number]
  """
  o = request.get_json()
  answers = o['answers']
  x, y = analyze(answers)
  return jsonify([x, y])

@app.route('/v1/points', methods=['GET'])
def get_points():
  cs = db.cursor()
  rows = cs.execute('SELECT id, x, y FROM comments')
  results = [{
    'id': _id,
    'pos': (x, y),
  } for (_id, x, y) in rows]
  return jsonify(results)

@app.route('/v1/comments', methods=['GET'])
def get_comments():
  # query
  rids = request.args.get('ids')
  if rids is None: abort(400, '`ids` is required in query')
  if rids == '': return jsonify([])
  ids = [int(rid) for rid in rids.split(',')]
  # read db
  cs = db.cursor()
  rows = cs.execute('''
    SELECT id, author, date, job, content
    FROM comments
    WHERE id IN (%s)
  '''%('?,'*len(ids))[:-1], ids)
  results = [{
    'id': row[0],
    'author': row[1],
    'date': row[2],
    'job': row[3],
    'content': row[4],
  } for row in rows]
  return jsonify(results)

#app.run(host='127.0.0.1', port=3333)
app.run(host='::', port=3333)
