<template>
  <div>
    <p v-show="sPoint">あなたは<span class="rem">{{msgY}}</span>な<span class="rem">{{msgX}}</span>支持者に近いです</p>
    <div class="ctn-2x2">
      <div v-for="(_, i) in 2" :key="i">
        <button v-for="(_, j) in 2" :key="j"
          :clicked="clickedQuadrant==(j<<1|(1-i))"
          @click="searchQuadrant(j, !i)"></button>
      </div>
    </div>
    <div style="font-weight: normal; color: black">
      <div style="text-align: center">攻撃的</div>
      <span class="tbrl" style="transform: translateY(-240px) translateY(50%)"
       >バイデン</span>
      <canvas ref="cv" width="480" height="480" />
      <span class="tbrl" style="transform: translateY(-240px) translateY(50%)"
        >トランプ</span>
      <div style="text-align: center">非攻撃的</div>
    </div>
  </div>
</template>

<script lang="ts">
import {Vue, Component, Prop, Watch} from 'vue-property-decorator';
import {Point, CommentPoint} from '@/type';

declare global {
  interface CanvasRenderingContext2D {
    fillCircle(
      x: number, y: number, r: number,
      theta0?: number, dtheta?: number,
    ): Path2D;
  }
}
CanvasRenderingContext2D.prototype.fillCircle = function(
  x: number, y: number, r: number,
  theta0: number=0, dtheta: number=TAU,
): Path2D {
  const circle = new Path2D();
  circle.arc(x, y, r, theta0, dtheta);
  this.fill(circle);
  return circle;
};

const TAU = Math.PI*2;
const dis = (p0: Point, p1: Point) =>
  ((p0[0]-p1[0])**2 + (p0[1]-p1[1])**2)**0.5;
@Component
export default class extends Vue {
  @Prop() oPoints!: CommentPoint[]; // other points
  @Prop() sPoint!: Point | null // user point
  @Prop() pointRadius!: number // radius of every point
  @Prop() maxSearchCount!:number
  @Prop() maxSearchRadius!:number
  @Prop() hPoints!: Point[] // highlight points
  private ctx!: CanvasRenderingContext2D;
  private clickedQuadrant = -1
  private drawRange = 1.02

  get msgX(): string {
    const {sPoint} = this;
    if (!sPoint) return '';
    return sPoint[0] > 0 ? 'トランプ' : 'バイデン';
  }
  get msgY(): string {
    const {sPoint} = this;
    if (!sPoint) return '';
    return sPoint[1] > 0 ? '攻撃的' : '非攻撃的';
  }

  mounted() {
    const cv = this.$refs.cv as HTMLCanvasElement;
    this.ctx = cv.getContext('2d')!;

    cv.onclick = e => {
      const {drawRange: dr} = this;
      const {offsetX: rx, offsetY: ry} = e;
      const {width: w, height: h} = cv;
      const x = (rx/w*2-1)*dr;
      const y = (1-ry/h*2)*dr;
      this.onClick(x, y);
    };
  }

  @Watch('oPoints')
  draw() {
    const {ctx, pointRadius: r, drawRange: dr, oPoints, sPoint} = this;
    if (oPoints == null) return;
    const {width: w, height: h} = ctx.canvas;
    ctx.resetTransform();
    ctx.clearRect(0, 0, w, h);
    ctx.transform(w/dr/2, 0, 0, -h/dr/2, w/2, h/2);

    // axis
    const wa = 0.004;
    ctx.fillStyle = '#bbb';
    ctx.fillRect(-dr, -wa/2, dr*2, wa);
    ctx.fillRect(-wa/2, -dr, wa, dr*2);

    // circles
    ctx.fillStyle = '#00f';
    for (const {pos: [x, y]} of oPoints) {
      ctx.fillCircle(x, y, r);
    }
    if (sPoint != null) {
      ctx.fillStyle = '#f00';
      ctx.fillCircle(sPoint[0], sPoint[1], r);
    }
  }

  @Watch('sPoint')
  didUserPointUpdate() {
    const {sPoint} = this;
    if (sPoint == null) return this.draw();
    this.searchQuadrant(sPoint[0]<0, sPoint[1]>=0);
    console.log(sPoint);
    // scroll
    const v = document.querySelector('#result')!;
    const {top: vY} = v.getBoundingClientRect();
    window.scrollBy({
      top: vY-14,
      behavior: 'smooth',
    });
  }

  @Watch('hPoints')
  drawHighlight() {
    const {ctx, hPoints, pointRadius: r} = this;
    if (hPoints != null) {
      ctx.fillStyle = '#707';
      for (const [x, y] of hPoints) {
        ctx.fillCircle(x, y, r);
      }
    }
  }

  onClick(x: number, y: number) {
    this.clickedQuadrant = -1;
    // calc radius
    const {
      ctx, maxSearchCount: mC, maxSearchRadius: mR,
      pointRadius: pR,
    } = this;
    const points = // [CommentPoint, dis]
      this.oPoints.map((p): [CommentPoint, number]=>[p, dis(p.pos, [x, y])])
        .filter(e => e[1]<=mR) // dis <= mR
        .sort((a, b) => a[1]-b[1]); // order by dis ASC
    // send event
    this.$emit('request', points.slice(0, mC).map(e => e[0]));
    // redraw points
    this.draw();
    // draw range circle
    const r = points.length > mC ? points[mC-1][1]+pR : mR;
    ctx.fillStyle = '#f003';
    ctx.fillCircle(x, y, r, 0, 2*Math.PI);
  }

  searchQuadrant(sx: boolean, sy: boolean) {
    this.clickedQuadrant = +sx<<1 | +sy;
    const {ctx, sPoint, drawRange: dr} = this;
    if (sPoint == null) return;
    const base: Point = [-sPoint[0], sPoint[1]];
    // filter
    const fx: (p: Point)=>boolean = sx ?
      pos => pos[0] >= 0 : pos => pos[0] < 0;
    const fy: (p: Point)=>boolean = sy ?
      pos => pos[1] >= 0 : pos => pos[1] < 0;
    const points = this.oPoints
      .filter(({pos}) => fx(pos) && fy(pos))
      .map((c): [CommentPoint, number] => [c, dis(c.pos, base)])
      .sort((a, b)=>a[1]-b[1]);
    // send event
    this.$emit('request', points.map(e => e[0]));
    // draw range circle
    this.draw();
    ctx.fillStyle = '#f003';
    ctx.fillRect(sx ? 0 : -dr, sy ? 0 : -dr, dr, dr);
  }
}
</script>

<style scoped>
canvas {
  border: solid var(--bd) 1px;
}
div.ctn-2x2 {
  margin: 0 0 8px;
}
div.ctn-2x2 > * {
  display:flex;
  align-items:center;
  justify-content:center;
}
div.ctn-2x2 button {
  width: 40px;
  height: 40px;
  margin: 2px;
}
button[clicked] {
  background-color: red;
}

.tbrl {
  -ms-writing-mode: tb-rl;
  writing-mode: vertical-rl;
}

span.rem {
  color: red;
  font-weight: bold;
}
</style>
