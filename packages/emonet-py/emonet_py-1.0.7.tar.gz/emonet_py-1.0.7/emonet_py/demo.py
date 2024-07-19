import os
from emonet_py.emonet import EmoNet, EmoNetPreProcess
from emonet_py.emonet_arousal import EmoNetArousal
from emonet_py.emonet_valence import EmoNetValence

if __name__ == '__main__':
    emonet = EmoNet(b_eval=True)
    emonet_pp = EmoNetPreProcess()
    img_big = os.path.join('..', 'data', 'demo_big.jpg')
    img_loaded = emonet_pp(img_big)
    pred = emonet.emonet(img_loaded.unsqueeze(0))
    emonet.prettyprint(pred, b_pc=True)

    emo_aro = EmoNetArousal()
    print(f"Arousal: {emo_aro(img_loaded.unsqueeze(0))}")

    emo_val = EmoNetValence()
    print(f"Valence: {emo_val(img_loaded.unsqueeze(0))}")
