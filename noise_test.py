def noise(x):
    x = x + 10000
    return (int(3.141927 * (x << 11) * x**2) % 100) / 100.0
    
def noise(x, y):
    x = x + 10000
    y = y + 10000
    return ((int(7.567243 * (x << 7) * x**2) % 100) + (int(13.239576 * (y << 9) * y**3) % 100)) / 200.0
     
for x in range(0, 4):
    for y in range(0, 4):
        print "f(" + str(x) + ", " + str(y) + ") = " + str(noise(x, y))
        print "f(" + str(-x) + ", " + str(-y) + ") = " + str(noise(-x, -y))
        print