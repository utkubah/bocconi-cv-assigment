import cv2
import numpy as np
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent

IMG1_PATH = str(ROOT / "data" / "sda_bocconi" / "photo1.png")
IMG2_PATH = str(ROOT / "data" / "sda_bocconi" / "photo2.png")
OUT_NPZ   = str(ROOT / "manual_points.npz")

N_PAIRS = 20

pts1 = []
pts2 = []

def draw_points(img, pts, color):
    vis = img.copy()
    for (x, y) in pts:
        cv2.circle(vis, (int(x), int(y)), 5, color, -1)
    return vis

def main():
    global pts1, pts2

    img1 = cv2.imread(IMG1_PATH)
    img2 = cv2.imread(IMG2_PATH)
    if img1 is None or img2 is None:
        raise RuntimeError("Could not read images. Check IMG1_PATH / IMG2_PATH.")

    win1 = "IMG1 (click here when prompted)"
    win2 = "IMG2 (click here when prompted)"

    state = {"expect": 1}  # 1 => click img1, 2 => click img2
    last_msg = {"text": ""}

    def on_mouse_img1(event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        if state["expect"] != 1:
            last_msg["text"] = "Wrong window: click IMG2 now"
            return
        pts1.append((x, y))
        state["expect"] = 2
        last_msg["text"] = f"Picked IMG1 ({x},{y}). Now click corresponding point in IMG2."

    def on_mouse_img2(event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        if state["expect"] != 2:
            last_msg["text"] = "Wrong window: click IMG1 now"
            return
        pts2.append((x, y))
        state["expect"] = 1
        last_msg["text"] = f"Picked IMG2 ({x},{y}). Now click next point in IMG1."

    cv2.namedWindow(win1, cv2.WINDOW_NORMAL)
    cv2.namedWindow(win2, cv2.WINDOW_NORMAL)

    cv2.setMouseCallback(win1, on_mouse_img1)
    cv2.setMouseCallback(win2, on_mouse_img2)

    # IMPORTANT on macOS: show once + waitKey(1) to get event loop going
    cv2.imshow(win1, img1)
    cv2.imshow(win2, img2)
    cv2.waitKey(1)

    while True:
        v1 = draw_points(img1, pts1, (0, 0, 255))
        v2 = draw_points(img2, pts2, (0, 0, 255))

        cv2.putText(v1, f"Pairs: {min(len(pts1),len(pts2))}/{N_PAIRS} | u=undo | q=save+quit | ESC=cancel",
                    (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(v2, f"Pairs: {min(len(pts1),len(pts2))}/{N_PAIRS} | u=undo | q=save+quit | ESC=cancel",
                    (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 2, cv2.LINE_AA)

        if state["expect"] == 1:
            cv2.putText(v1, "NEXT: CLICK IN IMG1", (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0,255,0), 2, cv2.LINE_AA)
            cv2.putText(v2, "WAIT (do not click)", (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0,0,255), 2, cv2.LINE_AA)
        else:
            cv2.putText(v2, "NEXT: CLICK IN IMG2", (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0,255,0), 2, cv2.LINE_AA)
            cv2.putText(v1, "WAIT (do not click)", (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0,0,255), 2, cv2.LINE_AA)

        if last_msg["text"]:
            cv2.putText(v1, last_msg["text"], (20, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(v2, last_msg["text"], (20, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2, cv2.LINE_AA)

        cv2.imshow(win1, v1)
        cv2.imshow(win2, v2)

        key = cv2.waitKey(20) & 0xFF

        if key == ord('u'):
            # undo last action safely
            if state["expect"] == 2 and len(pts1) == len(pts2) + 1:
                pts1.pop()
                state["expect"] = 1
                last_msg["text"] = "Undo: removed last IMG1 point."
            elif len(pts1) == len(pts2) and len(pts1) > 0:
                pts1.pop()
                pts2.pop()
                state["expect"] = 1
                last_msg["text"] = "Undo: removed last pair."

        if key == ord('q'):
            break

        if key == 27:
            print("Cancelled.")
            cv2.destroyAllWindows()
            return

        if len(pts1) >= N_PAIRS and len(pts2) >= N_PAIRS and len(pts1) == len(pts2):
            break

    cv2.destroyAllWindows()

    pts1_arr = np.array(pts1, dtype=np.float32)
    pts2_arr = np.array(pts2, dtype=np.float32)

    if len(pts1_arr) != len(pts2_arr) or len(pts1_arr) < 8:
        raise RuntimeError("Need at least 8 matched pairs (and counts must match).")

    np.savez(OUT_NPZ, pts1=pts1_arr, pts2=pts2_arr, img1_path=IMG1_PATH, img2_path=IMG2_PATH)
    print("Saved:", OUT_NPZ, "| pairs:", len(pts1_arr))

if __name__ == "__main__":
    main()