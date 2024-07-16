import cython
cimport cython
from libc.math cimport sqrt, abs, cos, sin, pi
from cpython cimport array
import array
import itertools

ctypedef list[tuple] listatupla
ctypedef list[list] listalista

ctypedef fused contis:
    listatupla
    listalista

ctypedef fused pythoncontainer:
    list
    tuple

cpdef list[tuple] get_circle_coordinates(Py_ssize_t x, Py_ssize_t y, Py_ssize_t r):
    """
    Generates the coordinates of a circle's perimeter based on its center and radius.

    Args:
    x (Py_ssize_t): The x-coordinate of the circle's center.
    y (Py_ssize_t): The y-coordinate of the circle's center.
    r (Py_ssize_t): The radius of the circle.

    Returns:
    list: A list of tuples representing the coordinates on the perimeter of the circle.
    """
    cdef:
        double a = int(y)
        double b = int(x)
        double stepSize = 0.005
        set positions = set()
        double t
    t = 0
    while t < 2 * pi:
        positions.add((int(r * cos(t) + a), int(r * sin(t) + b)))
        t += stepSize
    return list(positions)

cpdef list[tuple] get_rectangle_coordinates_surface(Py_ssize_t x, Py_ssize_t y, Py_ssize_t width, Py_ssize_t height):
    """
    Generates the boundary coordinates of a rectangle.

    Args:
    x (Py_ssize_t): The x-coordinate of the rectangle's upper left corner.
    y (Py_ssize_t): The y-coordinate of the rectangle's upper left corner.
    width (Py_ssize_t): The width of the rectangle.
    height (Py_ssize_t): The height of the rectangle.

    Returns:
    list: A list of tuples representing the boundary coordinates of the rectangle.
    """
    cdef:
        set[tuple] positions  = set()
        Py_ssize_t i, j
    for i in range(width + 1):
        positions.add((x + i, y))
        positions.add((x + i, y + height))

    for j in range(height + 1):
        positions.add((x, y + j))
        positions.add((x + width, y + j))

    return list(positions)

cpdef list[tuple] get_circle_coordinates_surface(Py_ssize_t x_center, Py_ssize_t y_center, Py_ssize_t radius):
    """
    Generates the boundary coordinates of a circle using the midpoint circle drawing algorithm.

    Args:
    x_center (Py_ssize_t): The x-coordinate of the circle's center.
    y_center (Py_ssize_t): The y-coordinate of the circle's center.
    radius (Py_ssize_t): The radius of the circle.

    Returns:
    list: A list of tuples representing the boundary coordinates of the circle.
    """
    cdef:
        Py_ssize_t x = radius
        Py_ssize_t y = 0
        set[tuple] positions = set()
        Py_ssize_t p
    positions.add((x_center + x, y_center + y))
    if radius > 0:
        positions.add((x_center - x, y_center + y))
        positions.add((x_center + y, y_center + x))
        positions.add((x_center - y, y_center + x))
    p = 1 - radius
    while x > y:
        y += 1
        if p <= 0:
            p = p + 2 * y + 1
        else:
            x -= 1
            p = p + 2 * y - 2 * x + 1
        if x < y:
            break
        positions.add((x_center + x, y_center + y))
        positions.add((x_center - x, y_center + y))
        positions.add((x_center + x, y_center - y))
        positions.add((x_center - x, y_center - y))
        if x != y:
            positions.add((x_center + y, y_center + x))
            positions.add((x_center - y, y_center + x))
            positions.add((x_center + y, y_center - x))
            positions.add((x_center - y, y_center - x))

    return list(positions)

