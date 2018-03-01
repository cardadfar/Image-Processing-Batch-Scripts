import requests
import os
import json
import base64

FILE_TYPES = ['png', 'jpg', 'jpeg', 'gif']

#encodes image to base64
def encode_image(img):
  with open(img) as image:
      image_content = image.read()
  return base64.b64encode(image_content)

#writes image adress to template.json, sends a request, and prints request to json
def write_data(tag_input, tag_output, image_path, file_name):
    template_loc = os.path.join(tag_input, 'template.json')
    image_base64 = encode_image(image_path)
    with open(os.path.join(tag_input,'template.json'), 'r+') as f:
        data = json.load(f)
        data['requests'][0]['image']['content'] = image_base64
        f.seek(0)       
        json.dump(data, f, indent=4)
        f.truncate()
    data = open(os.path.join(tag_input,'template.json'), 'rb').read()
    #Insert key below
    response = requests.post(url='https://vision.googleapis.com/v1/images:annotate?key=ENTER_KEY_HERE', \
		data=data, headers={'Content Type': 'application/json'}).json()
    

    with open(os.path.join(tag_output,file_name+".json"), 'wb') as results_file:
                               results_file.write(
                                   json.dumps(
                                       response, ensure_ascii=False, indent=4).encode('utf-8'))

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(
        description='Tags images in a folder')

    parser.add_argument(
        'input',
        metavar='<input>',
        type=str,
        nargs=1,
        help='The input - a folder containing images')

    parser.add_argument(
        'output',
        metavar='<output>',
        type=str,
        nargs=1,
        help='The output - a folder to output the results')

    args = parser.parse_args()

    return args


def main():

    args = parse_arguments()

    tag_input = args.input[0]
    tag_output = args.output[0]

    print('Tagging images started')

    results = {}
    if os.path.isdir(tag_input):
        images = [filename for filename in os.listdir(tag_input)
                  if os.path.isfile(os.path.join(tag_input, filename)) and
                  filename.split('.')[-1].lower() in FILE_TYPES]

        images_count = len(images)

        for iterator, image_file in enumerate(images):
            image_path = os.path.join(tag_input, image_file)
            print('[%s / %s] %s uploading' %
                  (iterator + 1, images_count, image_path))

            first_name = image_path.replace(tag_input,"")[1:]

            for extension in FILE_TYPES:
                if extension in first_name:
                    file_name = first_name.replace(extension,"")[:-1]
            
            write_data(tag_input, tag_output, image_path, file_name)

main()
