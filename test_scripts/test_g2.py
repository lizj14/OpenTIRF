import graph as gr

a = gr.Point(1.0, 1.0)
b = gr.Point(1.0, 2.0)
c = gr.Point(2.0, 2.0)
d = gr.Point(2.0, 1.0)

p = gr.Polygon([a, b, c, d])

print(p.judge_points_inside(gr.Point(1.5, 1.5)))
print(p.judge_points_inside(gr.Point(1.5, 0.5)))
print(p.judge_points_inside(gr.Point(4.0, 4.0)))
