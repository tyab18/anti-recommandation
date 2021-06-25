<template>
  <div class="root">
    <h1>アンチレコメンデーション</h1>

    <div>
      <details>
        <summary>説明</summary>
        <p>以下のアンケートに回答し、自分の意見を分析して自分と異なる意見を見てみましょう。</p>
        <h3>使い方</h3>
        <ul>
          <li>送信ボタンを押すとコメント分布図が表示されます。</li>
          <li>赤い点は自分のコメントを、青い点は他のコメントを示しています。</li>
          <li>コメント分布図をクリックすると、クリックする箇所の近傍にあるコメントが表示されます。</li>
          <li>コメント分布図の上にある4つの象限ボタンを押すと、対応する位置のコメントが表示されます。</li>
        </ul>
      </details>
    </div>
    <div class="spacer"></div>

    <div>
      <h2>アンケート</h2>
      <div class="question" v-for="(q, i) in questions" :key="q">
        <div class="question-text">{{`Q${i+1}. ${q}`}}</div>
        <textarea rows="4" v-model="answers[i]"></textarea>
      </div>
    </div>
    <button @click="submit" :disabled="submitDisabled">送信</button>
    <div class="spacer"></div>
    <p class="pre">{{statusMessage}}</p>

    <div id="result" v-show="sPoint">
      <h2>分析結果</h2>
      <table class="center" style="display: none">
        <tr>
          <td><label>最大検索半径</label></td>
          <td><input type="range" min="0.1" max="0.5" step="0.1"
            v-model="maxSearchRadius"></td>
        </tr>
        <tr>
          <td><label>最大コメント数</label></td>
          <td><input type="range" min="1" max="20" step="1"
            v-model="maxSearchCount"></td>
        </tr>
      </table>

      <canvas-view ref="cv"
        :o-points="oPoints" :s-point="sPoint"
        :h-points="commentPositions"
        :point-radius="0.015"
        :max-search-radius="maxSearchRadius"
        :max-search-count="maxSearchCount"
        @request="showComments"/>
      <div class="result-ctn">
        <div v-for="r in comments" :key="r[3]" class="result">
          <div>
            <span class="author">{{r.author}}</span>
            <span class="date">{{r.date}}</span>
          </div>
          <div>
            <span class="job">{{r.job}}</span>
          </div>
          <div class="spacer"></div>
          <div>{{r.content}}</div>
        </div>
      </div>

      <div>
        <button v-if="comments.length<commentIDs.length"
          class="more" @click="showMore">もっと表示</button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import {Vue, Component} from 'vue-property-decorator';
import CanvasView from './canvas.vue';
import {Point, CommentPoint, Comment} from '@/type';

@Component({
  components: {
    CanvasView,
  },
})
export default class extends Vue {
  questions: string[] = []
  answers: string[] = []
  submitDisabled = false
  statusMessage = ''
  comments: Comment[] = []
  commentPositions: Point[] = []
  oPoints: CommentPoint[] = []
  sPoint: Point | null = null
  cachedComments: {[id: number]: Comment} = {};
  page = 1
  // search
  maxSearchRadius = 0.2
  maxSearchCount = 5

  private async getQuestions() {
    const {data} = await this.$api.get('/questions');
    this.questions = data;
    this.answers = data.map(() => '');
  }
  private async getPoints() {
    const {data} = await this.$api.get('/points');
    this.oPoints = data;
  }
  async created() {
    this.getQuestions();
    this.getPoints();
  }
  submit() {
    this.sPoint = null;
    this.statusMessage = '分析中…少々お待ちください';
    this.submitDisabled = true;
    const {answers} = this;
    this.$api.post('/answers', {answers})
      .then(({data}) => {
        this.statusMessage = '';
        this.sPoint = data;
        this.submitDisabled = false;
      })
      .catch(err => {
        this.statusMessage = 'エラーが発生しました：\n'+err.toString();
        this.submitDisabled = false;
        console.log(err);
      });
  }

  async fetchComments(ids: number[]) {
    const fetchIDs = ids.filter(id => this.cachedComments[id]==null);
    // fetch and update
    if (fetchIDs.length) {
      try {
        const {data} = await this.$api.get('/comments', {
          params: {
            ids: fetchIDs.join(','),
          },
        });
        for (const c of data) {
          this.cachedComments[c.id] = c;
        }
      } catch (err) {
        this.statusMessage = 'エラーが発生しました：\n'+err.toString();
        console.log(err);
        return;
      };
    }
  }

  commentIDs: number[] = []
  commentPerPage = 5
  async showComments(points: CommentPoint[]) {
    const cids = points.map(e => e.id);
    const ids = cids.slice(0, this.commentPerPage);
    await this.fetchComments(ids.slice(0, this.commentPerPage));

    // result
    this.commentIDs = cids;
    this.comments = ids.map(id => this.cachedComments[id]);
    this.commentPositions = points.map(e => e.pos); // TODO
    this.page = 1;
  }
  async showMore() {
    const {commentIDs: cids, commentPerPage: m, page: p} = this;
    const ids = cids.slice(p*m, (p+1)*m);
    await this.fetchComments(ids);
    this.comments.push(...ids.map(id => this.cachedComments[id]));
    this.page++;
  }
}
</script>

<style>
:root {
  --fg: #000;
  --bg: #fff;
  --bd: #000;
}
.dark-mode {
  --fg: #eee;
  --bg: #333;
  --bd: #eee;
}

body {
  padding: 16px;
  color: var(--fg);
  background: var(--bg);
}
p.pre {
  white-space: pre;
}

textarea {
  width: 100%;
  resize: unset;
  color: var(--fg);
  background: var(--bg);
  box-sizing: border-box;
  border: solid 1px var(--bd);
  /* border-radius: 1em; */
  padding: 0.5em;
  font-size: 1em;
}

button {
  border: 0;
  color: #fff;
  background: #4f71be;
  width: 96px;
  height: 24px;
  border-radius: 4px;
}
button:disabled, button:disabled:hover {
  background: #777;
}
button:hover {
  background: #3e60ad;
}
button:active {
  background: #2d4f9c;
  border: none;
}

.root {
  margin: auto;
  max-width: 640px;
  text-align: center;
  padding: 4px;
}
details {
  text-align: left;
  border: 1px solid;
  padding: 0.5em 1em;
}

.question {
  margin: 16px auto;
}
.question:last-child {
  margin: 16px auto 8px;
}
.question-text {
  text-align: left;
  padding: 2px;
}

.result {
  border: solid 1px var(--bd);
  margin: 6px auto;
  padding: 8px;
  text-align: left;
  border-radius: 6px;
}
.author {
  font-weight: bold;
}
.date {
  color: #777;
}
.job {
  color: #777;
}
.spacer {
  height: 1em;
}

table.center {margin: auto}
h3 + ul {
  margin-block-start: -1em;
  padding-inline-start: 1.5em;
}
</style>
