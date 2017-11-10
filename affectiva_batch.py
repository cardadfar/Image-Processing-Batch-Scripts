import os
import json
import requests
import time
from requests.auth import HTTPBasicAuth


auth=('USERNAME','PASSWORD')
headers={"Accept":"application/json"}

uri = 'https://index.affectiva.com'
job_name = 'https://index.affectiva.com/jobs'

FILE_TYPES = ['png', 'jpg', 'jpeg', 'gif']

def upload_image(image_path):

    with open(image_path, 'rb') as image:
        files = {'entry_job[name]': (None, 'multiface'),
                 'entry_job[input]': (os.path.basename(image_path), image)}

        content_response = requests.post(job_name, auth=auth, headers=headers, files=files).json()
        content_id = content_response["self"]

    return content_id

def get_results(job_url, tag_output, image):
        #Returns the results for a processed image or video.
        job_json = requests.get(job_url, auth=auth, headers=headers).json()
        ready = job_json['status']
        while ready != 'done':
            time.sleep(10)
            job_json = requests.get(job_url, auth=auth, headers=headers).json()
            ready = job_json['status']
            if ready == 'done':
                types = job_json['result']['representations']
                for representation in types:
                    if representation["content_type"] == 'application/vnd.affectiva.session.v0+json':
                        media_url = representation["media"]
                        metrics = requests.get(media_url, auth=auth, headers=headers).json()
                        with open(os.path.join(tag_output, 'result_%s.json' % image), 'wb') as results_file:
                            results_file.write(
                                json.dumps(
                                    metrics, ensure_ascii=False, indent=4).encode('utf-8'))

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
            
            print(iterator)
            first_name = image_path.replace(tag_input,"")[1:]

            for extension in FILE_TYPES:
                if extension in filename:
                    file_name = first_name.replace(extension,"")[:-1]

            content_id = upload_image(image_path)
            print(content_id)

            get_results(content_id, tag_output, file_name) 

main()