cpdef list[tuple] get_ellipse_coordinates_surface(Py_ssize_t x_center, Py_ssize_t y_center, Py_ssize_t rx, Py_ssize_t ry):
    """
    Generates the boundary coordinates of an ellipse using the midpoint ellipse drawing algorithm.

    Args:
    x_center (Py_ssize_t): The x-coordinate of the ellipse's center.
    y_center (Py_ssize_t): The y-coordinate of the ellipse's center.
    rx (Py_ssize_t): The x-radius of the ellipse.
    ry (Py_ssize_t): The y-radius of the ellipse.

    Returns:
    list: A list of tuples representing the boundary coordinates of the ellipse.
    """
    cdef:
        set[tuple] positions = set()
        Py_ssize_t x = 0
        Py_ssize_t y = ry
        double d1 = ry**2 - rx**2 * ry + 0.25 * rx**2
        double dx = 2 * ry**2 * x
        double dy = 2 * rx**2 * y
        double d2

    while dx < dy:
        positions.add((x_center + x, y_center + y))
        positions.add((x_center - x, y_center + y))
        positions.add((x_center + x, y_center - y))
        positions.add((x_center - x, y_center - y))
        if d1 < 0:
            x += 1
            dx = 2 * ry**2 * x
            d1 += dx + ry**2
        else:
            x += 1
            y -= 1
            dx = 2 * ry**2 * x
            dy = 2 * rx**2 * y
            d1 += dx - dy + ry**2

    d2 = (ry**2) * ((x + 0.5) ** 2) + (rx**2) * ((y - 1) ** 2) - (rx**2) * (ry**2)

    while y >= 0:
        positions.add((x_center + x, y_center + y))
        positions.add((x_center - x, y_center + y))
        positions.add((x_center + x, y_center - y))
        positions.add((x_center - x, y_center - y))
        if d2 > 0:
            y -= 1
            dy = 2 * rx**2 * y
            d2 += rx**2 - dy
        else:
            y -= 1
            x += 1
            dx = 2 * ry**2 * x
            dy = 2 * rx**2 * y
            d2 += dx - dy + rx**2

    return list(positions)

cpdef list[tuple] bresenham_line(Py_ssize_t x1, Py_ssize_t y1, Py_ssize_t x2, Py_ssize_t y2):
    """
    Computes the points of a line from (x1, y1) to (x2, y2) using Bresenham's line algorithm.

    Args:
    x1, y1, x2, y2 (Py_ssize_t): Start and end coordinates of the line.

    Returns:
    list: List of tuples representing the coordinates of the line.
    """
    cdef:
        list positions = []
        Py_ssize_t dx = abs(x2 - x1)
        Py_ssize_t dy = abs(y2 - y1)
        Py_ssize_t sx = 1 if x1 < x2 else -1
        Py_ssize_t sy = 1 if y1 < y2 else -1
        Py_ssize_t err = dx - dy
        Py_ssize_t e2
    while True:
        positions.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    return positions

cpdef list[tuple] get_polygon_coordinates_surface(contis vertices):
    """
    Generates the boundary coordinates of a polygon defined by its vertices.

    Args:
    vertices (contis): A list or tuple of tuples representing the vertices of the polygon.

    Returns:
    list: A list of tuples representing the boundary coordinates of the polygon.
    """
    cdef:
        set positions = set()
        Py_ssize_t num_vertices = len(vertices)
        Py_ssize_t i, x1, x2, y1, y2
    for i in range(num_vertices):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % num_vertices]
        positions.update(bresenham_line(x1, y1, x2, y2))
    return list(positions)

cdef Py_ssize_t convex_hull_left_index(list points):
    """
    Finds the index of the leftmost point in a list of points.

    Args:
    points (list): A list of tuples representing the points.

    Returns:
    Py_ssize_t: The index of the leftmost point.
    """
    cdef:
        Py_ssize_t minn = 0
        Py_ssize_t i
        Py_ssize_t len_points = len(points)
    for i in range(1, len_points):
        if points[i][0] < points[minn][0]:
            minn = i
        elif points[i][0] == points[minn][0]:
            if points[i][0] > points[minn][0]:
                minn = i
    return minn

cdef Py_ssize_t convex_hull_orientation(list points, Py_ssize_t p, Py_ssize_t q, Py_ssize_t r):
    """
    Determines the orientation of the triplet (p, q, r) for convex hull calculations.

    Args:
    points (list): A list of tuples representing the points.
    p, q, r (Py_ssize_t): Indices in the list of points representing a triplet.

    Returns:
    int: 0 if collinear, 1 if clockwise, 2 if counterclockwise.
    """
    cdef:
        Py_ssize_t val

    val = (points[q][1] - points[p][1]) * (points[r][0] - points[q][0]) - (points[q][0] - points[p][0]) * (points[r][1] - points[q][1])

    if val == 0:
        return 0
    elif val > 0:
        return 1
    else:
        return 2

