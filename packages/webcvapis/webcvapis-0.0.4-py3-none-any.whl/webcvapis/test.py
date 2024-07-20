try: from .web_canvas import WebCanvas
except Exception: from web_canvas import WebCanvas
cv = WebCanvas(800, 800, 10, 10, debug=True)
cv.create_text(400, 400, "Hello World", textAlign="center", textBaseline="middle", font="30px Arial")
cv.loop_to_close()