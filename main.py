import turtle
import math
import random

# ==========================================
# CONFIGURACIÓN
# ==========================================

WIDTH = 1000
HEIGHT = 700

screen = turtle.Screen()
screen.setup(WIDTH, HEIGHT)
screen.title("Two cats under the moon ♡")
screen.bgcolor("#0A1029")
screen.tracer(0)

# Una tortuga para el fondo (se dibuja una sola vez)
# y otra para todo lo que se mueve.
bg_pen = turtle.Turtle()
fg_pen = turtle.Turtle()

for t in (bg_pen, fg_pen):
    t.hideturtle()
    t.speed(0)
    t.penup()

pen = bg_pen  # tortuga activa

# ---------- Colores ----------
SKY_TOP = "#0A1029"
SKY_HORIZON = "#34457A"
MOON = "#FFF1C9"
STAR = "#FFF4D6"

CREAM = "#FFF0D9"
CREAM_DARK = "#E8CBAA"
PINK = "#EFA6B8"

GROUND = "#263C4B"
GROUND_RIM = "#3C586B"
SHADOW = "#16222E"
HEART_PINK = "#F28CA3"
TEXT_COLOR = "#F8D7D0"

# Paletas de los gatitos
TABBY = dict(
    base="#8A6A50",
    patch="#A98767",
    stripe="#4A3326",
    outline="#33241A",
    rim="#D2B48E",
    inner="#D99AA3",
    whisker="#E8DCC8",
    tip="#3E2B20",
)

CREAM_CAT = dict(
    base=CREAM,
    patch="#F3DDBF",
    stripe=None,
    outline="#D2AE86",
    rim="#FFFFFF",
    inner=PINK,
    whisker="#FFFFFF",
    tip="#E5C7A2",
)

# Geometría de la escena
CAT_Y = -105
SCALE = 0.65
TIP_Y = -170        # punta inferior del corazón
FINAL_X = 88        # distancia de cada gatito al centro al final

LEAD = 20           # puntos (densos) del tramo cola -> punta del corazón
HEART_PTS = 90      # puntos (densos) de media curva del corazón
N = 60              # puntos finales de cada cola


# ==========================================
# UTILIDADES
# ==========================================

def hex_to_rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    a = hex_to_rgb(c1)
    b = hex_to_rgb(c2)
    return "#%02X%02X%02X" % tuple(
        int(a[i] + (b[i] - a[i]) * t) for i in range(3)
    )


def lerp(a, b, t):
    return a + (b - a) * t


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def sky_at(y):
    return mix(SKY_TOP, SKY_HORIZON, (350 - y) / 470)


# ==========================================
# FUNCIONES GEOMÉTRICAS
# ==========================================

def transform(x, y, cx, cy, scale):
    return cx + x * scale, cy + y * scale


def polygon(points, color, outline=None, width=2,
            cx=0, cy=0, scale=1):

    if outline is None:
        outline = color

    pen.penup()
    pen.goto(*transform(*points[0], cx, cy, scale))
    pen.color(outline, color)
    pen.pensize(max(1, width * scale))
    pen.pendown()
    pen.begin_fill()

    for point in points[1:]:
        pen.goto(*transform(*point, cx, cy, scale))

    pen.goto(*transform(*points[0], cx, cy, scale))
    pen.end_fill()
    pen.penup()


def ellipse(x, y, rx, ry, color, outline=None,
            width=2, cx=0, cy=0, scale=1):

    n = int(max(12, min(56, max(rx, ry) * scale * 0.7)))
    points = []

    for i in range(n):
        angle = 2 * math.pi * i / n
        points.append((
            x + rx * math.cos(angle),
            y + ry * math.sin(angle)
        ))

    polygon(points, color, outline, width, cx, cy, scale)


def line(points, color, width=2, cx=0, cy=0, scale=1):
    pen.penup()
    pen.goto(*transform(*points[0], cx, cy, scale))
    pen.pensize(max(1, width * scale))
    pen.pencolor(color)

    for point in points[1:]:
        pen.pendown()
        pen.goto(*transform(*point, cx, cy, scale))

    pen.penup()