cpdef list[tuple] convex_hull(contis points):
    """
    Computes the convex hull of a set of points.

    Args:
    points (contis): A list or tuple of tuples representing the points.

    Returns:
    list: A list of tuples representing the vertices of the convex hull.
    """
    cdef:
        Py_ssize_t n = len(points)
        Py_ssize_t l, p, q, i, resultcheck
        list hull = []
    if n < 3:
        return []
    l = convex_hull_left_index(points)
    p = l
    q = 0
    while True:
        hull.append(p)
        q = (p + 1) % n

        for i in range(n):
            resultcheck = convex_hull_orientation(points, p, i, q)
            if resultcheck == 2:
                q = i
        p = q
        if p == l:
            break
    return [((points[each][0], points[each][1])) for each in hull]

cpdef list groupcoords_asc_desc(list coordlist, Py_ssize_t xtolerance=-2):
    """
    Groups coordinates in ascending and descending order based on their x-values, considering a specified tolerance.

    Args:
    coordlist (list): A list of tuples, each containing x and y coordinates (x, y).
    xtolerance (Py_ssize_t): The tolerance level for x-coordinate grouping. Default is -2.

    Returns:
    list: A list of grouped coordinates in ascending and then descending order of x-values.
    """
    cdef:
        Py_ssize_t len_coordlist = len(coordlist)
        Py_ssize_t last_index_coordlist = len_coordlist - 1
        Py_ssize_t indexskip = -1
        list[tuple] resultlist_forward = []
        list last_listtmp
        Py_ssize_t coordindex1, x_coord_old, y_coord_old, highestx, coordindex2, x_coord_new, y_coord_new, difference_x, difference_x_highest
    for coordindex1 in range(last_index_coordlist):
        if coordindex1 <= indexskip:
            continue
        x_coord_old = coordlist[coordindex1][0]
        y_coord_old = coordlist[coordindex1][1]
        highestx = x_coord_old
        resultlist_forward.append([(coordindex1, (x_coord_old, y_coord_old))])
        for coordindex2 in range(coordindex1, len_coordlist):
            x_coord_new = coordlist[coordindex2][0]
            if x_coord_new > highestx:
                highestx = x_coord_new
            y_coord_new = coordlist[coordindex2][1]
            difference_x = x_coord_new - x_coord_old
            difference_x_highest = x_coord_new - highestx
            if difference_x <= 0:
                if difference_x == 0:
                    if coordindex2 != coordindex1:
                        resultlist_forward[len(resultlist_forward)-1].append(
                            (coordindex2, (x_coord_new, y_coord_new))
                        )
                elif (
                    difference_x > xtolerance
                    and difference_x_highest > xtolerance
                    and len(resultlist_forward[len(resultlist_forward)-1]) > 1
                ):
                    last_listtmp = resultlist_forward[len(resultlist_forward)-1]
                    last_listtmp[len(last_listtmp)-1] = (
                        coordindex2,
                        (
                            x_coord_new,
                            y_coord_new,
                        ),
                    )

                else:
                    break

            else:
                resultlist_forward[len(resultlist_forward)-1].append((coordindex2, (x_coord_new, y_coord_new)))
            indexskip = coordindex2
            x_coord_old = x_coord_new
            y_coord_old = y_coord_new
    return resultlist_forward

