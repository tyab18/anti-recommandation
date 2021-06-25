export type Point = [number, number];

export interface Comment {
  id: number;
  author: string;
  date: string;
  job: string;
  content: string;
};

export interface CommentPoint {
  id: number;
  pos: Point;
}