def dot(x, y, size, color):
    pen.penup()
    pen.goto(x, y)
    pen.dot(max(1, size), color)


def write_text(x, y, message, size, color):
    pen.penup()
    pen.goto(x, y)
    pen.color(color)
    pen.write(
        message,
        align="center",
        font=("Georgia", size, "italic")
    )


# ==========================================
# CORAZÓN
# ==========================================

def heart_xy(t):
    x = 16 * math.sin(t) ** 3
    y = (
        13 * math.cos(t)
        - 5 * math.cos(2 * t)
        - 2 * math.cos(3 * t)
        - math.cos(4 * t)
    )
    return x, y


def draw_heart(x, y, scale, color, points=28):
    pts = []

    for i in range(points + 1):
        px, py = heart_xy(2 * math.pi * i / points)
        pts.append((x + px * scale, y + (py + 2.5) * scale))

    polygon(pts, color, color, 1)


# ==========================================
# FONDO (se dibuja una sola vez)
# ==========================================

def hill_far(x):
    return -215 + 34 * math.sin(x * 0.009 + 0.6) \
        + 18 * math.sin(x * 0.021 + 2.0)


def hill_near(x):
    return -238 + 16 * math.sin(x * 0.012 + 3.0) \
        + 8 * math.sin(x * 0.031 + 1.0)


def draw_pine(x, y, h, color):
    for k in range(3):
        base_y = y + h * 0.28 * k
        w = 17 - k * 4
        polygon([
            (x - w, base_y),
            (x, base_y + h * 0.55),
            (x + w, base_y)
        ], color, width=1)

    polygon([(x - 2, y - 6), (x - 2, y), (x + 2, y), (x + 2, y - 6)],
            color, width=1)


def draw_static():
    global pen
    pen = bg_pen

    # --- Cielo con degradado ---
    y = 370
    while y > -300:
        polygon([
            (-520, y), (520, y),
            (520, y - 10), (-520, y - 10)
        ], sky_at(y - 5), width=1)
        y -= 8

    # --- Luna con resplandor ---
    mx, my, R = 335, 235, 70

    for i in range(10, 0, -1):
        r = R + i * 7
        k = 1 - i / 10
        ellipse(mx, my, r, r,
                mix(sky_at(my), MOON, 0.03 + 0.22 * k * k),
                width=1)

    # Creciente: círculo grande menos círculo desplazado
    ix, iy, ir = mx + 34, my + 14, 66
    left = []
    right = []
    yy = my + R

    while yy >= my - R:
        w = math.sqrt(max(0, R * R - (yy - my) ** 2))
        l = mx - w
        r = mx + w
        dy = yy - iy

        if abs(dy) < ir:
            r = min(r, ix - math.sqrt(ir * ir - dy * dy))

        if r - l > 1:
            left.append((l, yy))
            right.append((r, yy))

        yy -= 2

    polygon(left + right[::-1], MOON, MOON, 1)

    # --- Colinas lejanas ---
    far = [(x, hill_far(x)) for x in range(-520, 521, 20)]
    polygon(far + [(520, -320), (-520, -320)], "#1C2C54", width=1)

    # Pinitos en la colina
    random.seed(21)
    for x in (-470, -430, -395, -350, 300, 340, 390, 440, 480):
        draw_pine(x, hill_far(x) - 4, random.uniform(38, 62), "#142040")

    # --- Colinas cercanas ---
    near = [(x, hill_near(x)) for x in range(-520, 521, 20)]
    polygon(near + [(520, -320), (-520, -320)], "#1A2D45", width=1)

    # --- Suelo con borde iluminado por la luna ---
    ellipse(0, -388, 655, 172, GROUND_RIM, width=1)
    ellipse(0, -394, 650, 170, GROUND, width=1)

    # --- Hierbitas ---
    random.seed(5)
    for x in range(-460, 461, 22):
        gy = -392 + 170 * math.sqrt(max(0, 1 - (x / 650) ** 2))

        for k in range(3):
            bx = x + k * 5 - 5
            lean = random.uniform(-9, 9)
            h = random.uniform(12, 24)
            col = random.choice(["#46706B", "#37595A", "#5A8478"])

            line([
                (bx, gy),
                (bx + lean * 0.5, gy + h * 0.6),
                (bx + lean, gy + h)
            ], col, 2)

    pen = fg_pen