def calculate_missing_coords_and_fill_all_holes(
        list coordlist,
        Py_ssize_t xtolerance=-2,
        Py_ssize_t minvalue_x=0,
        Py_ssize_t minvalue_y=0,
        Py_ssize_t maxvalue_x=0,
        Py_ssize_t maxvalue_y=0,
        bint check_minvalue_x=False,
        bint check_maxvalue_x=False,
        bint check_minvalue_y=False,
        bint check_maxvalue_y=False,):
    """
    Calculates and fills in missing coordinates to create a continuous path between points.

    Args:
    coordlist (list): A list of tuples representing coordinates.
    xtolerance (Py_ssize_t): Tolerance for grouping coordinates.
    minvalue_x, minvalue_y, maxvalue_x, maxvalue_y (Py_ssize_t): Limits to filter coordinates.
    check_minvalue_x, check_maxvalue_x, check_minvalue_y, check_maxvalue_y (bint): Flags to apply limits.

    Returns:
    list: A list of tuples representing the continuous path of coordinates.
    """
    cdef:
        dict calca
        list allco = []
        list allcoallfinal = []
        dict v
        Py_ssize_t i
    calca = calculate_missing_coords(
            coordlist=coordlist,
            xtolerance=xtolerance,
            minvalue_x=minvalue_x,
            minvalue_y=minvalue_y,
            maxvalue_x=maxvalue_x,
            maxvalue_y=maxvalue_y,
            check_minvalue_x=check_minvalue_x,
            check_maxvalue_x=check_maxvalue_x,
            check_minvalue_y=check_minvalue_y,
            check_maxvalue_y=check_maxvalue_y,)
    for v in calca.values():
        allco.append(v["interp_coords"])
    for i in range(len(allco) - 1):
        #if not allco[i]:
            #continue
        #if len(allco[i][len(allco[i]) - 1]) <2:
            #continue
        #if len(allco[i + 1]) <2:
            #continue
        coli = get_coords_of_line(
            allco[i][len(allco[i]) - 1][0],
            allco[i][len(allco[i]) - 1][1],
            allco[i + 1][0][0],
            allco[i + 1][0][1],
        )
        allcoallfinal.extend(allco[i])
        allcoallfinal.extend(coli)
    allcoallfinal.extend(allco[len(allco)-1])
    return allcoallfinal

def calculate_missing_coords(
        list coordlist,
        Py_ssize_t xtolerance=-2,
        Py_ssize_t minvalue_x=0,
        Py_ssize_t minvalue_y=0,
        Py_ssize_t maxvalue_x=0,
        Py_ssize_t maxvalue_y=0,
        bint check_minvalue_x=False,
        bint check_maxvalue_x=False,
        bint check_minvalue_y=False,
        bint check_maxvalue_y=False,):
    """
    Calculates the coordinates that fit within specified limits and groups them by proximity.

    Args:
    coordlist (list): A list of tuples, each containing x and y coordinates.
    xtolerance (Py_ssize_t): The tolerance level for x-coordinate grouping. Default is -2.
    minvalue_x, maxvalue_x, minvalue_y, maxvalue_y (Py_ssize_t): Minimum and maximum values for x and y coordinates.
    check_minvalue_x, check_maxvalue_x, check_minvalue_y, check_maxvalue_y (bint): Flags to check the specified min and max values.

    Returns:
    dict: A dictionary with interpolated coordinates and input coordinates.
    """
    cdef:
        Py_ssize_t lengr = len(coordlist) - 1
        list[tuple] alltogether = sorted([
            [(int(y[0]), (y[1]), True) for y in x]
            for x in groupcoords_asc_desc(coordlist, xtolerance=xtolerance)
        ] + [
            list(reversed([(int(lengr - y[0]), (y[1]), False) for y in x]))
            for x in groupcoords_asc_desc(list(reversed(coordlist)), xtolerance=xtolerance)
        ], key=lambda x: x[0][0])
        Py_ssize_t alltogether_len=len(alltogether)
        list[list] allinonelistgrouped = [[]]
        set indexchecker = set()
        Py_ssize_t lastaddedindex = -1
        Py_ssize_t da,element_index,inid
        dict coordinateresults={}
        list[tuple[Py_ssize_t]] resnew
    for da in range(alltogether_len):
        if len(allinonelistgrouped[len(allinonelistgrouped)-1]) > 0:
            allinonelistgrouped.append([])
        for element_index in range(len(alltogether[da])):
            if alltogether[da][element_index][0] not in indexchecker and alltogether[da][element_index][0] > lastaddedindex:
                indexchecker.add(alltogether[da][element_index][0])
                lastaddedindex = alltogether[da][element_index][0]
                allinonelistgrouped[len(allinonelistgrouped)-1].append(alltogether[da][element_index])
    for inid in range(len(allinonelistgrouped)):
        if not allinonelistgrouped[inid]:
            continue
        resnew = cubic_interp1d(
            [ll[1] for ll in allinonelistgrouped[inid]],
            minvalue_x=minvalue_x,
            minvalue_y=minvalue_y,
            maxvalue_x=maxvalue_x,
            maxvalue_y=maxvalue_y,
            check_minvalue_x=check_minvalue_x,
            check_maxvalue_x=check_maxvalue_x,
            check_minvalue_y=check_minvalue_y,
            check_maxvalue_y=check_maxvalue_y,
        )
        if not allinonelistgrouped[inid][0][2]:
            resnew.reverse()
        coordinateresults[inid]={'interp_coords': resnew, 'input_indices':[allinonelistgrouped[inid][iind][0] for iind in range(len(allinonelistgrouped[inid]))],'is_reversed':not allinonelistgrouped[inid][0][2]}
    return coordinateresults

