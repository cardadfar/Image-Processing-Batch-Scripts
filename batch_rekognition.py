import boto3
import os
import json
import requests
from requests.auth import HTTPBasicAuth

#Before running the code, enter in the following commands into terminal:
    #export AWS_DEFAULT_REGION='YOUR_REGION'
    #export AWS_DEFAULT_PROFILE='YOUR_PROFILE'

FILE_TYPES = ['png', 'jpg', 'jpeg', 'gif']

#set with the bucket to upload files to
bucket='BUCKET_NAME'

def merge(x, y):
    z = x.copy() 
    z.update(y)
    return z

def write_data(fileName, tag_output, bucket):
    if __name__ == "__main__":
        client=boto3.client('rekognition')

        face_response = client.detect_faces(Image={'S3Object':{'Bucket':bucket,'Name':fileName}})
        text_response = client.detect_text(Image={'S3Object':{'Bucket':bucket,'Name':fileName}})
        labels_response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':fileName}},MinConfidence=15)
        
        response_temp = merge(face_response, text_response)
        response = merge(response_temp, labels_response)

        for extension in FILE_TYPES:
                if extension in fileName:
                    firstName = fileName.replace(extension,"")[:-1]

        with open(os.path.join(tag_output,firstName) + '.json', 'w') as outfile:
            json.dump(response, outfile, sort_keys=True, indent=4, separators=(',', ': '))

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

            s3=boto3.client('s3')
            first_name = image_path.replace(tag_input,"")[1:]

            with open(image_path, 'rb') as data:
                s3.upload_fileobj(data, bucket, first_name)

            write_data(first_name,tag_output,bucket)

            s3.delete_object(Bucket=bucket, Key=first_name)
main()