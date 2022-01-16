from graphics import Point,Line,GraphWin
from requests import get
from json import loads

def getLines():
    request = get("https://api.noopschallenge.com/vexbot?count=100&width=800&height=500&connected=1").text
    vectors = loads(request)['vectors']
    lines = []
    
    win = GraphWin('hexbot',900,600)
    for i in range (0,100):
        lineProps = vectors[i]
        a_ = lineProps['a']
        a = Point(a_['x']+50,a_['y']+50)
        b_ = lineProps['b']
        b = Point(b_['x']+50,b_['y']+50)
        speed = lineProps['speed']

        line = Line(a,b)
        lines.append(line)
    return lines
    
def main():
    getLines()


main()