# ==========================================
# ELEMENTOS ANIMADOS DEL CIELO Y EL SUELO
# ==========================================

random.seed(12)

stars = []
while len(stars) < 70:
    sx = random.randint(-480, 480)
    sy = random.randint(-10, 335)

    # Evitamos tapar la luna
    if math.hypot(sx - 335, sy - 235) < 125:
        continue

    stars.append({
        "x": sx,
        "y": sy,
        "size": random.choice([2, 3, 3, 4, 5]),
        "phase": random.uniform(0, math.pi * 2)
    })

fireflies = []
for _ in range(11):
    fireflies.append({
        "x": random.uniform(-440, 440),
        "y": random.uniform(-270, -70),
        "fx": random.uniform(0.012, 0.03),
        "fy": random.uniform(0.015, 0.035),
        "ph": random.uniform(0, math.pi * 2),
    })

shoot = None
love = []


def draw_stars(frame):
    for s in stars:
        b = 0.5 + 0.5 * math.sin(frame * 0.06 + s["phase"])
        color = mix(sky_at(s["y"]), STAR, 0.35 + 0.65 * b)
        size = s["size"] * (0.7 + b * 0.5)

        dot(s["x"], s["y"], size, color)

        # Destello en forma de cruz para las más grandes
        if s["size"] >= 4 and b > 0.75:
            L = 4 + 6 * b
            c = mix(sky_at(s["y"]), STAR, 0.7)
            line([(s["x"] - L, s["y"]), (s["x"] + L, s["y"])], c, 1)
            line([(s["x"], s["y"] - L), (s["x"], s["y"] + L)], c, 1)


def draw_shooting_star():
    global shoot

    if shoot is None:
        return

    shoot["t"] += 1
    x = shoot["x"] + shoot["t"] * 15
    y = shoot["y"] - shoot["t"] * 6

    for i in range(7):
        a = 1 - i / 7
        line([
            (x - i * 15, y + i * 6),
            (x - (i + 1) * 15, y + (i + 1) * 6)
        ], mix(sky_at(y), "#FFFFFF", a * (1 - shoot["t"] / 40)),
            max(1, 3 - i * 0.4))

    if shoot["t"] > 38:
        shoot = None


def draw_fireflies(frame):
    for f in fireflies:
        x = f["x"] + 35 * math.sin(frame * f["fx"] + f["ph"])
        y = f["y"] + 18 * math.sin(frame * f["fy"] + f["ph"] * 2)
        b = 0.5 + 0.5 * math.sin(frame * 0.07 + f["ph"])

        dot(x, y, 16, mix(sky_at(y), "#E8F59A", 0.10 + 0.18 * b))
        dot(x, y, 9, mix(sky_at(y), "#E8F59A", 0.25 + 0.3 * b))
        dot(x, y, 4, mix("#E8F59A", "#FFFFFF", b))


# ==========================================
# GATITOS VISTOS DESDE ATRÁS
# ==========================================

def path_length(pts):
    return sum(
        math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
        for i in range(len(pts) - 1)
    )


def resample(pts, n):
    """Reparte n puntos a distancias iguales a lo largo de la curva."""
    d = [0.0]
    for i in range(1, len(pts)):
        d.append(d[-1] + math.hypot(pts[i][0] - pts[i - 1][0],
                                    pts[i][1] - pts[i - 1][1]))
    total = d[-1]
    out = []
    j = 0

    for k in range(n):
        target = total * k / (n - 1)
        while j < len(pts) - 2 and d[j + 1] < target:
            j += 1
        seg = (d[j + 1] - d[j]) or 1
        u = (target - d[j]) / seg
        out.append((
            lerp(pts[j][0], pts[j + 1][0], u),
            lerp(pts[j][1], pts[j + 1][1], u)
        ))

    return out


