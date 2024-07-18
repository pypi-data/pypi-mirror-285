import numpy as np
import copy
class Point():

    def __init__(self, newx, newy, newz):
        self.x = newx
        self.y = newy
        self.z = newz

    def Update(self, otherx, othery, otherz):
        self.x = otherx
        self.y = othery
        self.z = otherz


    def mod(self):
        return pow((self.x ** 2) + (self.y ** 2) + (self.z ** 2), 0.5)
    def dot(self, v):
        return (self.x * v.x) + (self.y * v.y) + (self.z * v.z)
    def cross(self, u):
        ##Crossproduct
        return Point(
            self.y * u.z - self.z * u.y,
            self.z * u.x - self.x * u.z,
            self.x * u.y - self.y * u.x)
    def __pow__(v, u):
        ##Crossproduct
        return Point(
            v.y * u.z - v.z * u.y,
            v.z * u.x - v.x * u.z,
            v.x * u.y - v.y * u.x)
    def __add__(v, u):
        return Point(v.x + u.x, v.y + u.y, v.z + u.z)
    def __sub__(v, u):
        return Point(v.x - u.x, v.y - u.y, v.z - u.z)
    def __mul__(self, a):
        return Point(self.x*a,self.y*a,self.z*a)
    def __rmul__(self, a:float):
        return Point(self.x*a,self.y*a,self.z*a)
    def __truediv__(self, a:float):
        return Point(self.x/a,self.y/a,self.z/a)
    def __eq__(self, other):
        if isinstance(other, Point):
            return (self.x==other.x and self.y==other.y and self.z==other.z)
        else:
            return False
    def __str__(self):
        return "{x},{y},{z}".format(x = self.x, y = self.y, z = self.z)
    def __eq__(self, other):
        if isinstance(other, Point):
            if self.x == other.x and self.y == other.y and self.z == other.z:
                return True
        return False

