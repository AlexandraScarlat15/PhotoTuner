import argparse
from phototuner.utils import load_image, save_image
from phototuner.processing import enhance_image

def main():
    parser = argparse.ArgumentParser(description="AI Image Enhancer")
    parser.add_argument('--input', required=True, help="Path to input image")
    parser.add_argument('--output', default='output.jpg', help="Path to save enhanced image")
    parser.add_argument('--mode', default='standard', help="Enhancement mode: standard, natural, vivid, pro")
    args = parser.parse_args()

    image = load_image(args.input)
    print(f"[INFO] Enhancing image using mode: {args.mode}")
    enhanced = enhance_image(image, mode=args.mode)
    save_image(enhanced, args.output)
    print(f"[INFO] Enhanced image saved to {args.output}")

if __name__ == "__main__":
    main()