def relaxed_tail(bx, by, inn, frame, phase):
    """Cola relajada, moviéndose suavemente."""
    pts = []

    for i in range(80):
        u = i / 79
        sway = 14 * math.sin(u * 3.2 + frame * 0.14 + phase) * u
        x = bx + inn * (18 * u + 30 * u ** 3) + sway
        y = by + 185 * u ** 0.9
        pts.append((x, y))

    return resample(pts, N)


def smooth_pts(pts, passes):
    for _ in range(passes):
        new = [pts[0]]

        for i in range(1, len(pts) - 1):
            new.append((
                (pts[i - 1][0] + 2 * pts[i][0] + pts[i + 1][0]) / 4,
                (pts[i - 1][1] + 2 * pts[i][1] + pts[i + 1][1]) / 4
            ))

        new.append(pts[-1])
        pts = new

    return pts


def target_tail(bx, by, side, s):
    """
    Cola formando media silueta de corazón.
    Cada cola sale de su gatito, cruza hasta la punta inferior
    del corazón y sube por el lado contrario hasta el centro.
    """
    tip = (0.0, TIP_Y)
    c = (bx * 0.35, TIP_Y - 30)
    pts = []

    for i in range(LEAD):
        u = i / LEAD
        x = (1 - u) ** 2 * bx + 2 * (1 - u) * u * c[0] + u * u * tip[0]
        y = (1 - u) ** 2 * by + 2 * (1 - u) * u * c[1] + u * u * tip[1]
        pts.append((x, y))

    for k in range(HEART_PTS + 1):
        t = math.pi + side * math.pi * k / HEART_PTS
        hx, hy = heart_xy(t)
        pts.append((hx * s, TIP_Y + (hy + 17) * s))

    return resample(smooth_pts(pts, 4), N)


def solve_heart_scale():
    """
    Busca el tamaño del corazón para que cada cola mida lo mismo
    que una cola normal: así no se estira al formar el corazón.
    """
    bx = FINAL_X - 29
    by = CAT_Y - 150 * SCALE
    goal = path_length(relaxed_tail(bx, by, 1, 0, 0))
    lo, hi = 0.5, 8.0

    for _ in range(25):
        mid = (lo + hi) / 2
        if path_length(target_tail(bx, by, -1, mid)) < goal:
            lo = mid
        else:
            hi = mid

    return (lo + hi) / 2


HEART_S = solve_heart_scale()


def draw_tail(pts, pal, width=13):
    # Contorno, cuerpo y rayas de la cola
    line(pts, pal["outline"], width + 4)
    line(pts, pal["base"], width)

    if pal["stripe"]:
        for i in range(4, len(pts) - 9, 5):
            p0 = pts[i - 1]
            p1 = pts[i + 1]
            tx = p1[0] - p0[0]
            ty = p1[1] - p0[1]
            ln = math.hypot(tx, ty)

            if ln == 0:
                continue

            nx = -ty / ln
            ny = tx / ln
            half = width / 2 - 1
            px, py = pts[i]

            line([
                (px - nx * half, py - ny * half),
                (px + nx * half, py + ny * half)
            ], pal["stripe"], 4)

    # Punta de la cola
    line(pts[-9:], pal["tip"], width)