cpdef list[tuple[Py_ssize_t]] get_coords_of_line(Py_ssize_t x1, Py_ssize_t y1, Py_ssize_t x2, Py_ssize_t y2):
    """
    Computes the points of a line from (x1, y1) to (x2, y2) using Bresenham's line algorithm.

    Args:
    x1, y1, x2, y2 (Py_ssize_t): Start and end coordinates of the line.

    Returns:
    list: List of tuples representing the coordinates of the line.
    """
    cdef:
        list[tuple[Py_ssize_t]] points = []
        bint issteep = abs(y2 - y1) > abs(x2 - x1)
        bint rev = False
        Py_ssize_t deltax, deltay, error, y, ystep,x
    if x1==x2 and y1==y2:
        return [(x1,y1)]
    if x1==x2:
        return [(x1,i) for i in range(y1,y2+1,int(abs(y2-y1)/(y2-y1)))]
    if y1==y2:
        return [(i,y1) for i in range(x1,x2+1,int(abs(x2-x1)/(x2-x1)))]
    if issteep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        rev = True
    deltax = x2 - x1
    deltay = abs(y2 - y1)
    error = int(deltax / 2)
    y = y1
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
    for x in range(x1, x2 + 1):
        if issteep:
            points.append((y, x))
        else:
            points.append((x, y))
        error -= deltay
        if error < 0:
            y += ystep
            error += deltax
    if rev:
        points.reverse()
    return points

def logsplit(lst):
    """
    Splits a list into progressively larger chunks based on logarithmic growth.

    Args:
    lst (list): The list to be split.

    Yields:
    list: Sublists of increasing size.
    """
    iterator = iter(lst)
    for n, e in enumerate(iterator):
        yield list(itertools.chain([e], itertools.islice(iterator, n)))

cpdef list[double] _logspace(double stop, Py_ssize_t num):
    """
    Generates logarithmically spaced numbers between 1 and a specified stop value.

    Args:
    stop (double): The end value of the sequence.
    num (Py_ssize_t): Number of values to generate.

    Returns:
    list: A list of doubles containing the log-spaced values.
    """
    cdef:
        double ratio = stop ** (1 / (float(num) - 1))
        list[double] resultlist=[]
        Py_ssize_t i
    for i in range(num):
        if i == num - 1:
            resultlist.append(stop)
            break
        resultlist.append(ratio ** i)
    return resultlist

def logspace(start, stop, Py_ssize_t num=10):
    """
    Generates numbers spaced evenly on a log scale between start and stop.

    Args:
    start (double): The starting value of the sequence.
    stop (double): The end value of the sequence.
    num (Py_ssize_t): Number of values to generate. Default is 10.

    Returns:
    list: A list of doubles containing the log-spaced values.
    """
    cdef:
        list[double] resultlist=[]
        double fstop = float(stop)
        double fstart = float(start)
        double diff = fstop - fstart
        Py_ssize_t i
        list[double] logvars=(_logspace(fstop, num))
        Py_ssize_t logvarslen=len(logvars)
    for i in range(logvarslen):
        if i == 0:
            resultlist.append(fstart)
        elif i == num:
            resultlist.append(fstop)
        else:
            resultlist.append(fstart + logvars[i] * diff / fstop)
    return resultlist

