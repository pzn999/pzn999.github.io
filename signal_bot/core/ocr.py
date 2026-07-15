import os
import time
import easyocr

print("Initializing OCR...")

reader = easyocr.Reader(
    ['en'],
    gpu=False
)


def read_image(path):

    print("OCR PATH:", path)

    # attende che il file esista
    for _ in range(50):

        if os.path.exists(path):
            break

        time.sleep(0.1)

    # attende che Windows abbia finito di scriverlo
    last_size = -1

    for _ in range(20):

        try:
            size = os.path.getsize(path)

            if size == last_size and size > 0:
                break

            last_size = size

        except:
            pass

        time.sleep(0.1)

    # piccolo margine di sicurezza
    time.sleep(0.2)

    text = reader.readtext(path, detail=0)

    result = "\n".join(text)

    print("===== OCR TEXT =====")
    print(repr(result))
    print("====================")

    return result