class Perimeter():

    def __init__(self, *args, **kwargs):
        self.normal = Point(0,0,0)
        self.area = Point(0,0,0)
        self.total_length = 0
        self.blend_points = np.array([])
        if not "full_init" in kwargs.keys():
            full_init = True
        else:
            full_init = kwargs["full_init"]
        if args:
            if not isinstance(args[0][0], Point):
                ## np array of classes seems to point (memory level) at
                ##the first element only!!!
                ## This is a serious problem, keep an eye on it!!
                self.points = [Point(0,0,0) for i in range(args[0].shape[0])]
                for i in range(args[0].shape[0]):
                    self.points[i].Update(
                        args[0][i][0],
                        args[0][i][1],
                        args[0][i][2]
                        )
                ## Now back to numpy arrays...
                self.points = np.array(self.points)
            else:
                self.points = args[0]
        else:
            self.points = np.empty(0)
        if self.points.shape[0]>1 and full_init:
            self.fix_intersection()
            self.area_vec()
            self.compute_length()

    def append(self, np_array):
        self.points = np.append(self.points, np.array([np_array]), axis=0)
    def fix_distance(self, subdivision = 1):
        ## Creates new points between points that are too
        ##far apart from each other
        counter = 0
        distance = np.array([0.]*(self.points.shape[0]-1), dtype=float)

        for i in range(self.points.shape[0]-1):
            distance[i] = (self.points[i]-self.points[i+1]).mod()**2

        d0 = np.sum(distance)/(self.points.shape[0])
        aux = 0
        for i in range(self.points.shape[0]-1):
            if distance[i] >= (d0*subdivision):
                factor = int(distance[i]/d0)
                points_list = np.array([Point(0,0,0)]*(factor-1))
                for j in range(1, factor):
                    np_index = j/factor
                    new_point = (self.points[i+counter]-self.points[i+1+counter])*(np_index)
                    new_point += self.points[i+counter+1]
                    points_list[j-1] = new_point
                    aux += 1
                points_list = np.flip(points_list, axis=0)
                self.points = np.insert(self.points, i+counter+1, points_list)
                counter += aux
                aux = 0
    def subdivide(self):
        ## Creates new points no matter what
        counter = 0
        for i in range(self.points.shape[0]-2):
            new_point = (self.points[i+counter+1]-self.points[i+counter])/2
            new_point += self.points[i+counter]
            self.points = np.insert(self.points, i+counter+1, [new_point])
            counter += 1
    def spread_sulci(self,close=1e-1):
        def move(index_i, index_j):
            indexes = [index_i,index_j]
            for di,dj in zip(indexes,indexes[::-1]):
                dir1 = self.points[di+1]-self.points[di]
                dir2 = self.points[di-1]-self.points[di]
                new_points = [close*dir1+self.points[di],
                            close*dir2+self.points[di]]
                test1 = self.find_intersection(new_points[0],new_points[1],
                                self.points[dj],self.points[dj+1])
                test2 = self.find_intersection(new_points[0],new_points[1],
                                self.points[dj],self.points[dj-1])
                if not test1 and not test2:
                    break
            return new_points[::-1],di
        counter = 0
        for i in range(self.points.shape[0]-3):
            index_i = i+counter
            for j in range(i+2,self.points.shape[0]-1-counter):

                dist = (self.points[index_i]-self.points[j+counter]).mod()
                if dist<=close:
                    new_points,chosen_index = move(index_i, j+counter)
                    self.points = np.insert(self.points, chosen_index+1, new_points)
                    self.points = np.delete(self.points, chosen_index, axis=0)
                    counter += 1
                    break
        print(counter)
    def remove_by_angle(self,min_angle=np.pi/180):
        """
            Remove points that are closer than delta times the mean distance from
        each other.
        """
        aux = self.points
        counter = 0
        if self.points[0]==self.points[-1]:
            correction = 1
        else:
            correction = 0
        for i in range(self.points.shape[0]-correction):
            va = self.points[i-1] - self.points[i]
            vb = self.points[i] - self.points[i+1]
            if np.arccos(va.dot(vb)) < min_angle and np.arccos(va.dot(vb))>0:
                aux = np.delete(aux,i-counter)
                counter += 1
        self.points = aux
    def remove_overlap(self,delta=0.0):
        """
            Remove points that are closer than delta times the mean distance from
        each other.
        """
        aux = copy.deepcopy(self.points)
        counter = 0
        mean = 0
        for i in range(self.points.shape[0]-1):
            mean += (self.points[i]-self.points[i+1]).mod()
        mean = mean/(self.points.shape[0]-1)
        for i in range(self.points.shape[0]-1):
            counter = 0
            for j in range(i+1,self.points.shape[0]):
                if j-counter>=aux.shape[0]:
                    break
                if (aux[i] - aux[j-counter]).mod() <= delta*mean:
                    aux = np.delete(aux,j-counter)
                    counter += 1
        self.points = aux
        if not self.points[0]==self.points[-1]:
            self.append(self.points[0])
    def area_vec(self):
        self.area = Point(0,0,0)
        for n in range(1,self.points.shape[0]-1):
            v1 = self.points[n]-self.points[0]
            v2 = self.points[n+1]-self.points[0]
            cross = v1**v2
            self.area += cross*(1/2)
    def compute_length(self):
        self.total_length = 0
        for n in range(self.points.shape[0]-1):
            v1 = self.points[n]
            v2 = self.points[n+1]
            self.total_length += (v2-v1).mod()
    def c_clockwise(self, global_orientation=Point(1,0,0)):
        ## Reorients surface to counter-clockwise
        ##and creates a area vector
        if self.area.mod()==0:
            self.area_vec()
        if self.area.dot(global_orientation)<0:
            self.points = np.flip(self.points,0)
            self.area = -1*self.area
            for bridges in range(self.blend_points.shape[0]):
                self.blend_points[bridges] = np.flip(self.blend_points[bridges], axis=0)
    def geometric_center(self) -> Point:
        x = 0
        y = 0
        z = 0
        N = self.points.shape[0]
        center = Point(0,0,0)
        if self.points[0]==self.points[-1]:
            N -= 1
        for i in range(N):
            center += self.points[i]
        return center*(1/(N))
    def find_intersection(self, p1, p2, p3, p4, border = True) -> bool:
        ## Lets find a new algorithm to find intersections
        ##between lines
        '''
        https://stackoverflow.com/questions/2316490/the-algorithm-to-find-the-point-of-intersection-of-two-3d-line-segment
        Read all the comments!!

        s = Dot(Cross(dc, db), Cross(da, db)) / Norm2(Cross(da, db))

        t = Dot(Cross(dc, da), Cross(da, db)) / Norm2(Cross(da, db))

        da = p2 - p1
        db = p4 - p3
        dc = p3 - p1
        '''
        da = p2 - p1
        db = p4 - p3
        dc = p3 - p1

        norm2 = ((da**db).mod())**2
        if norm2 == 0:
            return False
            ## Could not find the reference for why the bellow code should be used
            ## AS far as i'm concerned, two parallel lines should never intersect
            ##so the return should always be false
            """
            d1 = p1 - p3
            d2 = p2 - p3
            d3 = p1 - p4
            d4 = p2 - p4
            cond1 = d1.dot(d2) < 0
            cond2 = d3.dot(d4) < 0
            if cond1 or cond2:
                return True
            else:
                return False"""
        s = (dc**db).dot(da**db) / norm2
        t = (dc**da).dot(da**db) / norm2
        if border:
            if ((s>=0 and s<=1) and (t>=0 and t<=1)):
                return True
            return False
        else:
            if ((s>0 and s<1) and (t>0 and t<1)):
                return True
            return False
    def fix_intersection(self):
        '''
        --Fixing intersections
        .Let i and j be two independent indexations to a list of Points (x,y)
        .With i < j, if the Points between i and i+1 creates a line that
        .intersects the line created by j and j+1, than fix the intersection by:
        revesing the order of the Points in the list from i+1 and j+1
        .This fixes the list in the sense that it will be no longer a
        self-intersecting curve
        '''
        p_points = self.points.shape[0]
        check = True
        Loops = 0   ## flexibility condition to avoid infinity
                    ##loops that may occur inside the while

        while check:
            found = False
            for i in range(p_points-3):
                for j in range(i+2, p_points-1):
                    if i==0 and j==p_points-2:
                        break
                    if self.find_intersection(
                            self.points[i],
                            self.points[i+1],
                            self.points[j],
                            self.points[j+1]):
                        found = True
                        aux = copy.deepcopy(self.points[(i+1):(j+1)])
                        aux = np.flip(self.points[(i+1):(j+1)], axis=0)
                        self.points[i+1:j+1] = np.flip(self.points[(i+1):(j+1)], axis=0)

                        if aux.size != 0:
                            for blends in range(self.blend_points.shape[0]):
                                sup = np.copy(self.blend_points[blends])
                                count1 = 0
                                count2 = 0
                                count3 = 0
                                count4 = 0
                                compile = np.array([self.points[i],
                                                    self.points[i+1],
                                                    self.points[j],
                                                    self.points[j+1]])
                                if sup[0] in compile:
                                    count1 += 1
                                if sup[1] in compile:
                                    count2 += 1
                                if sup[2] in compile:
                                    count3 += 1
                                if sup[3] in compile:
                                    count4 += 1
                                if count1 or count2 or count3 or count4: #remove later
                                    if 0:
                                        print(count1, count2, count3, count4)
                                        for p in self.points:
                                            print('"[{},{},{}]",'.format(p.x,p.y,p.z))
                                        print("blend")
                                        for p in self.blend_points[0]:
                                            print('"[{},{},{}]",'.format(p.x,p.y,p.z))
                                if count1 and not count2 and count3 and count4:
                                    self.blend_points[blends][0] = self.points[i]
                                    self.blend_points[blends][1] = self.points[j]
                                    self.blend_points[blends][2] = sup[1]
                                    self.blend_points[blends][3] = self.points[i+1]
                                if count1 and count2 and not count3 and count4:
                                    self.blend_points[blends][0] = self.points[i]
                                    self.blend_points[blends][1] = self.points[j]
                                    self.blend_points[blends][2] = sup[1]
                                    self.blend_points[blends][3] = self.points[j+1]
                                if count1 and count2 and count3 and not count4:
                                    self.blend_points[blends][0] = self.points[i]
                                    self.blend_points[blends][1] = self.points[j]
                                    self.blend_points[blends][2] = self.points[j+1]
                                    self.blend_points[blends][3] = sup[3]
                                if count1 and count2 and count3 and count4:
                                    self.blend_points[blends][1] = sup[2]
                                    self.blend_points[blends][2] = sup[1]
                            # for replace in range(i+1, j+1):
                            # self.points[i+1:j+1] = aux

                        # break
            ##Loop break if many intersections are encoutered
            Loops += 1

            if not found:
                check = False
            if Loops > 200:
                check = False
    def islands_ensemble(self, other):
        """
            For 2 independent contours in the same plane, it is possible to glue them
        together by picking the 2 closest points and creating a line that connects both.

            The ideia is simple, but there's some complications with the ordering of points.
        Also, it is possible that the two contours aren't fully separated, meaning that they
        might intersect. For that reason it is advisable to use Perimeter.fix_intersection()
        after ensembling two Perimeters().
        """
        M = self.points.shape[0]-1
        N = other.points.shape[0]-1
        other.c_clockwise(self.area)
        small_dist = np.inf
        for i in range(M):
            p_i = self.points[i]
            for j in range(N):
                p_j = other.points[j]
                if (p_i-p_j).mod()<=small_dist:
                    small_dist = (p_i-p_j).mod()
                    best_p_i = i
                    best_p_j = j
        if not self.find_intersection(self.points[best_p_i],
                                  other.points[best_p_j],
                                  self.points[best_p_i+1],
                                  other.points[best_p_j+1]):
            other.points=np.flip(other.points)
            other.area=-1*other.area
            best_p_j = N - best_p_j
            
        vari = M+N+1
        merged = np.array([Point(0,0,0) for _ in range(vari)])
        delta = 0
        if best_p_i<M-1:
            for i in range(M):
                if i==best_p_i+1:
                    for j in range(N):
                        if best_p_j+j<N:
                            merged[i+j] = other.points[best_p_j+j]
                            last_j = best_p_j+j
                        else:
                            merged[i+j] = other.points[j-(N-best_p_j)]
                            last_j = j-(N-best_p_j)
                    delta = N
                    merged[i+delta] = self.points[i]
                else:
                    merged[i+delta] = self.points[i]

        else:
            for i in range(M+1):
                if i<M-1:
                    merged[i] = self.points[i]
                else:
                    for j in range(N):
                        if best_p_j+j<N:
                            merged[i+j] = other.points[best_p_j+j]
                            last_j = best_p_j+j
                        else:
                            merged[i+j] = other.points[j-(N-best_p_j)]
                            last_j = j-(N-best_p_j)
        merged[vari-1] = self.points[0]
        if self.blend_points.shape[0]==0:
            self.blend_points = np.array([[self.points[best_p_i],
                                    other.points[best_p_j],
                                    other.points[last_j],
                                    self.points[best_p_i+1]]])
        else:
            self.blend_points = np.append(self.blend_points,np.array([[self.points[best_p_i],
                                    other.points[best_p_j],
                                    other.points[last_j],
                                    self.points[best_p_i+1]]]), axis=0)
        self.points = merged
    def flush_to_numpy(self):
        '''
            Returns a numpy array of type:

                array = [[x1,y1,z1],
                        ....
                        [xn,yn,zn]]

            that correponds to the Point()s in self.points:
        '''
        flushed = np.zeros((self.points.shape[0],3))
        for index,p in enumerate(self.points):
            flushed[index] = [p.x,p.y,p.z]
        return flushed
    def numpy_to_point(self, flushed):
        '''
            Analogous to flush_to_numpy(), but returns an array of Point()s
        '''
        perimeter = np.empty(flushed.shape[0],Point)
        for index,p in enumerate(flushed):
            perimeter[index] = Point(flushed[index,0],flushed[index,1],flushed[index,2])
        return perimeter
    def __str__(self):
        return "{L}\nwith shape = {S}".format(
                    L = [self.points[i].__str__()\
                        for i in range(self.points.shape[0])],
                    S = (self.points.shape)+(2,)
                    )
    def __add__(v,u):
        ## Caculates best point to connect two contours contained in the
        ## same slice

        M = v.points.shape[0]
        N = u.points.shape[0]
        cost_matrix = np.zeros((M-1,N-1))
        for m in range(M-1):
            for n in range(N-1):
                cost_matrix[m,n] = (v.points[m]-u.points[n]).mod()
        allMin = np.where(cost_matrix==np.amin(cost_matrix))
        final_min_cord = list(zip(allMin[0], allMin[1]))[0]
        vari = M+N
        final = [Point(0,0,0)]*(vari)
        m = 0
        n = final_min_cord[1]
        mc = 0
        nc = 0
        while mc<M:

            final[mc+nc] = Point(
                v.points[m].x,
                v.points[m].y,
                v.points[m].z)

            if m == final_min_cord[0]:

                while nc<N-1:

                    final[mc+nc] = Point(
                        u.points[n].x,
                        u.points[n].y,
                        u.points[n].z)
                    n += 1
                    nc += 1

                    if n == N:
                        n = 0

                final[mc+nc] = Point(
                    u.points[final_min_cord[1]].x,
                    u.points[final_min_cord[1]].y,
                    u.points[final_min_cord[1]].z)
                final[mc+nc + 1] = Point(
                    v.points[final_min_cord[0]-1],
                    v.points[final_min_cord[0]-1],
                    v.points[final_min_cord[0]-1])
                m += 0
                mc += 1

            m += 1
            mc += 1

            if m == M:

                m = 0

        final[vari-1] = Point(
            v.points[v.points.shape[0]-2].x,
            v.points[v.points.shape[0]-2].y,
            v.points[v.points.shape[0]-2].z)

        return final

