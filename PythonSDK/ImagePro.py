import base64
import io
import os
from PIL import Image, ImageColor


class ImageProCls:
    base64FilePath=None

    @staticmethod
    def humanbody_blending_with_image(input_image, gray_image, bg_image):
        """

        :param input_image: the PIL.Image instance, the source humanbody image
        :param gray_image: the PIL.Image instance, it is created from api base64 result, a gray image
        :param bg_image: the PIL.Image instance, the background image you want to replace
        :return: the PIL.Image instance is blending with humanbody

        notes: you should close the return object after you leave
        """
        input_width, input_height = input_image.size
        bg_width, bg_height = bg_image.size

        input_aspect_ratio = input_width / float(input_height)
        bg_aspect_ratio = bg_width / float(bg_height)

        if bg_aspect_ratio > input_aspect_ratio:
            target_width, target_height = int(bg_height * input_aspect_ratio), bg_height
        else:
            target_width, target_height = bg_width, int(bg_width / input_aspect_ratio)

        crop_image = bg_image.crop((0, 0, 0+target_width, 0+target_height))
        new_image = crop_image.resize((input_width, input_height))
        crop_image.close()

        for x in range(0, input_width):
            for y in range(0, input_height):
                coord = (x, y)
                gray_pixel_value = gray_image.getpixel(coord)
                input_rgb_color = input_image.getpixel(coord)
                bg_rgb_color = new_image.getpixel(coord)

                confidence = gray_pixel_value / 255.0
                alpha = confidence

                R = input_rgb_color[0] * alpha + bg_rgb_color[0] * (1 - alpha)
                G = input_rgb_color[1] * alpha + bg_rgb_color[1] * (1 - alpha)
                B = input_rgb_color[2] * alpha + bg_rgb_color[2] * (1 - alpha)

                R = max(0, min(int(R), 255))
                G = max(0, min(int(G), 255))
                B = max(0, min(int(B), 255))

                new_image.putpixel(coord, (R, G, B))

        return new_image

    @staticmethod
    def humanbody_blending_with_color(input_image, gray_image, bg_color):
        """
        :param input_image: the PIL.Image instance
        :param gray_image: the PIL.Image instance, it is created from api base64 result, it is a gray image
        :param bg_color: a color string value, such as '#FFFFFF'
        :return: PIL.Image instance

        notes: you should close the return object after you leave
        """
        input_width, input_height = input_image.size
        bg_rgb_color = ImageColor.getrgb(bg_color)

        new_image = Image.new("RGB", input_image.size, bg_color)

        for x in range(0, input_width):
            for y in range(0, input_height):
                coord = (x, y)
                gray_pixel_value = gray_image.getpixel(coord)
                input_rgb_color = input_image.getpixel(coord)

                confidence = gray_pixel_value / 255.0
                alpha = confidence

                R = input_rgb_color[0] * alpha + bg_rgb_color[0] * (1 - alpha)
                G = input_rgb_color[1] * alpha + bg_rgb_color[1] * (1 - alpha)
                B = input_rgb_color[2] * alpha + bg_rgb_color[2] * (1 - alpha)

                R = max(0, min(int(R), 255))
                G = max(0, min(int(G), 255))
                B = max(0, min(int(B), 255))

                new_image.putpixel(coord, (R, G, B))

        return new_image

    @staticmethod
    def getSegmentImg(filePath):
        input_file = ''
        with open(filePath, 'r') as f:
            input_file = f.read()
        input_file = base64.b64decode(input_file)

        gray_image = Image.open(io.BytesIO(input_file))
        input_image = Image.open('./imgResource/segment.jpg', 'r')

        new_image = ImageProCls.humanbody_blending_with_color(input_image, gray_image, '#FFFFFF')
        new_image.save('./imgResource/resultImg.jpg')
        print('-' * 60)
        print('结果已经生成，生成文件名：resultImg.jpg，请在imgResource/目录下查看')
        if os.path.exists(filePath):
            os.remove(filePath)
            f.close()
        new_image.close()
        input_image.close()
        gray_image.close()

    @staticmethod
    def getMergeImg(base64Str):
        imgdata = base64.b64decode(base64Str)
        file = open('./imgResource/MergeResultImg.jpg', 'wb')
        file.write(imgdata)
        file.close()
        print('结果已经生成，生成文件名：MergeResultImg.jpg，请在imgResource/目录下查看')