cpdef list[double] linspace(double start, double stop, Py_ssize_t number, bint endpoint=True):
    """
    Generates linearly spaced numbers between start and stop.

    Args:
    start (double): The starting value of the sequence.
    stop (double): The end value of the sequence.
    number (Py_ssize_t): Number of values to generate.
    endpoint (bint): If True, the stop is the last value, otherwise it is not included.

    Returns:
    list: A list of doubles containing the linearly spaced values.
    """
    cdef:
        double num = float(number)
        double start1 = float(start)
        double stop1 = float(stop)
        double step
        list[double] results=[]
        Py_ssize_t i

    if number == 1:
        return [num]
    if endpoint:
        step = (stop1 - start1) / (num - 1)
    else:
        step = (stop1 - start1) / num
    for i in range(number):
        results.append(start1 + step * i)
    return results

cpdef list difflist(list lst):
    """
    Computes the difference between consecutive elements in a list.

    Args:
    lst (list): Array of integer values.

    Returns:
    list: List of differences between consecutive elements.
    """
    cdef:
        Py_ssize_t size = len(lst) - 1
        list r = [0] * size
        Py_ssize_t i

    for i in range(size):
        r[i] = lst[i + 1] - lst[i]
    return r

cdef list[Py_ssize_t] diff(Py_ssize_t[:] lst):
    """
    Computes the difference between consecutive elements in a list.

    Args:
    lst (array[Py_ssize_t]): Array of integer values.

    Returns:
    list: List of differences between consecutive elements.
    """
    cdef:
        Py_ssize_t size = len(lst) - 1
        list[Py_ssize_t] r = [0] * size
        Py_ssize_t i
    for i in range(size):
        r[i] = lst[i + 1] - lst[i]
    return r

cdef list[list[Py_ssize_t],Py_ssize_t,Py_ssize_t,bint] _parse_coords(
    list[tuple] x_y_coordinates,
    Py_ssize_t minvalue_x=0,
    Py_ssize_t minvalue_y=0,
    Py_ssize_t maxvalue_x=0,
    Py_ssize_t maxvalue_y=0,
    bint check_minvalue_x=False,
    bint check_maxvalue_x=False,
    bint check_minvalue_y=False,
    bint check_maxvalue_y=False,
):
    """
    Parses coordinate data and applies constraints based on minimum and maximum values for x and y.

    Args:
    x_y_coordinates (list): List of tuples containing x and y coordinates.
    minvalue_x, minvalue_y, maxvalue_x, maxvalue_y (Py_ssize_t): Minimum and maximum values for x and y coordinates to filter.
    check_minvalue_x, check_maxvalue_x, check_minvalue_y, check_maxvalue_y (bint): Flags to check for min and max values.

    Returns:
    list: List containing the parsed coordinates, applied constraints, and a status indicating if constraints were met.
    """
    cdef:
        list[tuple[Py_ssize_t]] onlyco
        Py_ssize_t x_y_coordinates_len=len(x_y_coordinates)
        tuple xycoordinate_index
        Py_ssize_t oneco_index
        list[Py_ssize_t] all_x_coords=[]
        list[Py_ssize_t] all_y_coords=[]
        dict[Py_ssize_t,Py_ssize_t] maxdict = {}
        Py_ssize_t minvalue_x_final,maxvalue_x_final,add_dummys
        bint isbad = False
        Py_ssize_t maxvalue_first_element_y,minvalue_first_element_y
        list lindspaced =[]
    onlyco = sorted([(int(ll[0]),int(ll[1])) for ll in x_y_coordinates], key=lambda x: x[0])
    maxvalue_first_element_y=onlyco[0][1]
    minvalue_first_element_y=onlyco[0][1]
    for oneco_index in range(x_y_coordinates_len):
        if onlyco[oneco_index][0] not in maxdict:
            maxdict[onlyco[oneco_index][0]] = onlyco[oneco_index][1]
        else:
            if onlyco[oneco_index][0] != onlyco[0][0]:
                if maxdict[onlyco[oneco_index][0]] < onlyco[oneco_index][1]:
                    maxdict[onlyco[oneco_index][0]] = onlyco[oneco_index][1]
            else:
                if maxdict[onlyco[oneco_index][0]] > onlyco[oneco_index][1]:
                    maxdict[onlyco[oneco_index][0]] = onlyco[oneco_index][1]
                    minvalue_first_element_y= onlyco[oneco_index][1]
                if maxvalue_first_element_y < onlyco[oneco_index][1]:
                    maxvalue_first_element_y=onlyco[oneco_index][1]

    for xycoordinate_index in maxdict.items():
        if check_minvalue_x:
            if xycoordinate_index[0] < minvalue_x:
                continue
        if check_maxvalue_x:
            if xycoordinate_index[0] > maxvalue_x:
                continue
        if check_minvalue_y:
            if xycoordinate_index[1] < minvalue_y:
                continue
        if check_maxvalue_y:
            if xycoordinate_index[1] > maxvalue_y:
                continue
        all_x_coords.append( xycoordinate_index[0])
        all_y_coords.append( xycoordinate_index[1])
    minvalue_x_final=all_x_coords[0]
    maxvalue_x_final=all_x_coords[len(all_x_coords)-1]
    if minvalue_x_final==maxvalue_x_final:
        isbad=True
        if maxvalue_first_element_y-minvalue_first_element_y>0:
            for add_dummys in range(1,maxvalue_first_element_y-minvalue_first_element_y):
                maxvalue_x_final=maxvalue_x_final+add_dummys
                all_x_coords.append(maxvalue_x_final)
            all_y_coords.extend([int(floatval) for floatval in linspace(minvalue_first_element_y,maxvalue_first_element_y,maxvalue_first_element_y-minvalue_first_element_y)])
        else:
            all_x_coords.append(minvalue_x_final+1)
            maxvalue_x_final=maxvalue_x_final+1
            all_y_coords.append(maxvalue_first_element_y)
    return  [all_x_coords,all_y_coords,minvalue_x_final,maxvalue_x_final,isbad]