class Surface():

    def __init__(self):
        self.slices = np.empty(0) ##collection of Perimeters
        self._surface = False ##Fully built surface
        self._intersection_range = 3000
        self.fix_limit = 1000
        self.intersection_limit = 100000
        self.border_intersection = False ##
        self.surface_orientation = Point(0,0,0)
        self._intersection_counter = 0
        self._intrinsic_interpolation = True#False
        self.self_intersection = False

    def set_parameters(self, **kwargs):
        error = 0
        for k in kwargs:
            val = kwargs.get(k)
            if k=="intersection_range":
                self._intersection_range = val
                continue
            if k=="fix_limit":
                self.fix_limit= val
                continue
            print(f"Could not interpret {k} as valid argument")
            error+=1
        if error:
            self.help()
    def help():
        print("Send Help")
    def add_island(self, *arg):
        if arg:
            self.slices = np.append(
                self.slices,
                np.array([arg[0]]),
                axis=0
                )
        else:
            self.slices = np.append(
                self.slices,
                np.array([Perimeter()]),
                axis=0
                )
    def mesh_out(self,path="",name="NoName"):
        if self.out_surface:
            out = 0
        else:
            error = 0
    def estimate_geometric_values(self):
        """
            Ribeiro PF, Ventura-Antunes L, Gabi M, Mota B, Grinberg LT, Farfel
            JM, Ferretti-Rebustini RE, Leite RE, Filho WJ, Herculano-Houzel S.
            The human cerebral cortex is neither one nor many: neuronal
            distribution reveals two quantitatively different zones in the gray
            matter, three in the white matter, and explains local variations
            in cortical folding. Front Neuroanat. 2013 Sep 2;7:28.
            doi: 10.3389/fnana.2013.00028. PMID: 24032005; PMCID: PMC3759024.
        """
        def b_area(t,a1,a2,p1,p2):
            return np.sqrt((a1-a2)**2+(t*(p1+p2)/2)**2)

        def b_vol(t,a1,a2):
            return t*(a1+a2+np.sqrt(a1*a2))/3

        self.area_est = 0
        self.vol_est = 0
        for i in range(self.slices.shape[0]-1):
            a1 = self.slices[i].area.mod()
            a2 = self.slices[i+1].area.mod()
            p1 = self.slices[i].total_length
            p2 = self.slices[i+1].total_length
            
            ##thickness computation
            g1 = self.slices[i].geometric_center()
            g2 = self.slices[i+1].geometric_center()
            t = abs((g2-g1).dot(self.slices[i].area/self.slices[i].area.mod()))

            self.area_est += b_area(t,a1,a2,p1,p2)
            self.vol_est += b_vol(t,a1,a2)

    def build_surface(self, close_list=[], start_points={},skipping_cache=0):
        self.surfaceV = "" ##3d reconstructed surface
        self.surfaceE = ""
        total_shift = 0
        self.slices[0].area_vec()
        self.surface_orientation = self.slices[0].area
        for n in range(self.slices.shape[0]-1):
            self.slices[n+1].c_clockwise(self.surface_orientation)
            dist_matrix = self.__CostMatrix(self.slices[n],self.slices[n+1])
            self.border_intersection = False
            '''
                After reordering the both sequences of points, we need
            to a way to conect all in between points that represent a
            surface that:
                1) is not self intersecting
                2) has the smallest possible area
                3) is closed
            -~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
                If we find a point (edge) that all of its connections (triangles)
            create intersections, than we must never use this point in our final
            mesh. So we list all this points per stitched surface and exclude
            them from our path find algorithm by setting its value to
            infinity.
            '''
            bad_connect = []
            rerun = False
            dummy_counter=0

            ## Basic cache memmory mechanism
            for i in range(skipping_cache):
                closest_point_dist = np.amin(dist_matrix)
                allMin = np.where(dist_matrix == closest_point_dist)
                list_cordinates = list(zip(allMin[0], allMin[1]))
                dist_matrix[list_cordinates[0]]=np.inf
                final_min_cord = list_cordinates[0]
                f0 = final_min_cord[0]
                f1 = final_min_cord[1]
                dummy_counter+=1
            while not self.border_intersection:

                if len(bad_connect) >= self.intersection_limit:
                    skip_intersection = True
                    self.self_intersection = True
                    print("Skiping intersection check")
                else:
                    skip_intersection = False

                ##After finding a path with o intersections
                ## finding all min values contained inthe matrix
                ##there's usually only one, but the value might
                ##be repeated somewhere
                closest_point_dist = np.amin(dist_matrix)
                allMin = np.where(dist_matrix == closest_point_dist)
                list_cordinates = list(zip(allMin[0], allMin[1]))
                final_min_cord = list_cordinates[0]
                f0 = final_min_cord[0]
                f1 = final_min_cord[1]
                if str(n) in start_points.keys() and dummy_counter<=0:
                    self.fix_limit = self.slices[n].points.shape[0]*self.slices[n+1].points.shape[0]
                    P1 = start_points[f"{n}"][0]
                    P2 = start_points[f"{n}"][1]
                    print(f"\tStarting points selected for reconstruction number {n}:\n\t\t{P1}\n\t\t{P2}")
                    f_bool=[False,False]
                    for p_index_search,point_search in enumerate(self.slices[n].points):
                        if point_search==Point(P1[0],P1[1],P1[2]):
                            f0=p_index_search
                            f_bool[0]=True
                            break
                    for p_index_search,point_search in enumerate(self.slices[n+1].points):
                        if point_search==Point(P2[0],P2[1],P2[2]):
                            f1=p_index_search
                            f_bool[1]=True
                            break
                    if f_bool[0]*f_bool[1]:
                        final_min_cord=[f0,f1]

                reordered_upper =  self.__Reordering(
                    self.slices[n],
                    f0)
                reordered_lower =  self.__Reordering(
                    self.slices[n+1],
                    f1)
                cost_matrix =  self.__CostMatrix(reordered_upper,reordered_lower)
                for bad in bad_connect:
                    if bad[0]>=f0:
                        bad1 = bad[0]-f0
                    else:
                        bad1 = bad[0]+(self.slices[n].points.shape[0]-f0-1)
                    if bad[1]>=f1:
                        bad2 = bad[1]-f1
                    else:
                        bad2 = bad[1]+(self.slices[n+1].points.shape[0]-f1-1)
                    cost_matrix[bad1,bad2] = np.inf
                mincost,the_path,wrong,total_cost = self.__FindPath(
                                                                cost_matrix,
                                                                self.slices[n].points.shape[0],
                                                                self.slices[n+1].points.shape[0],
                                                                reordered_upper,
                                                                reordered_lower,
                                                                skip_intersection)
                ##fixing relative order to absolute/initial order
                if not isinstance(wrong, int):
                    for w in wrong:
                        if w[0]+f0 <= self.slices[n].points.shape[0]-2:
                            w[0] += f0
                        else:
                            w[0] += f0-self.slices[n].points.shape[0]-2
                        if w[1]+f1 <= self.slices[n+1].points.shape[0]-2:
                            w[1] += f1
                        else:
                            w[1] += f1-self.slices[n+1].points.shape[0]-2
                        if [w[0],w[1]] in bad_connect:
                            dummy_counter+=1
                            dist_matrix[f0,f1] = np.inf
                        else:
                            bad_connect.append([w[0],w[1]])
                else:
                    dummy_counter+=1
                    dist_matrix[f0,f1] = np.inf

            ##FAN ARTIFACT LOG
            c1_fan_artifact=1
            c2_fan_artifact=1
            p1_fan_artifact=the_path[0,0]
            p2_fan_artifact=the_path[0,1]
            for index_fan_artifact, pair_fan_artifact in enumerate(the_path):
                if index_fan_artifact==0:
                    continue
                if p1_fan_artifact==pair_fan_artifact[0]:
                    c1_fan_artifact += 1
                else:
                    c1_fan_artifact = 1
                if p2_fan_artifact==pair_fan_artifact[1]:
                    c2_fan_artifact += 1
                else:
                    c2_fan_artifact = 1

                if c1_fan_artifact>10:
                    fan_edge1 = reordered_upper.points[pair_fan_artifact[0]]-reordered_lower.points[p2_fan_artifact]
                    fan_edge2 = reordered_upper.points[pair_fan_artifact[0]]-reordered_lower.points[pair_fan_artifact[1]]
                    surface_vec_fan_artifact=fan_edge1**fan_edge2
                    surface_vec_fan_artifact=surface_vec_fan_artifact/surface_vec_fan_artifact.mod()
                    ori_fan = self.surface_orientation/self.surface_orientation.mod()
                    angle_fan_artifact = max(surface_vec_fan_artifact.dot(ori_fan),surface_vec_fan_artifact.dot(-1*ori_fan))
                    angle_fan_artifact = np.arccos(angle_fan_artifact)*180/np.pi
                    if angle_fan_artifact<=15:
                        print(f"Fan artifact found at {n}th reconstruction")
                        break
                if c2_fan_artifact>10:
                    fan_edge1 = reordered_lower.points[pair_fan_artifact[1]]-reordered_upper.points[p1_fan_artifact]
                    fan_edge2 = reordered_lower.points[pair_fan_artifact[1]]-reordered_upper.points[pair_fan_artifact[0]]
                    surface_vec_fan_artifact=fan_edge1**fan_edge2
                    surface_vec_fan_artifact=surface_vec_fan_artifact/surface_vec_fan_artifact.mod()
                    ori_fan = self.surface_orientation/self.surface_orientation.mod()
                    angle_fan_artifact = max(surface_vec_fan_artifact.dot(ori_fan),surface_vec_fan_artifact.dot(-1*ori_fan))
                    angle_fan_artifact = np.arccos(angle_fan_artifact)*180/np.pi
                    if angle_fan_artifact<=15:
                        print(f"Fan artifact found at {n}th reconstruction")
                        break

                p1_fan_artifact = pair_fan_artifact[0]
                p2_fan_artifact = pair_fan_artifact[1]
            ## The path is calculated based on the reordered points,
            ##so we should invert the transformation so that we have
            ##the path for the original set of points

            the_path = self.__FixPathOrder(
                the_path,
                final_min_cord,
                self.slices[n].points.shape[0],
                self.slices[n+1].points.shape[0])

            self.surfaceV += self.__Vertices(self.slices[n].points)
            self.surfaceE += self.__Edges(
                the_path,
                self.slices[n].points.shape[0]-1,
                self.slices[n+1].points.shape[0]-1,
                total_shift)

            total_shift += self.slices[n].points.shape[0] - 1
            self.border_intersection = False

        self.surfaceV += self.__Vertices(self.slices[n+1].points)
        for i in close_list:
            closing_points = self.slices[i].points
            self.slices[i].area_vec()
            area_vec = self.slices[i].area
            if i == 0:
                closing_shift = 0
            else:
                closing_shift = total_shift
            self.surfaceE += self.__CloseSurface(closing_points, area_vec, closing_shift)
        self.out_surface = True
    def super_resolution(self, parcelation=1,seed=1):
        import copy
        import matplotlib.pyplot as plt
        if parcelation==0:
            return
        def rotate_to(perimeter_rotate, vector):
            '''
                Rotates a closed loop/surface until its area vector
                is aligned with the in the vector
            '''
            unity_vec = vector*(1/vector.mod())
            perimeter_rotate.area_vec()
            unity_area = copy.deepcopy(perimeter_rotate.area)*(1/perimeter_rotate.area.mod())
            theta = np.arccos(unity_vec.dot(unity_area))
            unity_vec = unity_area**unity_vec
            if unity_vec.mod()==0:
                return perimeter_rotate
            unity_vec = unity_vec *(1/unity_vec.mod())
            new_point = []
            for point in perimeter_rotate.points:
                xcomp = (np.cos(theta)+unity_vec.x**2*(1-np.cos(theta)))*point.x +\
                        (unity_vec.x*unity_vec.y*(1-np.cos(theta))-unity_vec.z*np.sin(theta))*point.y+\
                        (unity_vec.x*unity_vec.z*(1-np.cos(theta))+unity_vec.y*np.sin(theta))*point.z

                ycomp = (unity_vec.y*unity_vec.x*(1-np.cos(theta))+unity_vec.z*np.sin(theta))*point.x +\
                        (np.cos(theta)+unity_vec.y**2*(1-np.cos(theta)))*point.y+\
                        (unity_vec.y*unity_vec.z*(1-np.cos(theta))-unity_vec.x*np.sin(theta))*point.z

                zcomp = (unity_vec.x*unity_vec.z*(1-np.cos(theta))-unity_vec.y*np.sin(theta))*point.x +\
                        (unity_vec.z*unity_vec.z*(1-np.cos(theta))+unity_vec.x*np.sin(theta))*point.y+\
                        (np.cos(theta)+unity_vec.z**2*(1-np.cos(theta)))*point.z
                new_point.append(Point(xcomp,ycomp,zcomp))
            return Perimeter(np.array(new_point))

        def intrinsic_reference(perimeter):
            '''
                Returns intrinsic distance vectors of a perimeter
            '''
            intrinsic = np.array([Point(0,0,0)]*(perimeter.points.shape[0]))
            intrinsic[0] = copy.deepcopy(perimeter.points[0])
            for index in range(1,perimeter.points.shape[0]):
                intrinsic[index] = perimeter.points[index]-perimeter.points[index-1]
            return Perimeter(intrinsic)

        def extrinsic_reference(perimeter):
            '''
                Returns extrinsic distance vectors of a perimeter with intrisic
                reference. Also centers the geometric center to the origin
            '''
            extrinsic = np.array([Point(0,0,0)]*(perimeter.points.shape[0]))
            extrinsic[0] = copy.deepcopy(perimeter.points[0])
            for index in range(1,perimeter.points.shape[0]):
                extrinsic[index] = perimeter.points[index]+extrinsic[index-1]
            extrinsic = Perimeter(extrinsic)
            return extrinsic
            geo = extrinsic.geometric_center()
            for index in range(extrinsic.points.shape[0]):
                extrinsic.points[index] -= geo
                extrinsic.points[index] += self.slices[n].geometric_center()

            return extrinsic

        def interpolate(perimeters, parcelation):
            ##Returns list of all new permiters in order of height
            def linear_interpol(interpol_1, interpol_2, parcelation):
                """
                    get the fourier coef and interpoalte
                """
                interpolation_sequence = []
                for p in range(1,parcelation+1):
                    newarray = interpol_2*p/(parcelation+1)+interpol_1*(1-p/(parcelation+1))
                    interpolation_sequence.append(newarray)
                return interpolation_sequence

            def to_complex(complex_perimeter):
                array = complex_perimeter.flush_to_numpy()
                complex = np.zeros(complex_perimeter.points.shape[0],dtype=np.cfloat)
                for sup_index in range(complex_perimeter.points.shape[0]):
                    complex[sup_index] = array[sup_index][0]+array[sup_index][1]*1j
                return complex

            def to_real(complex_points):
                real = np.zeros((complex_points.shape[0],2))
                for sup_index in range(complex_points.shape[0]):
                    real[sup_index] = [complex_points[sup_index].real,complex_points[sup_index].imag]
                return real

            array1 = to_complex(perimeters[0])
            array2 = to_complex(perimeters[1])

            if array1.shape[0]<array2.shape[0]:
                diff = array2.shape[0]-array1.shape[0]
                for i in range(diff):
                    insrert_list = np.random.randint(0,array1.shape[0]-1,1)
                    newpoint = (array1[insrert_list]+array1[insrert_list+1])/2
                    array1 = np.insert(array1,insrert_list+1,newpoint,axis=0)
            elif array1.shape[0]>array2.shape[0]:
                diff = array1.shape[0]-array2.shape[0]
                for i in range(diff):
                    insrert_list = np.random.randint(0,array2.shape[0]-1,1)
                    newpoint = (array2[i]+array2[i+1])/2
                    array2 = np.insert(array2,i+1,newpoint,axis=0)

            transform1 = np.fft.fft(array1)
            transform2 = np.fft.fft(array2)
            interpolation_sequence = linear_interpol(transform1,transform2,parcelation)
            resolved = []
            for inter in interpolation_sequence:
                points = to_real(np.fft.ifft(inter))
                points = [Point(px,py,0) for px,py in points]
                perimeter = Perimeter(np.array(points))
                if self._intrinsic_interpolation:
                    perimeter = extrinsic_reference(perimeter)
                perimeter.points[-1]=perimeter.points[0]
                resolved.append(perimeter)
            return resolved

        def perimeter_insert(perimeters):
            def get_height(index):

                height = self.slices[index+1].geometric_center()-self.slices[index].geometric_center()
                self.slices[index].area_vec()
                unity_area = copy.deepcopy(self.slices[index].area)*(1/self.slices[index].area.mod())
                prod_aux = height.dot(unity_area)
                if prod_aux>0:
                    return np.sqrt(height.dot(unity_area))*unity_area
                else:
                    print("",end="")
                    return -1*np.sqrt(height.dot(-1*unity_area))*unity_area
            super_res = Surface()
            fourier_original_coef = []
            for index,perimeter_insertion in perimeters:
                super_res.add_island(self.slices[index])
                newperimeter = copy.deepcopy(perimeter_insertion)
                height = get_height(index)#-1*nearest_point(index)#get_height(index)
                total = len(newperimeter)
                local_geo = self.slices[index].geometric_center()
                for fourier_index, p_insertion in enumerate(newperimeter):
                    for index2 in range(p_insertion.points.shape[0]):
                        p_insertion.points[index2] += local_geo
                    #p_insertion = rotate_to(p_insertion,self.slices[0].area)
                    for index2 in range(p_insertion.points.shape[0]):
                        p_insertion.points[index2] += (height+nearest[index])*((fourier_index+1)/(total+1))
                    p_insertion.remove_overlap()
                    p_insertion.area_vec()
                    p_insertion.fix_distance(subdivision=1)
                    p_insertion.fix_intersection()
                    p_insertion.area_vec()
                    super_res.add_island(p_insertion)

            super_res.add_island(self.slices[-1])
            for insert_n in range(super_res.slices.shape[0]):
                super_res.slices[insert_n] = rotate_to(super_res.slices[insert_n], self.surface_orientation)
                for ori_points in range(super_res.slices[insert_n].points.shape[0]):
                    super_res.slices[insert_n].points[ori_points]+=zero_center

            self.slices = super_res.slices

        def nearest_point(n:int):
            dist = np.inf
            for first_index in range(self.slices[n].points.shape[0]):
                for sec_index in range(self.slices[n+1].points.shape[0]):
                    dist_aux = (self.slices[n].points[first_index]-self.slices[n+1].points[sec_index]).mod()
                    if dist_aux<dist:
                        dist = dist_aux
                        displacement = self.slices[n].points[first_index]-self.slices[n+1].points[sec_index]
            return displacement
        if seed:
            np.random.rand(seed)
        self.slices[0].area_vec()
        self.surface_orientation = self.slices[0].area
        surface_normal_dir = copy.deepcopy(self.surface_orientation)*(1/self.surface_orientation.mod())

        def plot_interpolation(interpolation_slice, upper, lower, diff_vector, counter):
            UPPERX = []
            UPPERY = []
            LOWERX = []
            LOWERY = []
            INTERX = []
            INTERY = []
            for upper_index_plot in range(upper.points.shape[0]):
                UPPERX.append(upper.points[upper_index_plot].x)
                UPPERY.append(upper.points[upper_index_plot].y)

            for lower_index_plot in range(lower.points.shape[0]):
                LOWERX.append(lower.points[lower_index_plot].x)
                LOWERY.append(lower.points[lower_index_plot].y)

            for inter_index_plot in range(interpolation_slice.points.shape[0]):
                INTERX.append(interpolation_slice.points[inter_index_plot].x+horizontal_disp.x/2)
                INTERY.append(interpolation_slice.points[inter_index_plot].y+horizontal_disp.y/2)

            plt.plot(UPPERX,UPPERY,alpha=0.5)
            plt.plot(LOWERX,LOWERY,alpha=0.5)
            plt.plot(INTERX,INTERY,c="red")
            plt.arrow(self.slices[n].points[upper_counter].x,
                    self.slices[n].points[upper_counter].y,
                    diff_vector.x,
                    diff_vector.y,
                    width=0.002,
                    head_width=0.5,
                    head_length=0.55,
                    overhang=0.4)
            plt.xlim(-20,25)
            plt.ylim(-15,15)
            if counter<10:
                print("in")
                plt.savefig("C:/Users/hgess/Desktop/Fourier/disp/0000"+str(counter)+".jpg",bbox_inches='tight')
            elif counter<100:
                plt.savefig("C:/Users/hgess/Desktop/Fourier/disp/000"+str(counter)+".jpg",bbox_inches='tight')
            elif counter<1000:
                plt.savefig("C:/Users/hgess/Desktop/Fourier/disp/00"+str(counter)+".jpg",bbox_inches='tight')
            elif counter<10000:
                plt.savefig("C:/Users/hgess/Desktop/Fourier/disp/0"+str(counter)+".jpg",bbox_inches='tight')
            else:
                plt.savefig("C:/Users/hgess/Desktop/Fourier/disp/"+str(counter)+".jpg",bbox_inches='tight')
            plt.clf()

        z_orientation =  Point(0,0,1)
        original = [Perimeter(),Perimeter()]
        interpolated_all = []
        interpolated_list = []
        zero_center = self.slices[0].geometric_center()
        nearest = []
        if 1:
            for n in range(self.slices.shape[0]):
                self.slices[n].c_clockwise(self.surface_orientation)
                for ori_points in range(self.slices[n].points.shape[0]):
                    self.slices[n].points[ori_points]-=zero_center
                self.slices[n] = rotate_to(self.slices[n], z_orientation)
                self.slices[n] = extrinsic_reference(intrinsic_reference(self.slices[n]))
        img_counter = 0
        single_img = False
        for n in range(self.slices.shape[0]-1):
            for upper_counter in range(0,self.slices[n].points.shape[0],2):
                for lower_counter in range(0,self.slices[n+1].points.shape[0],2):
                    img_counter += 1
                    for i in range(2):
                        original[i] = copy.deepcopy(self.slices[n+i])
                        horizontal_disp = Point(0,0,0)
                        if i==1:
                            horizontal_disp = self.slices[n].points[upper_counter]-self.slices[n+1].points[lower_counter]
                            #nearest_point(n)#original[1].geometric_center()-original[0].geometric_center()
                            horizontal_disp = Point(horizontal_disp.x,horizontal_disp.y,0)
                            original[i].points -= horizontal_disp
                            nearest.append(horizontal_disp)
                        if i==200:
                            displacement = nearest_point(n)
                            nearest.append(displacement)
                            original[i].points -= displacement
                        original[i].area_vec()
                        if self._intrinsic_interpolation:
                            original[i] = intrinsic_reference(original[i])
                    interpolated_list = interpolate(original,parcelation)
                    plot_interpolation(*interpolated_list,self.slices[n],self.slices[n+1],horizontal_disp,img_counter)
                    interpolated_all.append([n,[*interpolated_list]])
                    if single_img:
                        break
                if single_img:
                    break
            if single_img:
                break
        #perimeter_insert(interpolated_all)
    def closebif(self, file_index, bif_list):
        '''
            There are 2 pairs of lines per connection created by merging
        islands. So we need to select those 2 pairs and put a surface on them
        to close all sruface holes.
            There are however some procidures such fix_intersection(), that
        may cause each pair to flip oriention individually. Instead of
        finding if they did or did not flip, we chose to simple allert when
        passing by one of the points.
            On the first pass, we record the next points because they are part
        of the line segment. On the second alert, we stop the recording.
        Finally, we grab 2 pairs at a time and triangulate them.
            Note that having more than 2 pairs means that there 3 or more
        islands on a given slice.
        '''

        bif = np.copy(self.slices[file_index].points)
        blend_points = np.copy(self.slices[file_index].blend_points)
        area = self.slices[file_index].area

        shift = 0
        for s in range(file_index):
            shift += self.slices[s].points.shape[0]-1

        for bridges in self.slices[file_index].blend_points:
            bridge_mut = np.copy(bridges) #dont mess with the original: leanrt the hard way

            def side(bridge_mut, bif, case = [0,0]):
                '''
                    Nice exception has appeared more than once. iF the link
                between two islands is point zero, we have to cosinder the cases
                of the bridge being the points before and after.
                    There's no good proof, but its quite intuitive that the
                smallest sequence of points should be the actuall bridge.
                '''
                part1 = np.array([bridge_mut[0],bridge_mut[1]])
                part2 = np.array([bridge_mut[2],bridge_mut[3]])
                bif_diff = np.array([Point(0,0,0)])
                index_list = np.array([],dtype=int)
                count1 = 0
                count2 = 0
                start_part1 = False
                start_part2 = False
                for point in range(case[0],bif.shape[0]-case[1]): #reccording loop
                    if bif[point] in part1:
                        start_part1 = True
                        count1 += 1
                    if bif[point] in part2:
                        start_part2 = True
                        count2 += 1
                    if start_part1:
                        bif_diff = np.append(bif_diff, bif[point])
                        if point+1==bif.shape[0]:
                            index_list = np.append(index_list, shift+1)
                        else:
                            index_list = np.append(index_list, point+shift+1)
                        if count1==2:
                            start_part1 = False
                    if start_part2:
                        bif_diff = np.append(bif_diff, bif[point])
                        if point+1==bif.shape[0]:
                            index_list = np.append(index_list, shift+1)
                        else:
                            index_list = np.append(index_list, point+shift+1)
                        if count2==2:
                            start_part2 = False
                return bif_diff, index_list

            bif_diff1, index_list1 = side(bridge_mut, bif, case = [0,1])
            bif_diff2, index_list2 = side(bridge_mut, bif, case = [1,0])
            if index_list1.shape[0]<index_list2.shape[0]:
                bif_diff, index_list = bif_diff1, index_list1
            else:
                bif_diff, index_list = bif_diff2, index_list2
            index_list = np.append(index_list, index_list[0])
            bif_diff = np.delete(bif_diff,0,0)
            bif_diff = np.append(bif_diff, bif_diff[0])
            #print(index_list-shift,self.slices[file_index].points.shape[0])
            self.surfaceE += self.__CloseSurface(bif_diff, area, shift, index_list)
    def close_extra(self, island):
        ## Simply takes an island and triangulate it
        closing_points = island.points
        self.surfaceV_extra = self.__Vertices(closing_points)
        island.area_vec()
        area_vec = island.area
        self.surfaceE_extra = self.__CloseSurface(closing_points, area_vec, 0)

    ## Not meant for end-user
    def __CloseSurface(self, closing_points, area_vec, shift=0, index_list = None):
        '''
            Implementation of a ear clipping algorithm to create a plane triangulation.

            Currently using a simpler and more comprehensible algorithm from

                ElGindy, Hossam, Hazel Everett, and Godfried Toussaint.
                "Slicing an ear using prune-and-search."
                Pattern Recognition Letters 14.9 (1993): 719-722.

            The idea is to define what is mathematically an ear (a type of triangle), and
        start clipping/slicing ear until there no more to be clipped.
        '''
        number_points = closing_points.shape[0]-1
        points = np.array([[Point(0,0,0),0]]*number_points)
        edges = ''

        for i in range(number_points):
            points[i][0] = closing_points[i]
            if not isinstance(index_list, np.ndarray):
                points[i][1] = i+1+shift #+1 corrects the .obj file format counting
            else:
                points[i][1] = index_list[i]

        def is_ear(GSP, p_i,area_vec): #check for intersection, points inside triangulation...
            def point_tiangle_3D(p1, p2, p3, p):
                ##returns if a point is inside the triangle surface or not
                v0 = p3 - p1
                v1 = p2 - p1
                v2 = p - p1
                dot00 = v0.dot(v0)
                dot01 = v0.dot(v1)
                dot02 = v0.dot(v2)
                dot11 = v1.dot(v1)
                dot12 = v1.dot(v2)
                if (dot00 * dot11 - dot01 * dot01) == 0:
                    return False
                invDenom = 1 / (dot00 * dot11 - dot01 * dot01)
                u = (dot11 * dot02 - dot01 * dot12) * invDenom
                v = (dot00 * dot12 - dot01 * dot02) * invDenom
                eta = 1e-5
                return (u>=0-eta) and (v>=0-eta) and (u+v<1+eta)
            if p_i == 0:
                p1 = GSP.shape[0]-1
            else:
                p1 = p_i-1
            if p_i == GSP.shape[0]-1:
                p3 = 0
            else:
                p3 = p_i+1
            displacement1 = GSP[p1][0] - GSP[p_i][0]
            displacement2 = GSP[p3][0] - GSP[p_i][0]
            displacement1 = displacement1*(1/displacement1.mod())
            displacement2 = displacement2*(1/displacement2.mod())
            the_dot = displacement1.dot(displacement2)
            if the_dot>1:
                the_dot = 1
            if the_dot<-1:
                the_dot = -1
            angle1 = np.arccos(the_dot)

            if ((-1*displacement1)**displacement2).dot(area_vec) < 0:
                return False
            if angle1==np.pi:
                return False

            for index in range(GSP.shape[0]):
                if index==p_i or index==p1 or index==p3:
                    continue
                if point_tiangle_3D(GSP[p_i][0], GSP[p1][0], GSP[p3][0], GSP[index][0]):
                    return False
            for index in range(GSP.shape[0]-1):
                if index==p_i or index==p1 or index==p3:
                    continue
                if index==p_i+1 or index==p1+1 or index==p3+1:
                    continue
                if Perimeter(full_init=False).find_intersection(
                    GSP[index][0],
                    GSP[index+1][0],
                    GSP[p1][0],
                    GSP[p3][0],
                    False):
                    return False
            return True
        def triang_ear(GSP, p_i): #string outrput
            if p_i == 0:
                p0 = GSP[GSP.shape[0]-1][1]
            else:
                p0 = GSP[p_i-1][1]
            p1 = GSP[p_i][1]
            if p_i == GSP.shape[0]-1:
                p2 = GSP[0][1]
            else:
                p2 = GSP[p_i+1][1]
            s = "f " +str(p0) +\
                    " " + str(p1) +\
                    " " + str (p2) + "\n"
            return s

        loop_max = points.shape[0]-2
        triang_count = 1
        while triang_count!=loop_max:
            for i in range(points.shape[0]):
                if is_ear(points,i,area_vec):
                    edges += triang_ear(points,i)
                    points = np.delete(points,i,0)
                    triang_count += 1
                    break
                if i == points.shape[0]-1:
                    close_problem = True
                    triang_count=loop_max
                else:
                    close_problem = False
                if points.shape[0]==3:
                    triang_count=loop_max
        edges += triang_ear(points,1)
        return edges
    def __CostMatrix(self, reordered_upper, reordered_lower) -> np.ndarray:
        ## Upper stands for the surface on top and Lower for the one in the bottom
        M = reordered_upper.points.shape[0]
        N = reordered_lower.points.shape[0]
        cost_matrix = np.zeros((M-1,N-1))

        for m in range(M-1):
            for n in range(N-1):
                cost_matrix[m,n] = (reordered_upper.points[m] - reordered_lower.points[n]).mod()

        return cost_matrix
    def __FindPath(self, final_matrix, M, N, reordered_upper, reordered_lower, skip_intersection = False):
        def surface_intersection(the_path, path_limit, next, upper, reordered_upper, reordered_lower, skip_intersection = False, final_cond=[False,[0,0]]) -> bool:
            '''
                Given a triangle with vertices p1, p2 and p3, we wish to know if a line segment
            (q1,q2) intersects it.
                1) a0 and b0 are the index of the points
                2) The given triangle is the new triangle being inserted in the 3D mesh
                3) Loop over all pairs of lines because thats the information contained
                    in the the_path list -> think that to get the triangles we still need
                    to process the_path in __Vertices() and __Edges() functions
            '''
            def line_triangle_intersection(q1, q2, p1, p2, p3):
                ## stackoverflow.com/questions/42740765/intersection-between-line-and-triangle-in-3d
                def volume(a, b, c, d):
                    vol = (b-a) ** (c-a)
                    vec = d - a
                    ## inner product
                    vol = vol.x*vec.x + vol.y*vec.y + vol.z*vec.z
                    return vol

                condition = volume(q1,p1,p2,p3)*volume(q2,p1,p2,p3)
                eta = 1e-8
                if condition < 0:
                    if volume(q1,q2,p1,p2)*volume(q1,q2,p2,p3) > 0-eta and\
                        volume(q1,q2,p1,p2)*volume(q1,q2,p3,p1) > 0-eta:
                        return True
                return False
            if path_limit < 3:
                return [-1,-1], False

            ## if speed is needed in the future
            ##we may try limiting the search range
            if path_limit > self._intersection_range-1:
                search_limit = path_limit - self._intersection_range
            else:
                search_limit = 0
            if not final_cond[0]:
                if path_limit < the_path.shape[0]:
                    p_index = the_path[path_limit]
                else:
                    return [-1,-1], False
            else:
                p_index = final_cond[1]

            if upper:
                p1 = reordered_upper.points[next[0]]
                p2 = reordered_lower.points[next[1]]
                p3 = reordered_lower.points[p_index[1]]
            else:
                p1 = reordered_lower.points[next[1]]
                p2 = reordered_upper.points[next[0]]
                p3 = reordered_upper.points[p_index[0]]
            for i in the_path[search_limit:path_limit+1]:
                a0 = int(i[0])
                b0 = int(i[1])
                q1 = reordered_upper.points[a0]
                q2 = reordered_lower.points[b0]
                if line_triangle_intersection(q1, q2, p1, p2, p3):
                    if skip_intersection:
                        self._intersection_counter += 1
                        return [-1,-1], False
                    return [a0,b0], True

            return [-1,-1], False

        def retract(m_local,n_local,min_cost_local,index_local,the_path, counter_local):
            m_local,n_local=the_path[index_local]
            min_cost_local[m_local][n_local]=np.inf
            the_path[index_local]=[0,0]
            index_local -= 1
            return m_local,n_local,min_cost_local,index_local,counter_local+1

        M = M - 1
        N = N - 1

        ofinal_matrix = final_matrix
        min_cost = np.zeros((M,N))
        min_cost[0][0] = final_matrix[0][0]

        ## setting the upper border cost
        for j in range(1,N):
            min_cost[0][j] = min_cost[0][j-1] + final_matrix[0][j]

        ## setting the left border cost
        for i in range(1,M):
            min_cost[i][0] = min_cost[i-1][0] + final_matrix[i][0]

        for i in range(1,M):
            for j in range(1,N):
                best = min(min_cost[i-1][j],min_cost[i][j-1])
                min_cost[i][j] = best + final_matrix[i][j]
                if min_cost[i][j]<=0:
                    print("Negative cost on the path")

        ## Everything from now on is a way of finding what's the acctual path
        ##not only the cost of getting there.
        total_cost = min_cost[M-1][N-1]
        var1 = False
        var2 = False
        the_path = np.array([[0,0]]*(M+N-2), dtype=int)
        the_path[M+N-3] = [M-1,N-1]
        m = M-1
        n = N-1
        the_path = np.insert(the_path, 0, [[M-1,N-1]], axis=0)
        index = 0
        fix_counter = 0
        while index<=M+N-3:
            ##  01/2022 -> changed to while loop beacause the index needs to be
            ##manipulated on the fly.

            '''
                1) The loop starts at the end of the 2D path matrix (M,N)
                2) We get the smallest value when going up (M-1,N) or left (M,N-1)
                3) Check for intersections with previous triangles in the mesh:
                    3.1) If up/left is intersection, go to check for left/up
                        If it is:
                        3.1.1) Try to retract the path find mark current point as infinity cost (bad point)
                        3.1.2) If too many retracts are performed -> return and try a new starting point
                        If not intersection pick left/up
                4) If reached (0,x) or (x,0) -> the rest of the path is trivial: go either
                    all the way up, or all the way left -> This should never happen in a realistic
                    reconstruction, be aware!
            '''
            if index<-1:
                return 0,0,[[0,0]],total_cost
            if m>0 and n>0:
                if min_cost[m-1][n] < min_cost[m][n-1]:
                    """
                        Checks for the following

                            x x x x x x x x
                            x x x A x x x x
                            x x B 0 0 0 0 x
                            x x x x x x 0 x
                            x x x x x x 0 0

                        A is the new point to be inserted in the path (represented by zeros)
                        if check[1] means it does cause an intersection. Then we try B, if it
                        returns True, start over. If not, pick B instead of A.
                    """
                    check = surface_intersection(the_path,
                                index,
                                [m-1,n],
                                False,
                                reordered_upper,
                                reordered_lower,
                                skip_intersection)
                    if check[1]:
                        check2 = surface_intersection(the_path,
                                    index,
                                    [m,n-1],
                                    True,
                                    reordered_upper,
                                    reordered_lower,
                                    skip_intersection)
                        if check2[1]:# or min_cost[m-1][n]==np.inf:
                            ##[m,n] -> Bad point that always create intersection
                            if fix_counter<self.fix_limit:
                                m,n,min_cost,index,fix_counter = retract(m,n,min_cost,index,the_path,fix_counter)
                                m,n = the_path[index]
                                continue
                            else:
                                if not check[0][0]==check2[0][0] or not check[0][1]==check2[0][1] :
                                    return 0,0,[[m,n],check[0],check2[0]],total_cost
                                else:
                                    return 0,0,[[m,n],check[0]],total_cost
                        else:
                            if not min_cost[m][n-1] == np.inf:
                                n = n - 1
                            else:
                                if fix_counter<self.fix_limit:
                                    m,n,min_cost,index,fix_counter = retract(m,n,min_cost,index,the_path,fix_counter)
                                    m,n = the_path[index]
                                    continue
                                else:
                                    if not check[0][0]==check2[0][0] or not check[0][1]==check2[0][1] :
                                        return 0,0,[[m,n],check[0],check2[0]],total_cost
                                    else:
                                        return 0,0,[[m,n],check[0]],total_cost
                                n=n-1
                    else:
                        if not min_cost[m-1][n] == np.inf:
                            m = m - 1
                        else:
                            if fix_counter<self.fix_limit:
                                m,n,min_cost,index,fix_counter = retract(m,n,min_cost,index,the_path,fix_counter)
                                m,n = the_path[index]
                                continue
                            else:
                                return 0,0,[[m,n],check[0]],total_cost
                else:
                    check = surface_intersection(the_path,
                                index,
                                [m,n-1],
                                True,
                                reordered_upper,
                                reordered_lower,
                                skip_intersection)
                    if check[1]:
                        check2 = surface_intersection(the_path,
                                    index,
                                    [m-1,n],
                                    False,
                                    reordered_upper,
                                    reordered_lower,
                                    skip_intersection)
                        if check2[1]:
                            if fix_counter<self.fix_limit:
                                m,n,min_cost,index,fix_counter = retract(m,n,min_cost,index,the_path,fix_counter)
                                m,n = the_path[index]
                                continue
                            else:
                                if not check[0][0]==check2[0][0] or not check[0][1]==check2[0][1] :
                                    return 0,0,[[m,n],check[0],check2[0]],total_cost
                                else:
                                    return 0,0,[[m,n],check[0]],total_cost
                        else:
                            if not min_cost[m-1][n] == np.inf:
                                m = m - 1
                            else:
                                if fix_counter<self.fix_limit:
                                    m,n,min_cost,index,fix_counter = retract(m,n,min_cost,index,the_path,fix_counter)
                                    m,n = the_path[index]
                                    continue
                                else:
                                    if not check[0][0]==check2[0][0] or not check[0][1]==check2[0][1] :
                                        return 0,0,[[m,n],check[0],check2[0]],total_cost
                                    else:
                                        return 0,0,[[m,n],check[0]],total_cost
                                m=m-1
                    else:
                        if not min_cost[m][n-1] == np.inf:
                            n = n - 1
                        else:
                            if fix_counter<self.fix_limit:
                                m,n,min_cost,index,fix_counter = retract(m,n,min_cost,index,the_path,fix_counter)
                                m,n = the_path[index]
                                continue
                            else:
                                return 0,0,[[m,n],check[0]],total_cost
            else:
                if m<=0:
                    check = surface_intersection(the_path,
                                index,
                                [m,n-1],
                                True,
                                reordered_upper,
                                reordered_lower,
                                skip_intersection)
                    if check[1]:
                        if fix_counter<self.fix_limit:
                            m,n,min_cost,index,fix_counter = retract(m,n,min_cost,index,the_path,fix_counter)
                            m,n = the_path[index]
                            continue
                        else:
                            return 0,0,[[m,n],check[0]],total_cost
                    n = n - 1
                else:
                    check = surface_intersection(the_path,
                                index,
                                [m-1,n],
                                False,
                                reordered_upper,
                                reordered_lower,
                                skip_intersection)
                    if check[1]:
                        if fix_counter<self.fix_limit:
                            m,n,min_cost,index,fix_counter = retract(m,n,min_cost,index,the_path,fix_counter)
                            m,n = the_path[index]
                            continue
                        else:
                            return 0,0,[[m,n],check[0]],total_cost
                    m = m - 1

            the_path[index+1] = [m,n] ##+1 because of the insert before the loop

            if [m,n] == [0,N-1]:
                var1 = True
            if [m,n] == [M-1,0]:
                var2 = True

            index += 1
        ##var1 and var2 are used to add a single point in order to make the
        ##the graph a closed cicle

        ## The final connections are made by inserting EITHER the top right corner
        ## or the left low corener.
        ## Note that, in this case ONLY, two triangles are made With the begining
        ##and the end of the of the path, making it a closed loop
        ## For that reason, two checks are necessary for intersection.

        if var1:
            check = surface_intersection(the_path,
                        the_path.shape[0],
                        [M-1,0],
                        False,
                        reordered_upper,
                        reordered_lower,
                        final_cond=[True,[0,0]])
            check2 = surface_intersection(the_path,
                        the_path.shape[0],
                        [M-1,0],
                        True,
                        reordered_upper,
                        reordered_lower,
                        final_cond=[True,[M-1,N-1]])
            if check[1] or check2[1]:
                return 0,0,[[m,n],[0,0]],total_cost

            the_path = np.append(the_path, [[M-1,0]], axis=0)
            min_cost[min_cost.shape[0]-1,min_cost.shape[1]-1] += ofinal_matrix[0][N-1]
            self.border_intersection = True
            return [min_cost,the_path,0,total_cost]

        if var2:
            check = surface_intersection(the_path,
                        the_path.shape[0],
                        [0,N-1],
                        True,
                        reordered_upper,
                        reordered_lower,
                        final_cond=[True,[0,0]])
            check2 = surface_intersection(the_path,
                        the_path.shape[0],
                        [0,N-1],
                        False,
                        reordered_upper,
                        reordered_lower,
                        final_cond=[True,[M-1,N-1]])
            if check[1] or check2[1]:
                return 0,0,[[m,n],check[0]],total_cost

            the_path = np.append(the_path, [[0,N-1]], axis=0)
            min_cost[min_cost.shape[0]-1,min_cost.shape[1]-1] += ofinal_matrix[0][N-1]
            self.border_intersection = True
            return [min_cost,the_path,0,total_cost]

        if ofinal_matrix[M-1][0]<ofinal_matrix[0][N-1]:
            check = surface_intersection(the_path,
                        the_path.shape[0],
                        [M-1,0],
                        False,
                        reordered_upper,
                        reordered_lower,
                        final_cond=[True,[0,0]])
            check2 = surface_intersection(the_path,
                        the_path.shape[0],
                        [M-1,0],
                        True,
                        reordered_upper,
                        reordered_lower,
                        final_cond=[True,[M-1,N-1]])
            if check[1] or check2[1]:
                return 0,0,[[m,n],[0,0]],total_cost
            the_path = np.append(the_path, [[M-1,0]], axis=0)
            min_cost[min_cost.shape[0]-1,min_cost.shape[1]-1] += ofinal_matrix[M-1][0]
            self.border_intersection = True
            return [min_cost,the_path,0,total_cost]
        else:
            check = surface_intersection(the_path,
                        the_path.shape[0],
                        [0,N-1],
                        True,
                        reordered_upper,
                        reordered_lower,
                        final_cond=[True,[0,0]])
            check2 = surface_intersection(the_path,
                        the_path.shape[0],
                        [0,N-1],
                        False,
                        reordered_upper,
                        reordered_lower,
                        final_cond=[True,[M-1,N-1]])

            if check[1] or check2[1]:
                return 0,0,[[m,n],check[0]],total_cost
            the_path = np.append(the_path, [[0,N-1]], axis=0)
            min_cost[min_cost.shape[0]-1,min_cost.shape[1]-1] += ofinal_matrix[0][N-1]
            self.border_intersection = True
            return [min_cost,the_path,0,total_cost]
    def __Reordering(self, contour, final_min_cord : int):
        M = contour.points.shape[0]
        reordered = [Point(0,0,0)]*M

        for i in range(M):

            if (i-final_min_cord) >= 0:

                index = i - final_min_cord
                reordered[index] = Point(
                    contour.points[i].x,
                    contour.points[i].y,
                    contour.points[i].z
                    )
            else:
                index = M - final_min_cord + i - 1
                reordered[index] = Point(
                    contour.points[i].x,
                    contour.points[i].y,
                    contour.points[i].z
                    )

        reordered[M-1] = Point(
            contour.points[final_min_cord].x,
            contour.points[final_min_cord].y,
            contour.points[final_min_cord].z
            )

        return Perimeter(np.array(reordered),full_init=False)
    def __FixPathOrder(self, path, final_min_cord : list, M, N) -> np.ndarray:
        fix_path = np.zeros(path.shape, dtype=int)
        for i in range(path.shape[0]):
            if path[i][1]+final_min_cord[1]<=N-2:
                fix_path[i][1] = path[i][1] + final_min_cord[1]
            else:
                fix_path[i][1] = path[i][1] - (N - 1 - final_min_cord[1])
            if path[i][0]+final_min_cord[0]<=M-2:
                fix_path[i][0] = path[i][0] + final_min_cord[0]
            else:
                fix_path[i][0] = path[i][0] - (M - 1 - final_min_cord[0])
        return fix_path
    def __Vertices(self, vertices) -> str:
        string = ""
        for i in range(vertices.shape[0]-1):
            text =  "v " + str(vertices[i].x) +\
                    " " + str(vertices[i].y) +\
                    " " + str(vertices[i].z) + "\n"
            string = string + text
        return string
    def __Edges(self, the_path : np.ndarray, M, N, shift) -> str:
        string = ""

        for i in range(the_path.shape[0]-1):

            if int(the_path[i][1]) == int(the_path[i+1][1]):

                text1 = "f " +str(int(the_path[i][0])+1+shift) +\
                        " " + str(int(the_path[i][1])+1+M+shift) +\
                        " " + str (int(the_path[i+1][0])+1+shift) + "\n"

                string += text1

            else:

                text2 = "f " +str(int(the_path[i][1])+1+M+shift) + \
                        " " + str(int(the_path[i+1][0])+1+shift) + \
                        " " + str (int(the_path[i+1][1])+1+M+shift) + "\n"

                string += text2

        if  int(the_path[the_path.shape[0]-1][0])+1 == int(the_path[the_path.shape[0]-1][1])+1+M or\
            int(the_path[the_path.shape[0]-1][0])+1 == int(the_path[0][0])+1 or\
            int(the_path[0][0])+1 == int(the_path[the_path.shape[0]-1][1])+1+M:

            string =    string + "f " +\
                        str(int(the_path[the_path.shape[0]-1][1])+1+M+shift) + " " +\
                        str(int(the_path[the_path.shape[0]-1][0])+1+shift) + " " +\
                        str (int(the_path[0][1])+1+M+shift) + "\n"

        else:

            string =    string + "f " +\
                        str(int(the_path[the_path.shape[0]-1][0])+1+shift) + " " +\
                        str(int(the_path[the_path.shape[0]-1][1])+1+M+shift) + " " +\
                        str (int(the_path[0][0])+1+shift) + "\n"

        return string
    def __str__(self):
        return "Surface shape = {S}\nPerimeters shape = {L}".format(
                                            L = [self.slices[i].points.shape[0] for i in range(self.slices.shape[0])],
                                            S = (self.slices.shape[0]))
