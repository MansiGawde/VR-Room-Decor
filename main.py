import cv2
import numpy as np
import os

# =============================
# LOAD IMAGE
# =============================

def load_image(path):
    if not os.path.exists(path):
        print("❌ Missing:", path)
        return None

    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    if img is None:
        print("❌ Cannot load:", path)
        return None

    if img.shape[2] != 4:
        print("❌ Must be PNG with transparency:", path)
        return None

    # Resize large images automatically
    max_width = 300
    if img.shape[1] > max_width:
        scale = max_width / img.shape[1]
        img = cv2.resize(img, None, fx=scale, fy=scale)

    print("✅ Loaded:", path)
    return img


sofa  = load_image("sofa.png")
table = load_image("table.png")
lamp  = load_image("lamp.png")
chair = load_image("chair.png")

# =============================
# GLOBALS
# =============================

objects = []
dragging = False
selected = -1
offset_x = 0
offset_y = 0

# =============================
# CAMERA FULLSCREEN
# =============================

cap = cv2.VideoCapture(0)

cv2.namedWindow("VR Room Decor", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("VR Room Decor",
                      cv2.WND_PROP_FULLSCREEN,
                      cv2.WINDOW_FULLSCREEN)

# =============================
# SAFE OVERLAY FUNCTION
# =============================

def overlay(bg, img, x, y):
    h, w = img.shape[:2]
    bg_h, bg_w = bg.shape[:2]

    if x >= bg_w or y >= bg_h or x + w <= 0 or y + h <= 0:
        return bg

    if x < 0:
        img = img[:, -x:]
        w = img.shape[1]
        x = 0

    if y < 0:
        img = img[-y:, :]
        h = img.shape[0]
        y = 0

    if x + w > bg_w:
        img = img[:, :bg_w - x]
        w = img.shape[1]

    if y + h > bg_h:
        img = img[:bg_h - y, :]
        h = img.shape[0]

    if w <= 0 or h <= 0:
        return bg

    alpha = img[:, :, 3] / 255.0
    alpha = alpha[:, :, np.newaxis]

    bg_region = bg[y:y+h, x:x+w]

    bg[y:y+h, x:x+w] = (
        alpha * img[:, :, :3] +
        (1 - alpha) * bg_region
    ).astype(np.uint8)

    return bg

# =============================
# TRANSFORM (ROTATE + SCALE)
# =============================

def transform(obj):
    resized = cv2.resize(obj["original"],
                         None,
                         fx=obj["scale"],
                         fy=obj["scale"])

    h, w = resized.shape[:2]
    center = (w // 2, h // 2)

    matrix = cv2.getRotationMatrix2D(center,
                                     obj["angle"],
                                     1.0)

    rotated = cv2.warpAffine(
        resized,
        matrix,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_TRANSPARENT
    )

    return rotated

# =============================
# MOUSE EVENTS
# =============================

def mouse(event, x, y, flags, param):
    global dragging, selected, offset_x, offset_y

    if event == cv2.EVENT_LBUTTONDOWN:
        for i in reversed(range(len(objects))):
            obj = objects[i]
            ox, oy = obj["x"], obj["y"]
            h, w = obj["current"].shape[:2]

            if ox < x < ox + w and oy < y < oy + h:
                selected = i
                dragging = True
                offset_x = x - ox
                offset_y = y - oy
                break

    elif event == cv2.EVENT_MOUSEMOVE and dragging:
        objects[selected]["x"] = x - offset_x
        objects[selected]["y"] = y - offset_y

    elif event == cv2.EVENT_LBUTTONUP:
        dragging = False

    elif event == cv2.EVENT_MOUSEWHEEL and objects:
        obj = objects[-1]
        if flags > 0:
            obj["scale"] += 0.05
        else:
            obj["scale"] = max(0.1, obj["scale"] - 0.05)


cv2.setMouseCallback("VR Room Decor", mouse)

# =============================
# MAIN LOOP
# =============================

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # Small black control panel
    cv2.rectangle(frame, (20, 20), (230, 160), (20, 20, 20), -1)

    cv2.putText(frame, "1 Sofa", (35, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    cv2.putText(frame, "2 Table", (35, 75),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    cv2.putText(frame, "3 Lamp", (35, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    cv2.putText(frame, "4 Chair", (35, 125),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    # Draw objects
    for obj in objects:
        obj["current"] = transform(obj)
        frame = overlay(frame,
                        obj["current"],
                        obj["x"],
                        obj["y"])

    cv2.imshow("VR Room Decor", frame)

    key = cv2.waitKey(1) & 0xFF

    # Add objects safely
    if key == ord('1') and sofa is not None:
        objects.append({"original": sofa, "current": sofa,
                        "x": 400, "y": 250,
                        "scale": 1.0, "angle": 0})

    elif key == ord('2') and table is not None:
        objects.append({"original": table, "current": table,
                        "x": 400, "y": 250,
                        "scale": 1.0, "angle": 0})

    elif key == ord('3') and lamp is not None:
        objects.append({"original": lamp, "current": lamp,
                        "x": 400, "y": 250,
                        "scale": 1.0, "angle": 0})

    elif key == ord('4') and chair is not None:
        objects.append({"original": chair, "current": chair,
                        "x": 400, "y": 250,
                        "scale": 1.0, "angle": 0})

    # Zoom keys
    elif (key == ord('+') or key == ord('=')) and objects:
        objects[-1]["scale"] += 0.05

    elif key == ord('-') and objects:
        objects[-1]["scale"] = max(0.1,
                                   objects[-1]["scale"] - 0.05)

    # Rotate
    elif key == ord('r') and objects:
        objects[-1]["angle"] += 5

    # Delete
    elif key == ord('d') and objects:
        objects.pop()

    # Save
    elif key == ord('s'):
        cv2.imwrite("room_design.png", frame)
        print("💾 Saved")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()