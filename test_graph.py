import graph as gr

a = gr.Point(1.0, 1.0)
b = gr.Point(1.0, 2.0)
c = gr.Point(2.0, 2.0)
d = gr.Point(3.0, 3.0)
e = gr.Point(2.5, 1.5)
f = gr.Point(4.0, 0.5)
g = gr.Point(2.0, 1.0)

p = gr.Polygon([a, b, c, d, e, f, g])

print(p.judge_points_inside(gr.Point(1.5, 1.5)))
print(p.judge_points_inside(gr.Point(1.5, 0.5)))
print(p.judge_points_inside(gr.Point(4.0, 4.0)))
print(p.judge_points_inside(gr.Point(1.2, 1.7)))
print(p.judge_points_inside(gr.Point(2.3, 1.6)))
print(p.judge_points_inside(gr.Point(2.6, 1.6)))
print(p.judge_points_inside(gr.Point(3.0, 0.6)))