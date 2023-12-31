from PIL import Image, ImageStat
import heapq

def heuristic(current, goal):
    return abs(current[0] - goal[0]) + abs(current[1] - goal[1])

def astar(grid_size, obstacles, start, goal):
    open_set = []
    closed_set = set()
    heapq.heappush(open_set, (0, start, None))

    while open_set:
        _, current, parent = heapq.heappop(open_set)

        if current == goal:
            path = []
            while parent:
                path.append(current)
                _, current, parent = parent
            path.append(start)
            return path[::-1]

        closed_set.add(tuple(current))

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_position = [current[0] + dx, current[1] + dy]

            if new_position[0] < 0 or new_position[0] >= grid_size or new_position[1] < 0 or new_position[1] >= grid_size:
                continue

            if new_position in obstacles or tuple(new_position) in closed_set:
                continue

            new_f = heuristic(new_position, goal)

            heapq.heappush(open_set, (new_f, new_position, (_, current, parent)))

    return None

def image_into_maze(image, cell_count, grid_size):
    obsticles = []
    start = None
    end = None
    for y in range(0, cell_count):
        for x in range(0, cell_count):
            crop_position = (x*grid_size, y*grid_size, (x+1)*grid_size, (y+1)*grid_size)
            cropped_image = image.crop(crop_position)
            median = ImageStat.Stat(cropped_image).median
            r, g, b = median[0] > 125, median[1] > 125, median[2] > 125
            if r and g and b: #white
                continue
            if not r and not g and not b: #black
                obsticles.append([x, y])
                continue
            
            #RGB
            if g:
                start = [x, y]
            elif r:
                end = [x, y]
    return [obsticles, start, end]

def optimize_instructions(instructions):
    current_forward = 0
    optimized_instructions = []
    instructions.append("end")
    
    for instruction in range(len(instructions)-1):
        if instructions[instruction] == "Go forward":
            current_forward += 1
        if not instructions[instruction+1] == "Go forward":
            optimized_instructions.append("Go forward x" + str(current_forward))
            optimized_instructions.append(instructions[instruction+1])
            current_forward = 0
            
    optimized_instructions.pop()
    
    return optimized_instructions

def append_instructions(instructions, facing, to_left, to_right, new_facing):
    if facing == to_left:
        instructions.append("Turn left")
    if facing == to_right:
        instructions.append("Turn right")
        
    instructions.append("Go forward")
    return [instructions, new_facing]

def path_into_instructions(path):
    instructions = []
    
    facing = [path[1][0] - path[0][0], path[1][1] - path[0][1]]
    for position in range(0, len(path)-1):
        if path[position][0] < path[position+1][0]: #Go right
            instructions, facing = append_instructions(instructions, facing, [0, 1], [0, -1], [1, 0])
            continue
        
        if path[position][0] > path[position+1][0]: #Go left
            instructions, facing = append_instructions(instructions, facing, [0, -1], [0, 1], [-1, 0])
            continue
        
        if path[position][1] < path[position+1][1]: #Go down
            instructions, facing = append_instructions(instructions, facing, [-1, 0], [1, 0], [0, 1])
            continue
        
        if path[position][1] > path[position+1][1]: #Go up
            instructions, facing = append_instructions(instructions, facing, [1, 0], [-1, 0], [0, -1])
            continue
    
    return optimize_instructions(instructions)
        
        
def image_into_instructions(grid_size, image_location):
    image = Image.open(image_location)
    image_size = image.size[0]
    cell_count = int(image_size/grid_size)
    obsticles, start, end = image_into_maze(image, cell_count, grid_size)
    
    path = astar(grid_size, obsticles, start, end)
    instructions = path_into_instructions(path)
    
    #put maze visualization and better looking instructions here
    
    for y in range(0, cell_count):
        for x in range(0, cell_count):
            if [x, y] in obsticles:
                print("#", end=" ")
                continue
            if [x, y] == start:
                print("s", end=" ")
                continue
            if [x, y] == end:
                print("e", end=" ")
                continue
            if [x, y] in path:
                print(".", end=" ")
                continue
            
            print("  ", end="")
            
        print()
        
    for i, instruction in enumerate(instructions):
        print(i+1, ":", instruction)
        
    x = input("Press anything to exit...")
    
    return instructions
 

#put your data here 
instructions = image_into_instructions(10, "./maze.jpg")
