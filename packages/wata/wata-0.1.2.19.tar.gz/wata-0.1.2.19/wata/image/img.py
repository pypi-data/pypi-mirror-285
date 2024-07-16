from wata.image.utils import utils


class ImageProcess:
    @staticmethod
    def show_img(path):
        utils.show_img(path)

    @staticmethod
    def img2video(img_dir, save_path, fps=30):
        utils.images_to_video(img_dir, save_path, fps)

    @staticmethod
    def video2img(path, save_path):
        utils.video_to_images(path, save_path)
