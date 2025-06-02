import cv2
import time
from skimage.metrics import structural_similarity
from datetime import datetime
import winsound  # Using winsound for alert sound

def spot_diff(frame1, frame2):  # Accept frame1 and frame2 as arguments
    # Check if frames are None (i.e., not successfully captured)
    if frame1 is None or frame2 is None:
        print("Error: One or both frames are None. Skipping processing.")
        return None  # Return None or handle the error gracefully

    # Check if the frames are already in grayscale (1 channel)
    if len(frame1.shape) == 2:  # Grayscale image (1 channel)
        g1 = frame1
    else:  # Convert to grayscale if it's a color image
        g1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)

    if len(frame2.shape) == 2:  # Grayscale image (1 channel)
        g2 = frame2
    else:  # Convert to grayscale if it's a color image
        g2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    g1 = cv2.GaussianBlur(g1, (5, 5), 0)
    g2 = cv2.GaussianBlur(g2, (5, 5), 0)

    # Compute structural similarity
    (score, diff) = structural_similarity(g1, g2, full=True)
    print("Image similarity:", score)

    diff = (diff * 255).astype("uint8")
    thresh = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY_INV)[1]

    # Detect contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [c for c in contours if cv2.contourArea(c) > 100]

    if contours:
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Beep sound when motion is detected
        winsound.Beep(1000, 500)

        # Save detected image
        filename = "stolen/" + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + ".jpg"
        cv2.imwrite(filename, frame1)
        print(f"Motion detected! Image saved: {filename}")
    else:
        print("No significant movement detected.")

    # Show results
    cv2.imshow("Diff", thresh)
    cv2.imshow("Detected Changes", frame1)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