def draw_cat_back(cx, cy, scale, pal, frame, walking, hx=0.0, step=0.0):
    base = pal["base"]
    patch = pal["patch"]
    stripe = pal["stripe"]
    outline = pal["outline"]
    rim = pal["rim"]

    swing = math.sin(frame * 0.35 + step) if walking else 0
    lift_l = max(0, swing) * 9
    lift_r = max(0, -swing) * 9
    bob = abs(swing) * 3

    # Sombra sobre el suelo
    ellipse(0, -200, 90, 15, SHADOW, width=1,
            cx=cx, cy=cy, scale=scale)

    cy = cy + bob
    kw = dict(cx=cx, cy=cy, scale=scale)

    def P(points):
        return [(x + hx, y) for x, y in points]

    # Patitas traseras
    ellipse(-35, -180 + lift_l, 23, 22, base, outline, 2, **kw)
    ellipse(35, -180 + lift_r, 23, 22, base, outline, 2, **kw)

    # Cuerpo (con un borde de luz de la luna)
    ellipse(3, -103, 69, 91, rim, **kw)
    ellipse(0, -105, 66, 88, base, outline, 2, **kw)

    # Zona clara de la espalda
    ellipse(0, -120, 38, 53, patch, patch, 1, **kw)

    # Muslos
    ellipse(-37, -140, 30, 42, base, outline, 2, **kw)
    ellipse(37, -140, 30, 42, base, outline, 2, **kw)

    # Rayas del cuerpo (atigrado)
    if stripe:
        for yy in (-62, -82, -102):
            hw = 66 * math.sqrt(1 - ((yy + 105) / 88) ** 2)
            line([
                (-hw + 3, yy), (-hw + 20, yy - 6), (-hw + 34, yy - 4)
            ], stripe, 5, **kw)
            line([
                (hw - 3, yy), (hw - 20, yy - 6), (hw - 34, yy - 4)
            ], stripe, 5, **kw)

        for a, b in ((-55, -72), (-82, -100), (-110, -130)):
            line([(0, a), (0, b)], stripe, 5, **kw)

        for yy in (-120, -140, -160):
            hw = 30 * math.sqrt(1 - ((yy + 140) / 42) ** 2)
            line([(-37 - hw + 2, yy), (-37 - hw + 19, yy + 3)],
                 stripe, 4, **kw)
            line([(37 + hw - 2, yy), (37 + hw - 19, yy + 3)],
                 stripe, 4, **kw)

    # Cabeza: borde de luz
    ellipse(hx + 3, 32, 86, 80, rim, **kw)

    # Orejas (detrás de la cabeza para ocultar su base)
    polygon(P([(-75, 60), (-70, 137), (-18, 91)]),
            base, outline, 2, **kw)
    polygon(P([(18, 91), (70, 137), (75, 60)]),
            base, outline, 2, **kw)

    # Cabeza
    ellipse(hx, 30, 83, 77, base, outline, 2, **kw)

    # Mechones de pelo en las mejillas
    polygon(P([(-78, 48), (-98, 32), (-82, 22), (-100, 8), (-76, 12)]),
            base, base, 1, **kw)
    polygon(P([(78, 48), (98, 32), (82, 22), (100, 8), (76, 12)]),
            base, base, 1, **kw)

    # Bigotitos asomando a los lados
    for sy, ey in ((22, 30), (14, 12)):
        line(P([(-86, sy), (-118, ey)]), pal["whisker"], 1.5, **kw)
        line(P([(86, sy), (118, ey)]), pal["whisker"], 1.5, **kw)

    # Rayas de la cabeza (atigrado)
    if stripe:
        line(P([(-13, 102), (-10, 82)]), stripe, 5, **kw)
        line(P([(0, 105), (0, 72)]), stripe, 5, **kw)
        line(P([(13, 102), (10, 82)]), stripe, 5, **kw)

        line(P([(-82, 38), (-60, 43)]), stripe, 5, **kw)
        line(P([(-80, 18), (-58, 24)]), stripe, 5, **kw)
        line(P([(82, 38), (60, 43)]), stripe, 5, **kw)
        line(P([(80, 18), (58, 24)]), stripe, 5, **kw)

    # Interior de las orejas
    polygon(P([(-65, 79), (-62, 119), (-34, 94)]),
            pal["inner"], pal["inner"], 1, **kw)
    polygon(P([(34, 94), (62, 119), (65, 79)]),
            pal["inner"], pal["inner"], 1, **kw)

    # Pequeño mechón de pelo
    polygon(P([(-15, 102), (0, 120), (15, 102)]),
            base, base, 1, **kw)