cpdef list[tuple[Py_ssize_t]] cubic_interp1d(
    x_y_coordinates,
    Py_ssize_t minvalue_x=0,
    Py_ssize_t minvalue_y=0,
    Py_ssize_t maxvalue_x=0,
    Py_ssize_t maxvalue_y=0,
    bint check_minvalue_x=False,
    bint check_maxvalue_x=False,
    bint check_minvalue_y=False,
    bint check_maxvalue_y=False,
):
    """
    Performs cubic interpolation on a given set of x and y coordinates.

    Args:
    x_y_coordinates (list): List of tuples containing x and y coordinates.
    minvalue_x, minvalue_y, maxvalue_x, maxvalue_y (Py_ssize_t): Minimum and maximum values for x and y coordinates.
    check_minvalue_x, check_maxvalue_x, check_minvalue_y, check_maxvalue_y (bint): Flags to check for min and max values.

    Returns:
    list: A list of tuples containing interpolated x and y coordinates.
    """
    cdef:

        list xaslist_yaslist=_parse_coords(
        x_y_coordinates,
        minvalue_x=minvalue_x,
        minvalue_y=minvalue_y,
        maxvalue_x=maxvalue_x,
        maxvalue_y=maxvalue_y,
        check_minvalue_x=check_minvalue_x,
        check_maxvalue_x=check_maxvalue_x,
        check_minvalue_y=check_minvalue_y,
        check_maxvalue_y=check_maxvalue_y,)

        array.array full_x=array.array("q",xaslist_yaslist[0])
        array.array full_y=array.array("q",xaslist_yaslist[1])
        Py_ssize_t minxvalue = xaslist_yaslist[2]
        Py_ssize_t maxxvalue = xaslist_yaslist[3]
        bint isbad = xaslist_yaslist[4]
        Py_ssize_t size = len(full_x)
        Py_ssize_t isize = size - 1
        Py_ssize_t min_val = 1
        Py_ssize_t max_val = size - 1
        Py_ssize_t[:] x = full_x
        Py_ssize_t[:] y = full_y
        array.array full_output = array.array("q", list(range(minxvalue, maxxvalue, 1)))
        Py_ssize_t[:] output  = full_output
        Py_ssize_t x0len = len(output)
        array.array full_xdiff = array.array("q", diff(x))
        Py_ssize_t[:] xdiff= full_xdiff
        array.array full_ydiff = array.array("q", diff(y))
        Py_ssize_t[:] ydiff= full_ydiff
        array.array full_liv1 = array.array("d", [0] * size)
        double[:] liv1= full_liv1
        array.array full_liv2 = array.array("d", [0] * (size - 1))
        double[:] liv2= full_liv2
        array.array full_z = array.array("d", [0] * size)
        double[:] z= full_z
        array.array full_x0 = array.array("q", output)
        Py_ssize_t[:] x0= full_x0
        array.array full_index = array.array("q", [0] * x0len)
        Py_ssize_t[:] index= full_index
        Py_ssize_t indexlen=len(full_index)
        array.array full_xi1 = array.array("d", [0] * x0len)
        double[:] xi1= full_xi1
        array.array full_xi0 = array.array("d", [0] * x0len)
        double[:] xi0= full_xi0
        array.array full_yi1 = array.array("d", [0] * x0len)
        double[:] yi1= full_yi1
        array.array full_yi0 = array.array("d", [0] * x0len)
        double[:] yi0= full_yi0
        array.array full_zi1 = array.array("d", [0] * x0len)
        double[:] zi1= full_zi1
        array.array full_zi0 = array.array("d", [0] * x0len)
        double[:] zi0= full_zi0
        array.array full_hi1 = array.array("d", [0] * x0len)
        double[:] hi1= full_hi1
        array.array full_resultsasint = array.array("q", [0] * x0len)
        Py_ssize_t len_resultsasint=len(full_resultsasint)
        Py_ssize_t[:] resultsasint = full_resultsasint
        Py_ssize_t xdiff_last_index=len(xdiff)-1
        Py_ssize_t indexcounter = 0
        Py_ssize_t i,x0index,j,num_index
        double nboundry

    liv1[0] = sqrt(2 * xdiff[0])
    for i in range(1, size - 1, 1):
        liv2[i] = xdiff[i - 1] / liv1[i - 1]
        liv1[i] = sqrt(2 * (xdiff[i - 1] + xdiff[i]) - liv2[i - 1] * liv2[i - 1])
        nboundry = 6 * (ydiff[i] / xdiff[i] - ydiff[i - 1] / xdiff[i - 1])
        z[i] = (nboundry - liv2[i - 1] * z[i - 1]) / liv1[i]
    liv2[isize - 1] = xdiff[xdiff_last_index] / liv1[isize - 1]
    liv1[isize] = sqrt(2 * xdiff[xdiff_last_index] - liv2[isize - 1] * liv2[isize - 1])
    nboundry = 0.0
    z[isize] = (nboundry - liv2[isize - 1] * z[isize - 1]) / liv1[isize]
    z[isize] = z[isize] / liv1[isize]
    for i in range(size - 2, -1, -1):
        z[i] = (z[i] - liv2[i - 1] * z[i + 1]) / liv1[i]

    for x0index in range(x0len):
        for i in range(size):
            if x0[x0index] <= x[i]:
                index[indexcounter] = i
                indexcounter += 1
                break
        else:
            index[indexcounter] = size
            indexcounter += 1

    for i in range(indexlen):
        if index[i] < min_val:
            index[i] = min_val
        elif index[i] > max_val:
            index[i] = max_val
    for num_index in range(x0len):
        xi1[num_index] = x[index[num_index]]
        yi1[num_index] = y[index[num_index]]
        zi1[num_index] = z[index[num_index]]
        xi0[num_index] = x[index[num_index] - 1]
        yi0[num_index] = y[index[num_index] - 1]
        zi0[num_index] = z[index[num_index] - 1]
        hi1[num_index] = xi1[num_index] - xi0[num_index]
    for j in range(len_resultsasint):
        resultsasint[j] = int(
            zi0[j] / (6 * hi1[j]) * (xi1[j] - x0[j]) ** 3
            + zi1[j] / (6 * hi1[j]) * (x0[j] - xi0[j]) ** 3
            + (yi1[j] / hi1[j] - zi1[j] * hi1[j] / 6) * (x0[j] - xi0[j])
            + (yi0[j] / hi1[j] - zi0[j] * hi1[j] / 6) * (xi1[j] - x0[j])
        )
    if isbad:
        for x0index in range(x0len):
            output[x0index]=minxvalue
        return sorted(set((zip(output, resultsasint))))
    return list(zip(output, resultsasint))
