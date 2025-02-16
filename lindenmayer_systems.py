import turtle, random

axiom_dict = {
    'baby\'s breath': 'X',
    'gnarly weed': 'F',
    'chaos twig junior': 'F',
    'lopsided frond': 'X',
    'floofy bush': 'F',
    'symmetrical frond': 'X',
    'chaos twig senior': 'X'
}

def generate_instructions(num_iter, l_sys_style):

    axiom = axiom_dict[l_sys_style]
    old_instruct = axiom

    for _ in range(num_iter):

        new_instruct = ''

        for cmd in old_instruct:

            if l_sys_style == 'baby\'s breath':
                if cmd == 'X':
                    new_instruct += 'F[-X]+X'
                elif cmd == 'F':
                    new_instruct += 'FF'
                else:
                    new_instruct += cmd

            elif l_sys_style == 'gnarly weed':
                if cmd == 'F':
                    new_instruct += 'F[-F]F[+F][F]'
                else:
                    new_instruct += cmd

            elif l_sys_style == 'chaos twig junior':
                uncertainty = random.random()
                if cmd == 'F':
                    if uncertainty < 0.33:
                        new_instruct += 'F[+F]F[-F]F'
                    elif uncertainty >= 0.33 and uncertainty < 0.66:
                        new_instruct += 'F[+F]F'
                    elif uncertainty >= 0.66:
                        new_instruct += 'F[-F]F'
                else:
                    new_instruct += cmd

            elif l_sys_style == 'lopsided frond':
                if cmd == 'X':
                    new_instruct += 'F-[[X]+X]+F[+FX]-X'
                elif cmd == 'F':
                    new_instruct += 'FF'
                else:
                    new_instruct += cmd

            elif l_sys_style == 'floofy bush':
                if cmd == 'F':
                    new_instruct += 'FF+[+F-F-F]-[-F+F+F]'
                else:
                    new_instruct += cmd

            elif l_sys_style == 'symmetrical frond':
                if cmd == 'X':
                    new_instruct += 'F[+X][-X]FX'
                elif cmd == 'F':
                    new_instruct += 'FF'
                else:
                    new_instruct += cmd

            elif l_sys_style == 'chaos twig senior':
                uncertainty = random.random()
                if cmd == 'X':
                    if uncertainty < 0.5:
                        new_instruct += 'F[+X][-X]FX'
                    elif uncertainty >= 0.5 and uncertainty < 0.75:
                        new_instruct += 'F[-X]FX'
                    else:
                        new_instruct += 'F[+X]FX'
                elif cmd == 'F':
                    new_instruct += 'FF'
                else:
                    new_instruct += cmd



        old_instruct = new_instruct

    return old_instruct

def draw_L_sys(turtle, instructions, angle, distance):
    pos_callstack = []
    for comm in instructions:
        if comm == 'F':
            turtle.forward(distance)
        elif comm == 'X':
            turtle.backward(distance)
        elif comm == '+':
            turtle.right(angle)
        elif comm == '-':
            turtle.left(angle)
        elif comm == '[':
            pos_callstack.append([turtle.heading(), turtle.xcor(), turtle.ycor()])
        elif comm == ']':
            return_to_pos = pos_callstack.pop()
            turtle.seth(return_to_pos[0])
            turtle.teleport(return_to_pos[1], return_to_pos[2])

def main():
    pen = turtle.Turtle()
    wn = turtle.Screen()

    wn.colormode(255)
    pen.hideturtle()
    pen.pencolor(99, 140, 83) # Change colours --- these are rgb values
    pen.speed(10)
    pen.seth(90)
    pen.teleport(0, -(wn.window_height() // 2))

    instructions = generate_instructions(6, 'chaos twig senior')
    draw_L_sys(pen, instructions, 22.5, 4)

    wn.exitonclick()

if __name__ == '__main__':
    main()