# ==========================================
# ANIMACIÓN
# ==========================================

frame = 0
progress = 0.0    # acercamiento de los gatitos
settle = 0        # tiempo desde que llegaron
heart_t = 0.0     # progreso de las colas hacia el corazón
text_t = 0        # aparición del texto


def animate():
    global frame, progress, settle, heart_t, text_t, shoot

    pen.clear()

    # ----- Estado de la animación -----
    progress = min(progress + 0.0055, 1.0)
    smooth = smoothstep(progress)
    walking = progress < 1

    if not walking:
        settle += 1
        if settle > 25:
            heart_t = min(1.0, heart_t + 0.0075)

    e = smoothstep(heart_t)
    look = smoothstep(settle / 30)
    pulse = 1 + 0.025 * math.sin(frame * 0.15) * (1 if heart_t >= 1 else 0)
    s = HEART_S * pulse

    # ----- Cielo -----
    if frame % 420 == 150:
        shoot = {
            "x": random.randint(-380, 0),
            "y": random.randint(230, 320),
            "t": 0
        }

    draw_stars(frame)
    draw_shooting_star()
    draw_fireflies(frame)

    # ----- Posiciones -----
    left_x = -(360 - (360 - FINAL_X) * smooth)
    right_x = -left_x

    # ----- Resplandor del corazón -----
    if e > 0:
        cy_h = TIP_Y + 14.5 * s
        glow_color = sky_at(cy_h)

        for k, a in ((1.9, 0.06), (1.5, 0.10), (1.2, 0.15)):
            pts = []
            for i in range(61):
                px, py = heart_xy(2 * math.pi * i / 60)
                pts.append((px * s * k, cy_h + (py + 2.5) * s * k))

            polygon(pts, mix(glow_color, HEART_PINK, a * e),
                    width=1)

    # ----- Colitas (detrás de los gatitos) -----
    cats = (
        (left_x, 1, TABBY, 0.0),
        (right_x, -1, CREAM_CAT, 1.7),
    )

    for cx_, inn, pal, ph in cats:
        bx = cx_ + inn * 29
        by = CAT_Y - 150 * SCALE

        pts = relaxed_tail(bx, by, inn, frame, ph)

        if e > 0:
            target = target_tail(bx, by, -inn, s)
            pts = [
                (lerp(p[0], q[0], e), lerp(p[1], q[1], e))
                for p, q in zip(pts, target)
            ]

        draw_tail(pts, pal)

    # ----- Gatitos -----
    for cx_, inn, pal, ph in cats:
        draw_cat_back(
            cx_, CAT_Y, SCALE, pal, frame, walking,
            hx=inn * look * 8, step=ph
        )

    # ----- Corazoncitos que suben -----
    if heart_t >= 1 and random.random() < 0.07:
        love.append({
            "x": random.uniform(-30, 30),
            "y": random.uniform(TIP_Y + 25, TIP_Y + 60),
            "vy": random.uniform(0.7, 1.3),
            "size": random.uniform(0.3, 0.6),
            "age": 0,
            "ph": random.uniform(0, 6.28),
        })

    for h in love[:]:
        h["age"] += 1
        h["y"] += h["vy"]
        life = h["age"] / 170

        if life >= 1:
            love.remove(h)
            continue

        x = h["x"] + 8 * math.sin(h["age"] * 0.08 + h["ph"])
        color = mix("#F7A1B5", sky_at(h["y"]), life ** 1.5)
        draw_heart(x, h["y"], h["size"], color, 24)

    # ----- Texto final -----
    if heart_t >= 1:
        text_t += 1
        a = smoothstep(text_t / 45)

        write_text(
            0, -310,
            "Contigo, cualquier lugar es mi favorito ♡",
            20,
            mix(GROUND, TEXT_COLOR, a)
        )

    screen.update()

    frame += 1
    screen.ontimer(animate, 33)


# ==========================================
# INICIO
# ==========================================

draw_static()
pen = fg_pen
screen.update()

animate()
screen.mainloop()
